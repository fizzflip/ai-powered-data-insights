"""
Automated tests for the Marimo interactive visual analytics dashboard.
Verifies DAG static check, headless execution via app.run(), CLI flags, and HTML export.
"""

import os
import subprocess
import sys
from pathlib import Path
import pytest


def test_marimo_static_check():
    """Verify marimo check passes with zero DAG circularities, syntax errors, or collisions."""
    repo_root = Path(__file__).resolve().parent.parent
    notebook_path = repo_root / "notebooks" / "anime_dashboard.py"
    shim_path = repo_root / "dashboard.py"

    assert notebook_path.exists(), f"Notebook file missing at {notebook_path}"
    assert shim_path.exists(), f"Root shim missing at {shim_path}"

    res_nb = subprocess.run(
        [sys.executable, "-m", "marimo", "check", str(notebook_path)],
        capture_output=True,
        text=True,
    )
    assert res_nb.returncode == 0, f"marimo check failed on notebook:\n{res_nb.stderr}"

    res_shim = subprocess.run(
        [sys.executable, "-m", "marimo", "check", str(shim_path)],
        capture_output=True,
        text=True,
    )
    assert res_shim.returncode == 0, f"marimo check failed on root shim:\n{res_shim.stderr}"


def test_dashboard_headless_app_run():
    """Verify programmatic headless execution via marimo app.run()."""
    from notebooks.anime_dashboard import app

    outputs, defs = app.run()

    # Verify key DAG definitions exist and are properly instantiated
    expected_defs = [
        "total_catalog_count",
        "controls_form",
        "active_params",
        "pipeline_results",
        "kpi_strip",
        "tab_archetypes",
        "tab_projections",
        "tab_diagnostics",
        "catalog_table",
        "tab_catalog",
        "tab_comparative",
        "tabs",
        "dashboard_layout",
    ]

    for d in expected_defs:
        assert d in defs, f"Expected definition '{d}' missing from defs namespace"

    assert defs["total_catalog_count"] >= 0
    assert defs["pipeline_results"]["k_optimal"] >= 2
    assert "df_clustered" in defs
    assert len(defs["df_clustered"]) > 0


def test_main_cli_dashboard_flag():
    """Verify that main.py exposes --dashboard, --port, and --headless arguments."""
    repo_root = Path(__file__).resolve().parent.parent
    res = subprocess.run(
        [sys.executable, str(repo_root / "main.py"), "--help"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "--dashboard" in res.stdout
    assert "--port" in res.stdout
    assert "--headless" in res.stdout


def test_static_html_dashboard_export():
    """Verify that the generated static HTML dashboard exists, is self-contained, and non-empty."""
    repo_root = Path(__file__).resolve().parent.parent
    html_path = repo_root / "reports" / "anime_dashboard.html"

    assert html_path.exists(), f"Static dashboard HTML not found at {html_path}"
    file_size = html_path.stat().st_size
    assert file_size > 50000, f"Dashboard HTML size unusually small ({file_size} bytes)"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read(2048)
        assert "<!DOCTYPE html>" in content or "<html" in content


def test_symlink_identity():
    """Verify root dashboard.py resolves to notebooks/anime_dashboard.py."""
    repo_root = Path(__file__).resolve().parent.parent
    notebook_path = (repo_root / "notebooks" / "anime_dashboard.py").resolve()
    shim_path = (repo_root / "dashboard.py").resolve()

    assert notebook_path.exists()
    assert shim_path.exists()
    assert notebook_path == shim_path or notebook_path.read_text() == shim_path.read_text()

