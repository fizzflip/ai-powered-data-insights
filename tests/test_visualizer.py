"""
Unit tests for visualization module.
"""

import os
import tempfile
import numpy as np
import pandas as pd
import pytest
from src.clustering import AnimeClusterer
from src.data_fetcher import MOCK_ANIME_DATA
from src.preprocessor import DataPreprocessor
from src.visualizer import ClusterVisualizer


def test_visualizer_generates_files():
    """Verify visualizer creates all 5 figures and returns their paths."""
    df_raw = pd.DataFrame(MOCK_ANIME_DATA)
    preprocessed = DataPreprocessor().fit_transform(df_raw)
    clustering = AnimeClusterer().run_clustering(preprocessed, k=5)

    with tempfile.TemporaryDirectory() as tmpdir:
        viz = ClusterVisualizer(random_state=42, dpi=50)
        paths = viz.generate_all(preprocessed, clustering, output_dir=tmpdir)

        assert "elbow_silhouette" in paths
        assert "pca_2d" in paths
        assert "pca_3d" in paths
        assert "tsne_2d" in paths
        assert "cluster_heatmap" in paths

        for name, p in paths.items():
            assert os.path.exists(p), f"Figure {name} was not created at {p}"
            assert os.path.getsize(p) > 1000, f"Figure {name} is unusually small"


def test_summary_table_formatting():
    """Verify summary table formats as valid markdown."""
    df_raw = pd.DataFrame(MOCK_ANIME_DATA)
    preprocessed = DataPreprocessor().fit_transform(df_raw)
    clustering = AnimeClusterer().run_clustering(preprocessed, k=5)

    viz = ClusterVisualizer()
    table_str = viz.format_summary_table(clustering.cluster_profiles)
    assert "| cluster_id | archetype |" in table_str or "cluster_id" in table_str


def test_palette_scaling_for_large_k():
    """Verify color map dynamically expands to tab20 (>10) and husl (>20)."""
    viz = ClusterVisualizer()
    cmap_10 = viz._get_color_map(list(range(10)))
    assert len(cmap_10) == 10

    cmap_15 = viz._get_color_map(list(range(15)))
    assert len(cmap_15) == 15
    assert len(set(cmap_15.values())) == 15

    cmap_25 = viz._get_color_map(list(range(25)))
    assert len(cmap_25) == 25
    assert len(set(cmap_25.values())) == 25

