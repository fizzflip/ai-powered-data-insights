"""
Integration tests for the end-to-end pipeline.
"""

import os
import tempfile
import pytest
from src.pipeline import InsightsPipeline, PipelineConfig


def test_pipeline_offline_execution():
    """Verify end-to-end pipeline execution in offline mode generates report and plots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        report_dir = os.path.join(tmpdir, "reports")
        fig_dir = os.path.join(report_dir, "figures")

        config = PipelineConfig(
            num_samples=25,
            k=5,
            min_k=2,
            max_k=6,
            output_dir=report_dir,
            figures_dir=fig_dir,
            offline_mode=True,
            generate_plots=True,
            dpi=50,
        )

        pipeline = InsightsPipeline(config)
        results = pipeline.run()

        assert results["num_samples"] == 25
        assert results["k_optimal"] == 5
        assert os.path.exists(results["report_path"])
        assert os.path.getsize(results["report_path"]) > 500

        # Verify figures were generated
        for fig_name, fig_path in results["figure_paths"].items():
            assert os.path.exists(fig_path)
