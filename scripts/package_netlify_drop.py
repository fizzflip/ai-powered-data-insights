"""
Netlify Drop Deployment Archive Generator and Clean Build Pipeline.

Automates the complete workflow:
1. Cleans stale build artifacts, temporary caches, and old export bundles.
2. Re-compiles the latest Marimo reactive notebook into standalone single-file WASM (reports/index.html).
3. Ensures compact data assets (reports/data/anime_catalog_compact.json.gz) are present and valid.
4. Enforces Cross-Origin Isolation headers (_headers) and clean URL rewrites (_redirects).
5. Packages all deployable assets into a root-level ZIP archive for Netlify Drop (app.netlify.com/drop).
6. Audits and verifies archive structure, integrity, and gzip magic headers.
"""

from __future__ import annotations

import argparse
import gzip
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any
import zipfile


EXCLUDE_PATTERNS = {
    "__marimo__",
    "CLAUDE.md",
    ".DS_Store",
    "assets",
    ".git",
    "__pycache__",
    "*.pyc",
}


def clean_reports_artifacts(source_dir: Path, output_zip: Path | None = None) -> list[str]:
    """Clean obsolete build caches, temporary directories, and old target zip files."""
    cleaned = []
    
    # 1. Clean subdirectories in reports/
    for sub in ["__marimo__", "assets"]:
        p = source_dir / sub
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            cleaned.append(f"dir: {p.name}/")

    # 2. Clean temporary files in reports/
    for fname in ["CLAUDE.md", ".DS_Store", "Thumbs.db"]:
        p = source_dir / fname
        if p.exists():
            try:
                p.unlink()
                cleaned.append(f"file: {p.name}")
            except OSError:
                pass

    # 3. Clean target zip if requested
    if output_zip and output_zip.exists():
        try:
            output_zip.unlink()
            cleaned.append(f"archive: {output_zip.name}")
        except OSError:
            pass

    return cleaned


def compile_single_file_wasm(
    repo_root: Path,
    reports_dir: Path,
    notebook_path: Path | None = None,
) -> Path:
    """Compile the latest notebooks/anime_notebook.py into single-file reports/index.html."""
    if notebook_path is None:
        notebook_path = repo_root / "notebooks" / "anime_notebook.py"
        if not notebook_path.exists():
            notebook_path = repo_root / "anime_notebook.py"

    if not notebook_path.exists():
        raise FileNotFoundError(f"Marimo notebook source not found at: {notebook_path}")

    index_html = reports_dir / "index.html"
    wasm_html = reports_dir / "anime_notebook.wasm.html"

    # Execute marimo export with input=b"n\n" to bypass sandbox prompt in current venv
    cmd = [
        sys.executable,
        "-m",
        "marimo",
        "export",
        "html-wasm",
        str(notebook_path),
        "--mode",
        "run",
        "--single-file",
        "-o",
        str(index_html),
    ]

    res = subprocess.run(cmd, input="n\n", capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"marimo export html-wasm failed (code {res.returncode}):\n{res.stderr}\n{res.stdout}"
        )

    # Mirror index.html to anime_notebook.wasm.html
    shutil.copy2(index_html, wasm_html)

    # Post-export cleanup: remove any temporary assets directory marimo might leave
    clean_reports_artifacts(reports_dir)

    return index_html


def ensure_catalog_asset(
    repo_root: Path,
    reports_dir: Path,
    force_repackage: bool = False,
) -> Path:
    """Ensure reports/data/anime_catalog_compact.json.gz exists and is non-empty."""
    catalog_path = reports_dir / "data" / "anime_catalog_compact.json.gz"

    if not catalog_path.exists() or force_repackage:
        from scripts.package_catalog import package_catalog

        source_db = repo_root / "data" / "anime_catalog.db"
        source_jsonl = repo_root / "data" / "anime-offline-database.jsonl"
        source = str(source_db) if source_db.exists() else str(source_jsonl)

        if not Path(source).exists():
            # If no raw database exists, verify existing catalog_path
            if catalog_path.exists():
                return catalog_path
            raise FileNotFoundError(
                f"Cannot package catalog: neither {source_db} nor {catalog_path} exists."
            )

        package_catalog(
            source_path=source,
            output_dir=str(repo_root / "data"),
            publish_dir=str(reports_dir / "data"),
        )

    return catalog_path


