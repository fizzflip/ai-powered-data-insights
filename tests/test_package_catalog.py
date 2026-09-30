"""
Unit and integration tests for catalog pre-packaging pipeline (scripts/package_catalog.py).
"""

from __future__ import annotations

import gzip
import json
import sqlite3
from pathlib import Path

import pytest

from scripts.package_catalog import (
    REQUIRED_RECORD_KEYS,
    clean_title,
    generate_compact_json_gz,
    generate_compact_sqlite_db,
    map_sub_origin,
    normalize_score,
    package_catalog,
    parse_genres,
    parse_tags,
    validate_records,
)


def test_clean_title_selection():
    """Verify title selection precedence and length bounds."""
    assert clean_title("Attack on Titan", "Shingeki no Kyojin") == "Attack on Titan"
    assert clean_title(None, "Shingeki no Kyojin") == "Shingeki no Kyojin"
    assert clean_title("", "  Cowboy Bebop  ") == "Cowboy Bebop"
    assert clean_title(None, None) == "Unknown Title"

    long_title = "A" * 150
    cleaned = clean_title(long_title, None)
    assert len(cleaned) <= 120


def test_score_normalization():
    """Verify 0.0-100.0 boundary mapping and 1-10 multiplier heuristic."""
    assert normalize_score(None) is None
    assert normalize_score(85.45) == 85.5
    # 1.0 - 10.0 scale from Manami converted to 0.0 - 100.0
    assert normalize_score(7.84) == 78.4
    assert normalize_score(-5.0) is None
    assert normalize_score(105.0) == 100.0


def test_tag_and_genre_parsing():
    """Verify tag capping and genre deduplication."""
    tags_json = json.dumps([{"name": "Action"}, {"name": "Fantasy"}, "Magic", "Adventure", "Isekai", "Comedy", "Supernatural"])
    tags = parse_tags(tags_json, max_tags=6)
    assert len(tags) == 6
    assert tags[0] == "Action"
    assert tags[2] == "Magic"

    genres_str = "Action, Drama, Fantasy, Action"
    genres = parse_genres(genres_str)
    assert genres == ["Action", "Drama", "Fantasy"]


def test_sub_origin_mapping():
    """Verify mapping of country codes to 5-class sub_origin taxonomy."""
    assert map_sub_origin("JP", 1) == "JP"
    assert map_sub_origin("CN", 0) == "CN"
    assert map_sub_origin("TW", 0) == "CN"
    assert map_sub_origin("KR", 0) == "KR"
    assert map_sub_origin("US", 0) == "WESTERN"
    assert map_sub_origin("FR", 0) == "WESTERN"
    assert map_sub_origin("XYZ", 0) == "OTHER"
    assert map_sub_origin(None, 1) == "JP"
    assert map_sub_origin(None, 0) == "OTHER"


def test_record_validation_contract():
    """Verify 12-key contract enforcement."""
    valid_record = {
        "id": 1,
        "title": "Cowboy Bebop",
        "seasonYear": 1998,
        "averageScore": 89.0,
        "popularity": 350000,
        "favourites": 45000,
        "episodes": 26,
        "duration": 24,
        "genres": ["Action", "Sci-Fi"],
        "tags": ["space", "bounty hunter"],
        "origin_cohort": "jp",
        "sub_origin": "JP",
    }
    validate_records([valid_record])

    # Record missing a required key
    invalid_record = dict(valid_record)
    del invalid_record["origin_cohort"]
    with pytest.raises(ValueError):
        validate_records([invalid_record])


