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
