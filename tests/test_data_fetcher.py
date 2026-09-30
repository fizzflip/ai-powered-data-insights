"""
Unit tests for AniList data fetcher and caching module.
"""

import json
import os
import tempfile
import pytest
from src.data_fetcher import AniListFetcher, MOCK_ANIME_DATA


def test_mock_anime_data_presence():
    """Verify built-in mock data has at least 30 entries and required fields."""
    assert len(MOCK_ANIME_DATA) >= 30
    required_keys = [
        "id", "title", "seasonYear", "episodes", "duration",
        "genres", "tags", "source", "averageScore", "popularity", "favourites"
    ]
    for item in MOCK_ANIME_DATA:
        for k in required_keys:
            assert k in item, f"Missing key {k} in mock item {item.get('id')}"


def test_fetcher_offline_mode():
    """Verify offline mode returns mock data without internet."""
    fetcher = AniListFetcher(cache_path="non_existent_cache.json")
    data = fetcher.fetch_anime_data(limit=15, offline=True)
    assert len(data) == 15
    assert data[0]["id"] == MOCK_ANIME_DATA[0]["id"]


def test_fetcher_caching():
    """Verify save_cache and load_cache roundtrip."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "test_cache.json")
        fetcher = AniListFetcher(cache_path=cache_file)

        sample = MOCK_ANIME_DATA[:5]
        fetcher.save_cache(sample)
        assert os.path.exists(cache_file)

        loaded = fetcher.load_cache()
        assert loaded is not None
        assert len(loaded) == 5
        assert loaded[0]["id"] == sample[0]["id"]
