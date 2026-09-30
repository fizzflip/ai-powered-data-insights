"""
Unit tests for the SQLite incremental database module.
"""

import os
import tempfile
import pytest
from src.database import AnimeCatalogDB
from src.data_fetcher import MOCK_ANIME_DATA


def test_sqlite_db_initialization_and_upsert():
    """Verify AnimeCatalogDB initializes tables and upserts records."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = os.path.join(tmpdir, "test_anime.db")
        db = AnimeCatalogDB(db_path=db_file)

        assert db.count_records() == 0

        # Upsert mock data
        inserted, updated = db.upsert_records(MOCK_ANIME_DATA[:10], source_api="test")
        assert inserted == 10
        assert updated == 0
        assert db.count_records() == 10

        # Upsert again - should update, not insert duplicate
        inserted2, updated2 = db.upsert_records(MOCK_ANIME_DATA[:5], source_api="test")
        assert inserted2 == 0
        assert updated2 == 5
        assert db.count_records() == 10


def test_sqlite_db_json_export_import():
    """Verify bidirectional SQLite <-> JSON export and import."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = os.path.join(tmpdir, "test_anime.db")
        json_file = os.path.join(tmpdir, "test_export.json")
        db = AnimeCatalogDB(db_path=db_file)

        db.upsert_records(MOCK_ANIME_DATA[:8], source_api="test")
        exported_count = db.export_to_json(json_file)
        assert exported_count == 8
        assert os.path.exists(json_file)

        # Import into new DB
        db_file2 = os.path.join(tmpdir, "test_anime2.db")
        db2 = AnimeCatalogDB(db_path=db_file2)
        imported_count = db2.import_from_json(json_file, source_api="test")
        assert imported_count == 8
        assert db2.count_records() == 8


def test_sqlite_db_thorough_deduplicate():
    """Verify thorough deduplication merges legacy IDs and cross-source duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = os.path.join(tmpdir, "test_dedup.db")
        db = AnimeCatalogDB(db_path=db_file)

        # 1. Insert anilist record
        rec_anilist = {
            "id": 101922,
            "title": {"romaji": "Kimetsu no Yaiba", "english": "Demon Slayer: Kimetsu no Yaiba"},
            "seasonYear": 2019,
            "episodes": 26,
            "popularity": 500000,
            "averageScore": 85,
            "source_api": "anilist",
        }
        # 2. Insert duplicate legacy 'api' record with same external ID
        rec_api = {
            "id": 101922,
            "title": {"romaji": "Kimetsu no Yaiba", "english": "Demon Slayer"},
            "seasonYear": 2019,
            "episodes": 26,
            "popularity": 450000,
            "averageScore": 84,
            "source_api": "api",
        }
        # 3. Insert kitsu record with same title and year
        rec_kitsu = {
            "id": 41370,
            "title": {"romaji": "Kimetsu no Yaiba", "english": "Demon Slayer: Kimetsu no Yaiba"},
            "seasonYear": 2019,
            "episodes": 26,
            "popularity": 350000,
            "averageScore": 83,
            "source_api": "kitsu",
        }
        # 4. Insert an unrelated anime
        rec_distinct = {
            "id": 16498,
            "title": {"romaji": "Shingeki no Kyojin", "english": "Attack on Titan"},
            "seasonYear": 2013,
            "episodes": 25,
            "popularity": 600000,
            "averageScore": 88,
            "source_api": "anilist",
        }

        db.upsert_records([rec_anilist], source_api="anilist")
        db.upsert_records([rec_distinct], source_api="anilist")
        db.upsert_records([rec_kitsu], source_api="kitsu")

        # Manually insert legacy 'api:' record to test ID consolidation
        with db._get_connection() as conn:
            conn.execute(
                "INSERT INTO anime_records (id, source_api, external_id, title_romaji, title_english, season_year, episodes, raw_json) "
                "VALUES ('api:101922', 'api', 101922, 'Kimetsu no Yaiba', 'Demon Slayer', 2019, 26, '{}')"
            )
            conn.commit()

        assert db.count_records() == 4

        # Run thorough deduplication
        stats = db.thorough_deduplicate()

        # Should consolidate api:101922 into anilist:101922 and merge kitsu:41370
        assert stats["legacy_ids_consolidated"] == 1
        assert stats["cross_source_merged"] == 1
        assert stats["total_pruned"] == 2
        assert db.count_records() == 2

        # Remaining records should be the distinct Attack on Titan and canonical Demon Slayer
        records = db.get_all_records()
        record_ids = {r["id"] for r in records}
        assert 16498 in record_ids
        assert 101922 in record_ids

