"""
Shared Pytest Fixtures for ai-powered-data-insights test suite.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest

from src.database import AnimeCatalogDB
from src.mock_data import MOCK_ANIME_DATA


@pytest.fixture
def sample_anime_records() -> List[Dict[str, Any]]:
    """Return a fresh copy of the curated 55-item mock dataset."""
    return [dict(item) for item in MOCK_ANIME_DATA]


@pytest.fixture
def temp_db(tmp_path: Path) -> AnimeCatalogDB:
    """Provide an isolated, temporary SQLite database instance."""
    db_file = tmp_path / "temp_anime_catalog.db"
    return AnimeCatalogDB(str(db_file))


@pytest.fixture
def populated_db(temp_db: AnimeCatalogDB, sample_anime_records: List[Dict[str, Any]]) -> AnimeCatalogDB:
    """Provide a temporary SQLite database pre-populated with mock anime records."""
    temp_db.upsert_records(sample_anime_records, source_api="anilist")
    return temp_db
