"""
Automated tests for the reactive pedagogical Jupyter-style Marimo notebook.
Verifies DAG static check, headless execution via app.run(), reactive knobs,
Altair cluster map widget, CLI flag, WASM HTML export, and root symlink.
"""

import subprocess
import sys
from pathlib import Path
import pytest


def test_notebook_static_marimo_check():
    """Verify marimo check passes with zero DAG circularities, syntax errors, or collisions."""
    repo_root = Path(__file__).resolve().parent.parent
    notebook_path = repo_root / "notebooks" / "anime_notebook.py"
    symlink_path = repo_root / "anime_notebook.py"

    assert notebook_path.exists(), f"Notebook file missing at {notebook_path}"
    assert symlink_path.exists(), f"Root symlink missing at {symlink_path}"

    res_nb = subprocess.run(
        [sys.executable, "-m", "marimo", "check", str(notebook_path)],
        capture_output=True,
        text=True,
    )
    assert res_nb.returncode == 0, f"marimo check failed on notebook:\n{res_nb.stderr}\n{res_nb.stdout}"

    res_link = subprocess.run(
        [sys.executable, "-m", "marimo", "check", str(symlink_path)],
        capture_output=True,
        text=True,
    )
    assert res_link.returncode == 0, f"marimo check failed on root symlink:\n{res_link.stderr}\n{res_link.stdout}"


def test_notebook_headless_app_run():
    """Verify programmatic headless execution via marimo app.run() and key DAG definitions."""
    from notebooks.anime_notebook import app

    outputs, defs = app.run()

    # Core reactive controls and DAG nodes
    expected_defs = [
        "raw_catalog_df",
        "source_name",
        "cohort_picker",
        "sample_slider",
        "min_score_slider",
        "max_tag_features_slider",
        "df_active",
        "df_cleaned",
        "engineered_features",
        "k_metrics_df",
        "suggested_k",
        "k_slider",
        "eps_slider",
        "archetype_summary_df",
        "df_clustered",
        "var_exp",
        "n_noise",
        "cluster_map_widget",
        "detail_table",
    ]

    for d in expected_defs:
        assert d in defs, f"Expected definition '{d}' missing from defs namespace"

    # Verify quantitative properties of calculated values
    assert len(defs["raw_catalog_df"]) > 0
    assert len(defs["df_active"]) > 0
    assert len(defs["df_clustered"]) == len(defs["df_active"])
    assert defs["suggested_k"] >= 2
    assert len(defs["archetype_summary_df"]) == defs["k_slider"].value
    assert defs["cluster_map_widget"] is not None
    assert len(defs["var_exp"]) == 2
    assert defs["var_exp"][0] > 0.0


def test_main_cli_notebook_flag():
    """Verify that main.py exposes the --notebook CLI argument."""
    repo_root = Path(__file__).resolve().parent.parent
    res = subprocess.run(
        [sys.executable, str(repo_root / "main.py"), "--help"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "--notebook" in res.stdout
    assert "Jupyter-style" in res.stdout


def test_wasm_html_notebook_export():
    """Verify that the generated standalone client-side WASM HTML export exists and has valid markup."""
    repo_root = Path(__file__).resolve().parent.parent
    wasm_path = repo_root / "reports" / "anime_notebook.wasm.html"

    assert wasm_path.exists(), f"WASM HTML notebook not found at {wasm_path}"
    file_size = wasm_path.stat().st_size
    assert file_size > 50000, f"WASM HTML notebook size unusually small ({file_size} bytes)"

    with open(wasm_path, "r", encoding="utf-8") as f:
        content = f.read(4096)
        assert "<!DOCTYPE html>" in content or "<html" in content
        assert 'data-marimo="true"' in content


def test_notebook_symlink_identity():
    """Verify root anime_notebook.py symlink resolves directly to notebooks/anime_notebook.py."""
    repo_root = Path(__file__).resolve().parent.parent
    notebook_path = (repo_root / "notebooks" / "anime_notebook.py").resolve()
    symlink_path = (repo_root / "anime_notebook.py").resolve()

    assert symlink_path.exists()
    assert notebook_path.exists()
    assert symlink_path == notebook_path
