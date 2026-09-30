"""
Unit tests for the Offline Indexer and Relational Deduplication Engine.
"""

import json
import os
import tempfile
import pytest

from src.database import AnimeCatalogDB
from src.offline_indexer import OfflineIndexer


def test_offline_indexer_mini_ingestion():
    """Verify OfflineIndexer extracts mappings, relations, and unrepresented records."""
    sample_records = [
        {
            "$schema": "https://test.schema.json",
            "license": "ODbL",
        },
        {
            "sources": [
                "https://anilist.co/anime/16498",
                "https://myanimelist.net/anime/16498",
                "https://kitsu.app/anime/7442",
            ],
            "title": "Shingeki no Kyojin",
            "type": "TV",
            "episodes": 25,
            "status": "FINISHED",
            "animeSeason": {"season": "SPRING", "year": 2013},
            "duration": {"value": 24, "unit": "MINUTES"},
            "score": {"arithmeticMean": 8.54},
            "synonyms": ["Attack on Titan"],
            "studios": ["wit studio"],
            "relatedAnime": [
                "https://anilist.co/anime/20958",
                "https://myanimelist.net/anime/25777",
            ],
            "tags": ["action", "drama", "fantasy", "military"],
        },
        {
            "sources": [
                "https://anilist.co/anime/20958",
                "https://myanimelist.net/anime/25777",
                "https://kitsu.app/anime/8671",
            ],
            "title": "Shingeki no Kyojin Season 2",
            "type": "TV",
            "episodes": 12,
            "status": "FINISHED",
            "animeSeason": {"season": "SPRING", "year": 2017},
            "duration": {"value": 24, "unit": "MINUTES"},
            "score": {"arithmeticMean": 8.42},
            "synonyms": ["Attack on Titan Season 2"],
            "studios": ["wit studio"],
            "relatedAnime": [
                "https://anilist.co/anime/16498",
                "https://myanimelist.net/anime/16498",
            ],
            "tags": ["action", "drama", "fantasy", "post-apocalyptic"],
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        jsonl_path = os.path.join(tmpdir, "mini_offline.jsonl")
        db_path = os.path.join(tmpdir, "test_catalog.db")

        with open(jsonl_path, "w", encoding="utf-8") as f:
            for item in sample_records:
                f.write(json.dumps(item) + "\n")

        db = AnimeCatalogDB(db_path=db_path)
        indexer = OfflineIndexer(db=db)
        stats = indexer.index_file(jsonl_path=jsonl_path, insert_unrepresented=True)

        assert stats["total_items_processed"] == 2
        assert stats["final_catalog_records"] == 2
        assert db.count_records() == 2

        # Verify external mappings
        mappings_1 = db.get_external_mappings("anilist:16498")
        sites_1 = {m["external_site"] for m in mappings_1}
        assert "anilist" in sites_1
        assert "myanimelist" in sites_1
        assert "kitsu" in sites_1

        # Verify relations
        assert db.has_relation("anilist:16498", "anilist:20958") is True
        assert db.has_relation("anilist:20958", "anilist:16498") is True
        related_ids = db.get_related_ids("anilist:16498")
        assert "anilist:20958" in related_ids


def test_relation_boundary_guard_prevents_false_merges():
    """Verify Tier 2 Relation Boundary Guard blocks merging related installments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_guard.db")
        db = AnimeCatalogDB(db_path=db_path)

        # 1. Insert FLCL (Part 1) (2018, 6 eps)
        rec_flcl_prog = {
            "id": 21745,
            "source_api": "anilist",
            "title": {"romaji": "FLCL (Part 1)", "english": "FLCL (Part 1)"},
            "seasonYear": 2018,
            "episodes": 6,
            "averageScore": 68,
            "popularity": 45000,
        }
        # 2. Insert FLCL (Part 2) (2018, 6 eps) - same year, same episode count, normalizes to same clean title
        rec_flcl_alt = {
            "id": 21746,
            "source_api": "kitsu",
            "title": {"romaji": "FLCL (Part 2)", "english": "FLCL (Part 2)"},
            "seasonYear": 2018,
            "episodes": 6,
            "averageScore": 66,
            "popularity": 38000,
        }

        db.upsert_records([rec_flcl_prog], source_api="anilist")
        db.upsert_records([rec_flcl_alt], source_api="kitsu")
        assert db.count_records() == 2

        # Register relation between Progressive and Alternative
        db.insert_relations([
            ("anilist:21745", "kitsu:21746", "sequel", "manami"),
            ("kitsu:21746", "anilist:21745", "prequel", "manami"),
        ])
        assert db.has_relation("anilist:21745", "kitsu:21746") is True

        # Run thorough deduplication
        stats = db.thorough_deduplicate()

        # Both records must be preserved because of the relation guard!
        assert stats["guarded_relational_skips"] >= 1
        assert db.count_records() == 2
        remaining_ids = {r["id"] for r in db.get_all_records()}
        assert 21745 in remaining_ids
        assert 21746 in remaining_ids


def test_tier1_deterministic_id_deduplication():
    """Verify Tier 1 DSU deduplication merges cross-source entries sharing external IDs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_crosswalk.db")
        db = AnimeCatalogDB(db_path=db_path)

        rec_anilist = {
            "id": 101922,
            "source_api": "anilist",
            "title": {"romaji": "Kimetsu no Yaiba", "english": "Demon Slayer"},
            "seasonYear": 2019,
            "episodes": 26,
            "averageScore": 85,
            "popularity": 500000,
        }
        rec_kitsu = {
            "id": 41370,
            "source_api": "kitsu",
            "title": {"romaji": "Blade of Demon Destruction", "english": "Kimetsu"},
            "seasonYear": 2019,
            "episodes": 26,
            "averageScore": 84,
            "popularity": 250000,
        }

        db.upsert_records([rec_anilist], source_api="anilist")
        db.upsert_records([rec_kitsu], source_api="kitsu")
        assert db.count_records() == 2

        # Cross-reference them via shared MyAnimeList ID 38000
        db.insert_external_mappings([
            ("anilist:101922", "myanimelist", "38000"),
            ("kitsu:41370", "myanimelist", "38000"),
        ])

        # Deduplicate
        stats = db.thorough_deduplicate()
        assert stats["deterministic_id_merged"] == 1
        assert stats["total_pruned"] == 1
        assert db.count_records() == 1

        # Check winner is the anilist record (higher priority & popularity)
        remaining = db.get_all_records()
        assert remaining[0]["id"] == 101922
