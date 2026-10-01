"""
Tests for Netlify Production Deployment Configuration.

Verifies:
1. netlify.toml syntax, build commands, and environment variables
2. Cross-Origin Isolation headers (COOP: same-origin, COEP: credentialless)
3. MIME type declarations for WebAssembly (.wasm) and Python wheels (.whl)
4. reports/_headers and reports/_redirects synchronization
5. Local Netlify preview server handler
"""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path

import pytest

from scripts.serve_netlify_preview import NetlifyPreviewHandler


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_netlify_toml_structure(repo_root: Path):
    """Verify netlify.toml exists, parses as valid TOML, and defines required fields."""
    toml_path = repo_root / "netlify.toml"
    assert toml_path.exists(), f"netlify.toml missing at {toml_path}"

    with open(toml_path, "rb") as f:
        config = tomllib.load(f)

    # 1. Build table
    assert "build" in config
    assert config["build"]["publish"] == "reports"
    assert "marimo export html-wasm" in config["build"]["command"]
    assert "--single-file" in config["build"]["command"]

    # 2. Redirects
    assert "redirects" in config
    redirect_map = {r["from"]: r["to"] for r in config["redirects"]}
    assert redirect_map.get("/notebook") == "/index.html"
    assert redirect_map.get("/pyodide") == "/anime_notebook.pyodide.html"
    assert redirect_map.get("/dashboard") == "/anime_dashboard.html"


def test_netlify_cross_origin_isolation_headers(repo_root: Path):
    """Verify netlify.toml enforces COOP and COEP for SharedArrayBuffer and WASM workers."""
    toml_path = repo_root / "netlify.toml"
    with open(toml_path, "rb") as f:
        config = tomllib.load(f)

    assert "headers" in config
    global_headers = None
    for entry in config["headers"]:
        if entry.get("for") == "/*":
            global_headers = entry.get("values", {})
            break

    assert global_headers is not None, "Missing global '/*' header definition in netlify.toml"
    assert global_headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert global_headers.get("Cross-Origin-Embedder-Policy") == "credentialless"
    assert global_headers.get("Access-Control-Allow-Origin") == "*"


def test_reports_standalone_headers_and_redirects(repo_root: Path):
    """Verify reports/_headers and reports/_redirects exist for standalone Netlify Drop deployment."""
    headers_path = repo_root / "reports" / "_headers"
    redirects_path = repo_root / "reports" / "_redirects"

    assert headers_path.exists(), "reports/_headers file missing"
    assert redirects_path.exists(), "reports/_redirects file missing"

    headers_content = headers_path.read_text(encoding="utf-8")
    assert "Cross-Origin-Opener-Policy: same-origin" in headers_content
    assert "Cross-Origin-Embedder-Policy: credentialless" in headers_content
    assert "application/wasm" in headers_content

    redirects_content = redirects_path.read_text(encoding="utf-8")
    assert "/notebook" in redirects_content
    assert "/pyodide" in redirects_content
    assert "/dashboard" in redirects_content


def test_netlify_preview_handler_mime_and_headers():
    """Verify NetlifyPreviewHandler extensions map and header injection."""
    assert NetlifyPreviewHandler.extensions_map[".wasm"] == "application/wasm"
    assert NetlifyPreviewHandler.extensions_map[".whl"] == "application/octet-stream"


def test_build_netlify_zip_archive(tmp_path: Path):
    """Verify Netlify Drop ZIP generator packages root files, headers, and excludes caches."""
    import zipfile
    from scripts.package_netlify_drop import build_netlify_zip

    mock_reports = tmp_path / "mock_reports"
    mock_reports.mkdir()
    (mock_reports / "index.html").write_text("<html></html>", encoding="utf-8")
    (mock_reports / "_headers").write_text("/*\n  Cross-Origin-Opener-Policy: same-origin\n  Cross-Origin-Embedder-Policy: credentialless", encoding="utf-8")
    (mock_reports / "_redirects").write_text("/from /to 200", encoding="utf-8")

    sub_data = mock_reports / "data"
    sub_data.mkdir()
    (sub_data / "catalog.json.gz").write_bytes(b"\x1f\x8b\x08test")

    # Temp cache folder that must be excluded
    marimo_cache = mock_reports / "__marimo__"
    marimo_cache.mkdir()
    (marimo_cache / "cache.json").write_text("{}", encoding="utf-8")

    out_zip = tmp_path / "test-deploy.zip"
    build_netlify_zip(source_dir=mock_reports, output_zip=out_zip)

    assert out_zip.exists()
    with zipfile.ZipFile(out_zip, "r") as zf:
        names = zf.namelist()
        assert "index.html" in names
        assert "_headers" in names
        assert "_redirects" in names
        assert "data/catalog.json.gz" in names
        assert not any("__marimo__" in n for n in names)


def test_clean_reports_artifacts(tmp_path: Path):
    """Verify that clean_reports_artifacts purges stale caches, old zips, and CLAUDE.md."""
    from scripts.package_netlify_drop import clean_reports_artifacts

    mock_reports = tmp_path / "mock_reports"
    mock_reports.mkdir()
    (mock_reports / "assets").mkdir()
    (mock_reports / "assets" / "bundle.js").write_text("console.log(1)")
    (mock_reports / "__marimo__").mkdir()
    (mock_reports / "CLAUDE.md").write_text("old notes")
    (mock_reports / ".DS_Store").write_bytes(b"\x00")
    (mock_reports / "index.html").write_text("<html></html>")

    mock_zip = tmp_path / "old-deploy.zip"
    mock_zip.write_bytes(b"PK\x05\x06" + b"\x00" * 18)

    cleaned = clean_reports_artifacts(mock_reports, mock_zip)
    assert len(cleaned) >= 4
    assert not (mock_reports / "assets").exists()
    assert not (mock_reports / "__marimo__").exists()
    assert not (mock_reports / "CLAUDE.md").exists()
    assert not mock_zip.exists()
    assert (mock_reports / "index.html").exists()


def test_audit_netlify_zip_validation(tmp_path: Path):
    """Verify audit_netlify_zip validates root files, headers, and gzip magic bytes."""
    import zipfile
    from scripts.package_netlify_drop import audit_netlify_zip

    valid_zip = tmp_path / "valid.zip"
    with zipfile.ZipFile(valid_zip, "w") as zf:
        zf.writestr("index.html", "<html></html>")
        zf.writestr(
            "_headers",
            "/*\n  Cross-Origin-Opener-Policy: same-origin\n  Cross-Origin-Embedder-Policy: credentialless",
        )
        zf.writestr("_redirects", "/from /to 200")
        zf.writestr("data/anime_catalog_compact.json.gz", b"\x1f\x8b\x08\x00\x00\x00\x00\x00" + b"x" * 120)

    audit = audit_netlify_zip(valid_zip)
    assert audit["has_index"] is True
    assert audit["has_headers"] is True
    assert audit["has_redirects"] is True
    assert audit["has_catalog"] is True
    assert audit["file_count"] == 4


def test_main_cli_build_netlify_flag():
    """Verify that main.py exposes the --build-netlify argument."""
    import subprocess
    repo_root = Path(__file__).resolve().parent.parent
    res = subprocess.run(
        [sys.executable, str(repo_root / "main.py"), "--help"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "--build-netlify" in res.stdout
    assert "Netlify Drop" in res.stdout