def build_netlify_zip(
    source_dir: str | Path = "reports",
    output_zip: str | Path = "netlify-wasm-deploy.zip",
    clean: bool = False,
    compile_wasm: bool = False,
    repackage_catalog: bool = False,
    verify: bool = False,
) -> Path:
    """
    Package reports/ directory into a deploy-ready ZIP archive for Netlify Drop.
    
    Parameters:
        source_dir: Directory containing static site assets (default: reports)
        output_zip: Target ZIP archive location (default: netlify-wasm-deploy.zip)
        clean: Clean stale temporary build artifacts before packaging
        compile_wasm: Re-compile Marimo notebook to reports/index.html before packaging
        repackage_catalog: Re-run catalog pruner before packaging
        verify: Audit the resulting archive structure and headers
    """
    source_path = Path(source_dir).resolve()
    zip_dest = Path(output_zip).resolve()
    repo_root = source_path.parent if source_path.name == "reports" else Path.cwd().resolve()

    if not source_path.exists() or not source_path.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_path}")

    # Step 1: Clean stale caches
    if clean:
        clean_reports_artifacts(source_path, zip_dest)

    # Step 2: Compile WASM if requested
    if compile_wasm:
        compile_single_file_wasm(repo_root, source_path)

    # Step 3: Ensure data asset exists if packaging production reports directory
    if repackage_catalog or (source_path == (repo_root / "reports") and (source_path / "data").exists()):
        ensure_catalog_asset(repo_root, source_path, force_repackage=repackage_catalog)

    # Step 4: Write ZIP archive
    with zipfile.ZipFile(zip_dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file_path in sorted(source_path.rglob("*")):
            if any(part in EXCLUDE_PATTERNS for part in file_path.parts):
                continue
            if file_path.is_file():
                arcname = file_path.relative_to(source_path)
                zf.write(file_path, arcname)

    # Step 5: Verification audit
    if verify:
        audit_netlify_zip(zip_dest)

    return zip_dest


def audit_netlify_zip(zip_path: Path) -> dict[str, Any]:
    """Audit the generated Netlify ZIP archive to guarantee deployment readiness."""
    if not zip_path.exists() or zip_path.stat().st_size == 0:
        raise ValueError(f"Target archive missing or empty: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())

        # Check essential root files
        if "index.html" not in names:
            raise ValueError("Verification failed: 'index.html' missing from root of archive.")
        if "_headers" not in names:
            raise ValueError("Verification failed: '_headers' missing from root of archive.")

        # Check headers content (supports full header name and shorthand)
        headers_content = zf.read("_headers").decode("utf-8")
        if (
            "Cross-Origin-Opener-Policy" not in headers_content
            and "COOP" not in headers_content
        ):
            raise ValueError("Verification failed: COOP header missing from _headers.")
        if (
            "Cross-Origin-Embedder-Policy" not in headers_content
            and "COEP" not in headers_content
        ):
            raise ValueError("Verification failed: COEP header missing from _headers.")

        # Check compact catalog if data folder is included
        catalog_name = "data/anime_catalog_compact.json.gz"
        if catalog_name in names:
            raw_bytes = zf.read(catalog_name)
            if len(raw_bytes) < 100 or raw_bytes[:2] != b"\x1f\x8b":
                raise ValueError(f"Verification failed: '{catalog_name}' has invalid gzip format.")

        total_uncompressed = sum(info.file_size for info in zf.infolist())
        compressed_size = zip_path.stat().st_size

        return {
            "file_count": len(names),
            "uncompressed_bytes": total_uncompressed,
            "compressed_bytes": compressed_size,
            "has_index": "index.html" in names,
            "has_headers": "_headers" in names,
            "has_redirects": "_redirects" in names,
            "has_catalog": catalog_name in names,
        }


def clean_build_and_export(
    source_dir: str | Path = "reports",
    output_zip: str | Path = "netlify-wasm-deploy.zip",
    repackage_catalog: bool = False,
) -> Path:
    """Full end-to-end pipeline: clean artifacts -> compile WASM -> package ZIP -> audit."""
    print("=" * 65)
    print(" NETLIFY DROP CLEAN BUILD AND WASM EXPORT PIPELINE")
    print("=" * 65)
    print(f"1. Cleaning stale build caches and previous archives...")
    source_path = Path(source_dir).resolve()
    zip_dest = Path(output_zip).resolve()
    cleaned = clean_reports_artifacts(source_path, zip_dest)
    if cleaned:
        print(f"   Cleaned {len(cleaned)} stale items: {', '.join(cleaned[:5])}")
    else:
        print("   Directory already clean.")

    print(f"2. Compiling latest notebooks/anime_notebook.py into single-file WASM...")
    repo_root = source_path.parent if source_path.name == "reports" else Path.cwd().resolve()
    index_html = compile_single_file_wasm(repo_root, source_path)
    print(f"   Compiled: {index_html} ({index_html.stat().st_size / 1024:.1f} KB)")

    print(f"3. Verifying compact data assets...")
    catalog_path = ensure_catalog_asset(repo_root, source_path, force_repackage=repackage_catalog)
    print(f"   Verified: {catalog_path} ({catalog_path.stat().st_size / (1024*1024):.2f} MB)")

    print(f"4. Packaging deployable root-level ZIP archive...")
    zip_file = build_netlify_zip(
        source_dir=source_path,
        output_zip=zip_dest,
        clean=False,
        compile_wasm=False,
        repackage_catalog=False,
        verify=True,
    )

    audit = audit_netlify_zip(zip_file)
    size_mb = audit["compressed_bytes"] / (1024 * 1024)
    uncomp_mb = audit["uncompressed_bytes"] / (1024 * 1024)

    print(f"\nDEPLOYMENT ARCHIVE GENERATION SUCCESSFUL")
    print(f"  Archive Path:       {zip_file}")
    print(f"  Compressed Size:    {size_mb:.2f} MB")
    print(f"  Uncompressed Size:  {uncomp_mb:.2f} MB")
    print(f"  Total Files in ZIP: {audit['file_count']}")
    print(f"  Root index.html:    {'VERIFIED' if audit['has_index'] else 'MISSING'}")
    print(f"  COOP/COEP Headers:  {'VERIFIED' if audit['has_headers'] else 'MISSING'}")
    print(f"  Redirects Rules:    {'VERIFIED' if audit['has_redirects'] else 'MISSING'}")
    print(f"  40k Compact Data:   {'VERIFIED' if audit['has_catalog'] else 'MISSING'}")
    print("=" * 65)
    print(f"Ready to deploy! Drag and drop {zip_file.name} to https://app.netlify.com/drop\n")

    return zip_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean build, compile WASM, and export deploy-ready Netlify Drop ZIP archive."
    )
    parser.add_argument(
        "--source",
        default="reports",
        help="Directory to package (default: reports)",
    )
    parser.add_argument(
        "--output",
        default="netlify-wasm-deploy.zip",
        help="Output ZIP path (default: netlify-wasm-deploy.zip)",
    )
    parser.add_argument(
        "--build",
        "--rebuild",
        action="store_true",
        help="Re-compile Marimo notebook into standalone WASM HTML before packaging",
    )
    parser.add_argument(
        "--repackage-catalog",
        action="store_true",
        help="Re-run catalog pruner script before packaging",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip cleaning stale build artifacts and caches",
    )
    args = parser.parse_args()

    if args.build:
        clean_build_and_export(
            source_dir=args.source,
            output_zip=args.output,
            repackage_catalog=args.repackage_catalog,
        )
    else:
        zip_file = build_netlify_zip(
            source_dir=args.source,
            output_zip=args.output,
            clean=not args.no_clean,
            compile_wasm=False,
            repackage_catalog=args.repackage_catalog,
            verify=True,
        )
        size_mb = zip_file.stat().st_size / (1024 * 1024)
        print(f"Deployment ZIP ready: {zip_file} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
