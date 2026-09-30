#!/usr/bin/env python3
"""
Netlify Local Preview Server.

Emulates Netlify's production hosting environment with:
1. Cross-Origin Isolation (COOP: same-origin, COEP: credentialless)
2. Proper WebAssembly (.wasm) and Python wheel (.whl) MIME types
3. Clean URL rewrites (/notebook, /pyodide, /dashboard)
"""

from __future__ import annotations

import argparse
import http.server
import os
import socketserver
import sys
from pathlib import Path


class NetlifyPreviewHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler that injects Netlify production headers."""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".whl": "application/octet-stream",
        ".json": "application/json",
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".css": "text/css",
        ".html": "text/html",
    }

    def end_headers(self) -> None:
        """Inject Netlify Cross-Origin Isolation and CORS headers."""
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def do_GET(self) -> None:
        """Handle URL rewrites matching reports/_redirects."""
        path = self.path.split("?")[0]
        if path == "/notebook":
            self.path = "/index.html"
        elif path == "/pyodide":
            self.path = "/anime_notebook.pyodide.html"
        elif path == "/dashboard":
            self.path = "/anime_dashboard.html"
        return super().do_GET()


def main() -> None:
    parser = argparse.ArgumentParser(description="Netlify Local Preview Server with COOP/COEP")
    parser.add_argument("--port", type=int, default=8888, help="Port to listen on (default: 8888)")
    parser.add_argument(
        "--directory",
        type=str,
        default="reports",
        help="Directory to serve (default: reports)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    serve_dir = repo_root / args.directory

    if not serve_dir.exists():
        print(f"Error: Directory '{serve_dir}' does not exist.")
        sys.exit(1)

    os.chdir(serve_dir)

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReusableTCPServer(("", args.port), NetlifyPreviewHandler) as httpd:
        print("\n" + "=" * 65)
        print(" NETLIFY LOCAL PREVIEW SERVER")
        print("=" * 65)
        print(f" Serving Directory: {serve_dir}")
        print(f" Local URL:         http://localhost:{args.port}")
        print(f" Notebook URL:      http://localhost:{args.port}/notebook")
        print(f" Pyodide URL:       http://localhost:{args.port}/pyodide")
        print(f" COOP Header:       same-origin")
        print(f" COEP Header:       credentialless (SharedArrayBuffer Enabled)")
        print(" Press Ctrl+C to stop.")
        print("=" * 65 + "\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down preview server.")


if __name__ == "__main__":
    main()
