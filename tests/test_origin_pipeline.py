"""
Integration and Unit Tests for Origin Cohort Pipeline and Comparative Visualizer.
"""

import os
import shutil
import tempfile
import pandas as pd
import pytest

from src.comparative_visualizer import ComparativeVisualizer
from src.database import AnimeCatalogDB
from src.pipeline import InsightsPipeline, PipelineConfig, run_comparative_pipeline


@pytest.fixture
def temp_output_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_comparative_visualizer_generation(temp_output_dir):
    """Verify that ComparativeVisualizer outputs all 4 diagnostic comparative plots."""
    df_jp = pd.DataFrame([
        {
            "id": 1,
            "title": "Spirited Away",
            "origin_cohort": "jp",
            "sub_origin": "JP",
            "averageScore": 88.0,
            "popularity": 150000,
            "episodes": 1,
            "duration": 125,
            "genres": ["Animation", "Adventure", "Fantasy"],
        },
        {
            "id": 2,
            "title": "Cowboy Bebop",
            "origin_cohort": "jp",
            "sub_origin": "JP",
            "averageScore": 89.0,
            "popularity": 120000,
            "episodes": 26,
            "duration": 24,
            "genres": ["Action", "Sci-Fi"],
        },
    ])

    df_non_jp = pd.DataFrame([
        {
            "id": 3,
            "title": "Soul Land",
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
            "averageScore": 76.0,
            "popularity": 25000,
            "episodes": 250,
            "duration": 20,
            "genres": ["Action", "Fantasy"],
        },
        {
            "id": 4,
            "title": "Tower of God (KR)",
            "origin_cohort": "non-jp",
            "sub_origin": "KR",
            "averageScore": 77.0,
            "popularity": 35000,
            "episodes": 13,
            "duration": 23,
            "genres": ["Action", "Fantasy", "Mystery"],
        },
    ])

    df_all = pd.concat([df_jp, df_non_jp], ignore_index=True)

    viz = ComparativeVisualizer()
    fig_paths = viz.generate_all_comparative(
        df_all=df_all,
        df_jp=df_jp,
        df_non_jp=df_non_jp,
        output_dir=temp_output_dir,
    )

    assert "origin_distribution" in fig_paths
    assert "score_popularity" in fig_paths
    assert "format_comparison" in fig_paths
    assert "genre_divergence" in fig_paths

    for name, path in fig_paths.items():
        assert os.path.exists(path), f"Figure {name} was not created at {path}"
        assert os.path.getsize(path) > 1000, f"Figure {name} is unusually small ({os.path.getsize(path)} bytes)"


def test_pipeline_jp_cohort(temp_output_dir):
    """Test running pipeline restricted to Japanese domestic titles."""
    config = PipelineConfig(
        num_samples=60,
        origin="jp",
        output_dir=temp_output_dir,
        offline_mode=True,
        generate_plots=False,
    )
    pipeline = InsightsPipeline(config)
    results = pipeline.run()

    assert results["num_samples"] > 0
    assert "df" in results
    df = results["df"]
    # All titles in df must be marked JP
    assert all(df["origin_cohort"] == "jp")
    assert results["report_path"].endswith("cluster_analysis_report_jp.md")
    assert os.path.exists(results["report_path"])


def test_pipeline_non_jp_cohort(temp_output_dir):
    """Test running pipeline restricted to non-Japanese international titles."""
    config = PipelineConfig(
        num_samples=60,
        origin="non-jp",
        output_dir=temp_output_dir,
        offline_mode=True,
        generate_plots=False,
    )
    pipeline = InsightsPipeline(config)
    results = pipeline.run()

    assert results["num_samples"] > 0
    assert "df" in results
    df = results["df"]
    # All titles in df must be marked non-jp
    assert all(df["origin_cohort"] == "non-jp")
    assert results["report_path"].endswith("cluster_analysis_report_non_jp.md")
    assert os.path.exists(results["report_path"])


def test_comparative_pipeline_run(temp_output_dir):
    """Test running dual-cohort comparative pipeline."""
    config = PipelineConfig(
        num_samples=50,
        origin="compare",
        output_dir=temp_output_dir,
        offline_mode=True,
        generate_plots=False,
    )
    results = run_comparative_pipeline(config)

    assert results["origin"] == "compare"
    assert results["num_jp"] > 0
    assert results["num_non_jp"] > 0
    assert results["num_samples"] == results["num_jp"] + results["num_non_jp"]

    assert "jp" in results["k_optimal"]
    assert "non_jp" in results["k_optimal"]
    assert "jp" in results["archetype_labels"]
    assert "non_jp" in results["archetype_labels"]

    report_path = results["report_path"]
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Comparative Cross-Market Anime Analysis" in content
    assert "Japanese Domestic" in content
    assert "Overseas (Non-JP)" in content
    assert "Chinese Donghua" in content
    assert len(content) > 1500
