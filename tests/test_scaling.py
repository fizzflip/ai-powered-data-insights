"""
Unit and integration tests for adaptive cluster scaling and multi-step incremental database verification.
"""

import tempfile
import numpy as np
import pandas as pd
import pytest

from src.clustering import AnimeClusterer, compute_adaptive_k_range
from src.database import AnimeCatalogDB
from src.data_fetcher import MOCK_ANIME_DATA
from src.pipeline import InsightsPipeline, PipelineConfig
from src.preprocessor import DataPreprocessor


def test_compute_adaptive_k_range_monotonicity():
    """Verify that target k and candidate bounds increase monotonically with N."""
    sample_sizes = [20, 50, 100, 250, 600, 1000, 2000, 5000]
    prev_target = 0
    prev_max = 0

    for n in sample_sizes:
        min_k, max_k, target = compute_adaptive_k_range(n)
        assert min_k <= target <= max_k, f"Target {target} outside range [{min_k}, {max_k}] for N={n}"
        assert target >= prev_target, f"Target decreased from {prev_target} to {target} at N={n}"
        assert max_k >= prev_max, f"Max k decreased from {prev_max} to {max_k} at N={n}"
        prev_target = target
        prev_max = max_k


def test_compute_adaptive_k_range_bounds():
    """Verify boundary invariants across edge cases."""
    # Tiny sample
    min_k, max_k, target = compute_adaptive_k_range(3)
    assert min_k >= 2
    assert max_k >= 2

    # Medium sample
    min_k, max_k, target = compute_adaptive_k_range(150)
    assert 2 <= min_k <= target <= max_k <= 12
    assert max_k <= 150 - 1

    # Large sample
    min_k, max_k, target = compute_adaptive_k_range(2000)
    assert min_k >= 4
    assert max_k <= 12


def test_variable_k_archetype_profiling():
    """Verify archetype profiling and 100% collision-free label uniqueness for arbitrary k."""
    clusterer = AnimeClusterer()
    prep = DataPreprocessor()
    df_mock = pd.DataFrame(MOCK_ANIME_DATA)
    preprocessed = prep.fit_transform(df_mock)

    for test_k in [2, 3, 5, 7]:
        res = clusterer.run_clustering(preprocessed, k=test_k)
        assert res.k_optimal == test_k
        assert len(res.archetype_labels) == test_k
        # Guarantee 100% label uniqueness (zero collisions)
        unique_labels = set(res.archetype_labels.values())
        assert len(unique_labels) == test_k, (
            f"Archetype collision detected for k={test_k}: {res.archetype_labels}"
        )
        assert not res.cluster_profiles.empty
        assert len(res.cluster_profiles) == test_k


def test_adaptive_k_pipeline_execution():
    """Verify that InsightsPipeline with adaptive_k=True computes range and clusters smoothly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config = PipelineConfig(
            num_samples=55,
            k=None,
            adaptive_k=True,
            offline_mode=True,
            generate_plots=False,
            output_dir=tmp_dir,
            figures_dir=f"{tmp_dir}/figures",
            db_path=f"{tmp_dir}/test.db",
        )
        pipeline = InsightsPipeline(config)
        results = pipeline.run()

        assert results["k_optimal"] >= 2
        assert len(results["archetype_labels"]) == results["k_optimal"]
        assert len(set(results["archetype_labels"].values())) == results["k_optimal"]


def test_incremental_database_growth_and_scaling():
    """
    Verify 3-step incremental SQLite database population and monotonic cluster scaling.
    """
    clusterer = AnimeClusterer()
    prep = DataPreprocessor()

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/incremental_test.db"
        db = AnimeCatalogDB(db_path=db_path)

        # Create synthetic corpus
        synthetic_records = []
        for i in range(600):
            mock_copy = dict(MOCK_ANIME_DATA[i % len(MOCK_ANIME_DATA)])
            mock_copy["id"] = 10000 + i
            mock_copy["source_api"] = "test"
            synthetic_records.append(mock_copy)

        step_counts = [50, 250, 600]
        optimal_ks = []
        ingested = 0

        for target_count in step_counts:
            # Incremental slice
            slice_to_add = synthetic_records[ingested:target_count]
            db.upsert_records(slice_to_add, source_api="test")
            ingested = db.count_records()
            assert ingested == target_count

            current_records = db.get_all_records(limit=target_count)
            df_step = pd.DataFrame(current_records)
            preprocessed = prep.fit_transform(df_step)

            res = clusterer.run_clustering(preprocessed, k=None, adaptive_k=True)
            optimal_ks.append(res.k_optimal)
            # Verify 100% unique archetypes
            assert len(set(res.archetype_labels.values())) == res.k_optimal

        # Monotonicity check: k should be non-decreasing across growth steps
        for i in range(len(optimal_ks) - 1):
            assert optimal_ks[i] <= optimal_ks[i + 1], (
                f"k decreased across growth steps: {optimal_ks}"
            )
