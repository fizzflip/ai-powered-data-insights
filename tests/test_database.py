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
