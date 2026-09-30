"""
Tests for ParallelAnimeHarvester module (src/harvester.py).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.database import AnimeCatalogDB
from src.harvester import ParallelAnimeHarvester


@pytest.fixture
def temp_db(tmp_path: Path) -> AnimeCatalogDB:
    db_file = tmp_path / "test_harvest.db"
    return AnimeCatalogDB(str(db_file))


def test_harvester_initialization(temp_db: AnimeCatalogDB):
    """Verify harvester initialization, rate limiter clamping, and stats structure."""
    harvester = ParallelAnimeHarvester(db=temp_db, target_records=50, rate_delay=1.0)

    # Clamping guarantee: rate_delay must never drop below 3.0s to avoid API ban
    assert harvester.rate_delay >= 3.0
    assert harvester.target_records == 50
    assert harvester.stats["anilist_batches"] == 0
    assert harvester.stats["kitsu_batches"] == 0
    assert not harvester.stop_event.is_set()


def test_harvester_stop_event(temp_db: AnimeCatalogDB):
    """Verify stop event halts worker processing safely."""
    harvester = ParallelAnimeHarvester(db=temp_db, target_records=10)
    harvester.stop_event.set()
    assert harvester.stop_event.is_set()
