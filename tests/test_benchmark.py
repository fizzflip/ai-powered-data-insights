"""
Tests for IncrementalScalingHarness module (src/benchmark.py).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.benchmark import IncrementalScalingHarness
from src.clustering import compute_adaptive_k_range
from src.mock_data import MOCK_ANIME_DATA


def test_adaptive_k_range_formula():
    """Verify sub-linear scaling formula for various dataset sizes."""
    min_k, max_k, target_k = compute_adaptive_k_range(50)
    assert 2 <= min_k <= max_k <= 10

    min_k_large, max_k_large, target_k_large = compute_adaptive_k_range(5000)
    assert min_k_large >= min_k
    assert max_k_large >= max_k


def test_benchmark_harness_with_mock_data(tmp_path: Path):
    """Verify benchmark harness execution on temporary mock data file."""
    mock_file = tmp_path / "mock_catalog.json"
    with open(mock_file, "w", encoding="utf-8") as f:
        json.dump(MOCK_ANIME_DATA[:30], f)

    harness = IncrementalScalingHarness(
        raw_json_path=str(mock_file),
        output_dir=str(tmp_path / "reports"),
    )

    records = harness.load_all_cached_records()
    assert len(records) == 30