def test_packaging_pipeline_synthetic_execution(tmp_path: Path):
    """Verify end-to-end packaging with temporary SQLite catalog."""
    db_file = tmp_path / "test_catalog.db"
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE anime_records (
            id TEXT PRIMARY KEY,
            source_api TEXT,
            external_id INTEGER,
            title_romaji TEXT,
            title_english TEXT,
            season_year INTEGER,
            average_score REAL,
            popularity INTEGER,
            favourites INTEGER,
            episodes INTEGER,
            duration INTEGER,
            genres_json TEXT,
            tags_json TEXT,
            country_code TEXT,
            is_jp INTEGER
        );
    """)

    sample_rows = [
        (
            f"test:{i}",
            "test",
            i,
            f"Romaji {i}",
            f"English {i}",
            2020 + (i % 5),
            8.2 if i % 2 == 0 else 75.0,
            1000 * i,
            100 * i,
            12,
            24,
            json.dumps(["Action", "Adventure"]),
            json.dumps([{"name": "superpowers"}, {"name": "hero"}]),
            "JP" if i % 3 != 0 else "CN",
            1 if i % 3 != 0 else 0,
        )
        for i in range(1, 51)
    ]
    cur.executemany(
        """
        INSERT INTO anime_records (
            id, source_api, external_id, title_romaji, title_english,
            season_year, average_score, popularity, favourites,
            episodes, duration, genres_json, tags_json, country_code, is_jp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_rows,
    )
    conn.commit()
    conn.close()

    out_dir = tmp_path / "out"
    pub_dir = tmp_path / "pub"

    summary = package_catalog(
        source_path=str(db_file),
        output_dir=str(out_dir),
        publish_dir=str(pub_dir),
    )

    assert summary.total_records == 50
    assert summary.json_gz_bytes > 0
    assert summary.db_bytes > 0

    # Verify JSON.GZ contents
    json_gz_path = out_dir / "anime_catalog_compact.json.gz"
    assert json_gz_path.exists()
    with gzip.open(json_gz_path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 50
    assert set(data[0].keys()) == REQUIRED_RECORD_KEYS

    # Verify compact SQLite contents and indexes
    db_compact_path = out_dir / "anime_catalog_compact.db"
    assert db_compact_path.exists()
    compact_conn = sqlite3.connect(str(db_compact_path))
    compact_cur = compact_conn.cursor()

    compact_cur.execute("SELECT COUNT(*) FROM anime_records")
    assert compact_cur.fetchone()[0] == 50

    compact_cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = {row[0] for row in compact_cur.fetchall()}
    assert "idx_compact_pop" in indexes
    assert "idx_compact_score" in indexes
    assert "idx_compact_origin" in indexes

    # Test virtual column query
    compact_cur.execute("SELECT seasonYear, averageScore FROM anime_records LIMIT 1")
    row = compact_cur.fetchone()
    assert row[0] is not None
    assert row[1] is not None

    compact_conn.close()

    # Verify published mirrors
    assert (pub_dir / "anime_catalog_compact.json.gz").exists()
    assert (pub_dir / "anime_catalog_compact.db").exists()


def test_packaging_pipeline_jsonl_execution(tmp_path: Path):
    """Verify packaging pipeline ingesting from raw JSONL file."""
    jsonl_file = tmp_path / "test_catalog.jsonl"
    records_raw = [
        {"$schema": "https://example.com/schema.json"},
        {
            "sources": ["https://anilist.co/anime/101"],
            "title": "Fullmetal Alchemist",
            "type": "TV",
            "episodes": 64,
            "animeSeason": {"season": "SPRING", "year": 2009},
            "score": {"arithmeticMean": 9.1},
            "popularity": 500000,
            "favourites": 45000,
            "duration": {"value": 1440, "unit": "SECONDS"},
            "genres": ["Action", "Adventure", "Drama"],
            "tags": ["alchemy", "military", "brothers"],
            "studios": ["Bones"],
        },
        {
            "sources": ["https://myanimelist.net/anime/202"],
            "title": "Mo Dao Zu Shi",
            "type": "ONA",
            "episodes": 15,
            "animeSeason": {"season": "SUMMER", "year": 2018},
            "score": {"arithmeticMean": 8.4},
            "popularity": 80000,
            "favourites": 12000,
            "duration": {"value": 24, "unit": "MINUTES"},
            "genres": ["Action", "Supernatural"],
            "tags": ["chinese animation", "cultivation", "historical"],
            "studios": ["B.CMAY PICTURES"],
        },
    ]

    with open(jsonl_file, "w", encoding="utf-8") as f:
        for r in records_raw:
            f.write(json.dumps(r) + "\n")

    out_dir = tmp_path / "out_jsonl"
    pub_dir = tmp_path / "pub_jsonl"

    summary = package_catalog(
        source_path=str(jsonl_file),
        output_dir=str(out_dir),
        publish_dir=str(pub_dir),
    )

    assert summary.total_records == 2
    assert (out_dir / "anime_catalog_compact.json.gz").exists()
    assert (out_dir / "anime_catalog_compact.db").exists()

    with gzip.open(out_dir / "anime_catalog_compact.json.gz", "rt", encoding="utf-8") as f:
        loaded = json.load(f)

    assert len(loaded) == 2
    # Verify origin classification was applied
    assert loaded[0]["origin_cohort"] == "jp"
    assert loaded[0]["sub_origin"] == "JP"
    assert loaded[0]["duration"] == 24  # 1440 seconds -> 24 minutes

    assert loaded[1]["origin_cohort"] == "non-jp"
    assert loaded[1]["sub_origin"] == "CN"
