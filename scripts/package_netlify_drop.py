"""
Netlify Drop Deployment Archive Generator.

Packages the reports/ directory into a deploy-ready ZIP archive
optimized for drag-and-drop deployment onto Netlify Drop (app.netlify.com/drop).
"""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


def build_netlify_zip(
    source_dir: str | Path = "reports",
    output_zip: str | Path = "netlify-wasm-deploy.zip",
) -> Path:
    source_path = Path(source_dir).resolve()
    zip_dest = Path(output_zip).resolve()

    if not source_path.exists() or not source_path.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_path}")

    # Exclude internal caches and temporary dev artifacts
    exclude_names = {"__marimo__", "CLAUDE.md", ".DS_Store", "assets", ".git"}

    count = 0
    with zipfile.ZipFile(zip_dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file_path in sorted(source_path.rglob("*")):
            if any(part in exclude_names for part in file_path.parts):
                continue
            if file_path.is_file():
                arcname = file_path.relative_to(source_path)
                zf.write(file_path, arcname)
                count += 1

    return zip_dest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Netlify Drop deployment ZIP archive.")
    parser.add_argument("--source", default="reports", help="Directory to package (default: reports)")
    parser.add_argument("--output", default="netlify-wasm-deploy.zip", help="Output ZIP path (default: netlify-wasm-deploy.zip)")
    args = parser.parse_args()

    zip_file = build_netlify_zip(args.source, args.output)
    size_mb = zip_file.stat().st_size / (1024 * 1024)
    print(f"Deployment ZIP ready: {zip_file} ({size_mb:.2f} MB)")
