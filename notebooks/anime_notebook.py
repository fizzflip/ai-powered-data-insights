# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair>=5.0.0",
#     "marimo>=0.25.0",
#     "numpy",
#     "pandas",
#     "scikit-learn",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(
    width="medium",
    app_title="Empirical Anime Latent Space & Archetype Analysis",
)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def intro_narrative(mo):
    mo.md(r"""
    # Empirical Latent Space and Cluster Archetype Analysis in Animated Media
    ### *Codebase: https://github.com/fizzflip/ai-powered-data-insights*

    This study provides a structured data science investigation analyzing an empirical catalog of animation titles spanning Japanese television broadcasts, Chinese Donghua, and Korean Aeni. The workflow models multidimensional audience reception, format parameters, and categorical taxonomies through dimensionality reduction and unsupervised clustering.

    ---
    """)
    return


@app.cell(hide_code=True)
def setup_and_imports():
    import os
    import sys
    from pathlib import Path

    import altair as alt
    import numpy as np
    import pandas as pd
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.decomposition import PCA
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    # Resolve repository root safely without failing in Pyodide/browser
    try:
        _current = Path(__file__).resolve()
        repo_root = _current.parent.parent if _current.parent.name == "notebooks" else _current.parent
    except Exception:
        repo_root = Path(".")

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return (
        DBSCAN,
        KMeans,
        PCA,
        StandardScaler,
        TfidfVectorizer,
        alt,
        np,
        pd,
        repo_root,
        silhouette_score,
    )


@app.cell(hide_code=True)
def embedded_catalog_data():
    # Curated standalone fallback dataset to guarantee zero-backend execution in client-side Pyodide/WASM
    EMBEDDED_CATALOG = [
        {
            "id": 1,
            "title": "Cowboy Bebop",
            "seasonYear": 1998,
            "averageScore": 89,
            "popularity": 340000,
            "favourites": 45000,
            "episodes": 26,
            "duration": 24,
            "genres": ["Action", "Sci-Fi"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 20,
            "title": "Neon Genesis Evangelion",
            "seasonYear": 1995,
            "averageScore": 83,
            "popularity": 320000,
            "favourites": 95000,
            "episodes": 26,
            "duration": 24,
            "genres": ["Action", "Drama", "Mecha", "Psychological"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 164,
            "title": "Princess Mononoke",
            "seasonYear": 1997,
            "averageScore": 88,
            "popularity": 260000,
            "favourites": 22000,
            "episodes": 1,
            "duration": 133,
            "genres": ["Action", "Adventure", "Fantasy"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 199,
            "title": "Spirited Away",
            "seasonYear": 2001,
            "averageScore": 88,
            "popularity": 380000,
            "favourites": 34000,
            "episodes": 1,
            "duration": 125,
            "genres": ["Adventure", "Fantasy", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 5114,
            "title": "Fullmetal Alchemist: Brotherhood",
            "seasonYear": 2009,
            "averageScore": 91,
            "popularity": 490000,
            "favourites": 88000,
            "episodes": 64,
            "duration": 24,
            "genres": ["Action", "Adventure", "Drama", "Fantasy"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 9253,
            "title": "Steins;Gate",
            "seasonYear": 2011,
            "averageScore": 90,
            "popularity": 410000,
            "favourites": 72000,
            "episodes": 24,
            "duration": 24,
            "genres": ["Drama", "Psychological", "Sci-Fi", "Thriller"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 1535,
            "title": "Death Note",
            "seasonYear": 2006,
            "averageScore": 86,
            "popularity": 540000,
            "favourites": 68000,
            "episodes": 37,
            "duration": 23,
            "genres": ["Mystery", "Psychological", "Supernatural", "Thriller"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 16498,
            "title": "Attack on Titan",
            "seasonYear": 2013,
            "averageScore": 85,
            "popularity": 620000,
            "favourites": 67000,
            "episodes": 25,
            "duration": 24,
            "genres": ["Action", "Drama", "Fantasy", "Mystery"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 101922,
            "title": "Kimetsu no Yaiba: Demon Slayer",
            "seasonYear": 2019,
            "averageScore": 84,
            "popularity": 510000,
            "favourites": 42000,
            "episodes": 26,
            "duration": 24,
            "genres": ["Action", "Fantasy", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 113415,
            "title": "Jujutsu Kaisen",
            "seasonYear": 2020,
            "averageScore": 86,
            "popularity": 490000,
            "favourites": 38000,
            "episodes": 24,
            "duration": 24,
            "genres": ["Action", "Fantasy", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 154587,
            "title": "Sousou no Frieren",
            "seasonYear": 2023,
            "averageScore": 93,
            "popularity": 320000,
            "favourites": 45000,
            "episodes": 28,
            "duration": 24,
            "genres": ["Adventure", "Drama", "Fantasy"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 127230,
            "title": "Chainsaw Man",
            "seasonYear": 2022,
            "averageScore": 84,
            "popularity": 460000,
            "favourites": 49000,
            "episodes": 12,
            "duration": 24,
            "genres": ["Action", "Drama", "Horror", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 7785,
            "title": "The Tatami Galaxy",
            "seasonYear": 2010,
            "averageScore": 85,
            "popularity": 132000,
            "favourites": 16400,
            "episodes": 11,
            "duration": 23,
            "genres": ["Comedy", "Mystery", "Psychological", "Romance"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 5081,
            "title": "Bakemonogatari",
            "seasonYear": 2009,
            "averageScore": 83,
            "popularity": 280000,
            "favourites": 41000,
            "episodes": 15,
            "duration": 25,
            "genres": [
                "Comedy",
                "Mystery",
                "Psychological",
                "Romance",
                "Supernatural",
            ],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 20665,
            "title": "Ping Pong the Animation",
            "seasonYear": 2014,
            "averageScore": 86,
            "popularity": 140000,
            "favourites": 15000,
            "episodes": 11,
            "duration": 23,
            "genres": ["Drama", "Psychological", "Sports"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 19,
            "title": "Monster",
            "seasonYear": 2004,
            "averageScore": 88,
            "popularity": 240000,
            "favourites": 36000,
            "episodes": 74,
            "duration": 24,
            "genres": ["Drama", "Mystery", "Psychological", "Thriller"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 339,
            "title": "Serial Experiments Lain",
            "seasonYear": 1998,
            "averageScore": 80,
            "popularity": 210000,
            "favourites": 31000,
            "episodes": 13,
            "duration": 24,
            "genres": ["Drama", "Mystery", "Psychological", "Sci-Fi"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 30,
            "title": "Neon Genesis Evangelion: The End of Evangelion",
            "seasonYear": 1997,
            "averageScore": 86,
            "popularity": 240000,
            "favourites": 37000,
            "episodes": 1,
            "duration": 87,
            "genres": ["Action", "Drama", "Mecha", "Psychological", "Sci-Fi"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 43,
            "title": "Ghost in the Shell",
            "seasonYear": 1995,
            "averageScore": 82,
            "popularity": 210000,
            "favourites": 16000,
            "episodes": 1,
            "duration": 83,
            "genres": ["Action", "Mecha", "Psychological", "Sci-Fi"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 101347,
            "title": "Mo Dao Zu Shi (Grandmaster of Demonic Cultivation)",
            "seasonYear": 2018,
            "averageScore": 84,
            "popularity": 95000,
            "favourites": 19000,
            "episodes": 15,
            "duration": 24,
            "genres": [
                "Action",
                "Adventure",
                "Drama",
                "Fantasy",
                "Mystery",
                "Supernatural",
            ],
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
        },
        {
            "id": 108465,
            "title": "Tian Guan Ci Fu (Heaven Official's Blessing)",
            "seasonYear": 2020,
            "averageScore": 83,
            "popularity": 88000,
            "favourites": 16500,
            "episodes": 11,
            "duration": 24,
            "genres": [
                "Action",
                "Adventure",
                "Drama",
                "Fantasy",
                "Supernatural",
            ],
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
        },
        {
            "id": 11061,
            "title": "Hunter x Hunter (2011)",
            "seasonYear": 2011,
            "averageScore": 90,
            "popularity": 480000,
            "favourites": 82000,
            "episodes": 148,
            "duration": 23,
            "genres": ["Action", "Adventure", "Fantasy"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 101921,
            "title": "Soul Land (Douluo Dalu)",
            "seasonYear": 2018,
            "averageScore": 77,
            "popularity": 32000,
            "favourites": 4200,
            "episodes": 250,
            "duration": 20,
            "genres": ["Action", "Adventure", "Fantasy", "Romance"],
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
        },
        {
            "id": 111324,
            "title": "A Will Eternal (Yi Nian Yong Heng)",
            "seasonYear": 2020,
            "averageScore": 78,
            "popularity": 21000,
            "favourites": 2600,
            "episodes": 106,
            "duration": 20,
            "genres": ["Action", "Comedy", "Fantasy"],
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
        },
        {
            "id": 107419,
            "title": "Battle Through the Heavens (Doupo Cangqiong)",
            "seasonYear": 2017,
            "averageScore": 76,
            "popularity": 28000,
            "favourites": 2900,
            "episodes": 12,
            "duration": 22,
            "genres": ["Action", "Adventure", "Fantasy"],
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
        },
        {
            "id": 113417,
            "title": "Tower of God (Kami no Tou)",
            "seasonYear": 2020,
            "averageScore": 77,
            "popularity": 290000,
            "favourites": 15000,
            "episodes": 13,
            "duration": 23,
            "genres": ["Action", "Adventure", "Drama", "Fantasy", "Mystery"],
            "origin_cohort": "non-jp",
            "sub_origin": "KR",
        },
        {
            "id": 141821,
            "title": "The Daily Life of the Immortal King",
            "seasonYear": 2020,
            "averageScore": 73,
            "popularity": 140000,
            "favourites": 7800,
            "episodes": 15,
            "duration": 18,
            "genres": [
                "Action",
                "Adventure",
                "Comedy",
                "Fantasy",
                "Slice of Life",
            ],
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
        },
        {
            "id": 140960,
            "title": "SPY x FAMILY",
            "seasonYear": 2022,
            "averageScore": 83,
            "popularity": 420000,
            "favourites": 31500,
            "episodes": 12,
            "duration": 24,
            "genres": ["Action", "Comedy", "Slice of Life", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 99423,
            "title": "Scissor Seven (Cike Wu Liuqi)",
            "seasonYear": 2018,
            "averageScore": 81,
            "popularity": 85000,
            "favourites": 9200,
            "episodes": 10,
            "duration": 14,
            "genres": ["Action", "Comedy", "Drama", "Mystery", "Supernatural"],
            "origin_cohort": "non-jp",
            "sub_origin": "CN",
        },
        {
            "id": 132405,
            "title": "Bocchi the Rock!",
            "seasonYear": 2022,
            "averageScore": 88,
            "popularity": 220000,
            "favourites": 38000,
            "episodes": 12,
            "duration": 24,
            "genres": ["Comedy", "Music", "Slice of Life"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 14513,
            "title": "Kimi no Na wa. (Your Name.)",
            "seasonYear": 2016,
            "averageScore": 89,
            "popularity": 450000,
            "favourites": 59000,
            "episodes": 1,
            "duration": 107,
            "genres": ["Drama", "Romance", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 20755,
            "title": "Koe no Katachi (A Silent Voice)",
            "seasonYear": 2016,
            "averageScore": 89,
            "popularity": 430000,
            "favourites": 53000,
            "episodes": 1,
            "duration": 130,
            "genres": ["Drama", "Slice of Life"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 20605,
            "title": "Tokyo Ghoul",
            "seasonYear": 2014,
            "averageScore": 75,
            "popularity": 520000,
            "favourites": 48000,
            "episodes": 12,
            "duration": 24,
            "genres": [
                "Action",
                "Drama",
                "Horror",
                "Mystery",
                "Psychological",
                "Supernatural",
            ],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 21856,
            "title": "Boku no Hero Academia (My Hero Academia)",
            "seasonYear": 2016,
            "averageScore": 79,
            "popularity": 540000,
            "favourites": 35000,
            "episodes": 13,
            "duration": 24,
            "genres": ["Action", "Adventure", "Comedy", "Sci-Fi"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 10087,
            "title": "Fate/Zero",
            "seasonYear": 2011,
            "averageScore": 83,
            "popularity": 290000,
            "favourites": 26000,
            "episodes": 13,
            "duration": 28,
            "genres": ["Action", "Drama", "Fantasy", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 21519,
            "title": "Kimi no Suizou wo Tabetai (I Want to Eat Your Pancreas)",
            "seasonYear": 2018,
            "averageScore": 85,
            "popularity": 240000,
            "favourites": 24000,
            "episodes": 1,
            "duration": 108,
            "genres": ["Drama", "Romance", "Slice of Life"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 13601,
            "title": "Psycho-Pass",
            "seasonYear": 2012,
            "averageScore": 83,
            "popularity": 320000,
            "favourites": 29000,
            "episodes": 22,
            "duration": 23,
            "genres": ["Action", "Psychological", "Sci-Fi", "Thriller"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 1575,
            "title": "Code Geass: Hangyaku no Lelouch",
            "seasonYear": 2006,
            "averageScore": 87,
            "popularity": 420000,
            "favourites": 63000,
            "episodes": 25,
            "duration": 24,
            "genres": ["Action", "Drama", "Mecha", "Sci-Fi", "Thriller"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 21087,
            "title": "One Punch Man",
            "seasonYear": 2015,
            "averageScore": 85,
            "popularity": 590000,
            "favourites": 52000,
            "episodes": 12,
            "duration": 24,
            "genres": ["Action", "Comedy", "Sci-Fi", "Supernatural"],
            "origin_cohort": "jp",
            "sub_origin": "JP",
        },
        {
            "id": 113418,
            "title": "The God of High School",
            "seasonYear": 2020,
            "averageScore": 68,
            "popularity": 190000,
            "favourites": 5400,
            "episodes": 13,
            "duration": 23,
            "genres": ["Action", "Comedy", "Supernatural"],
            "origin_cohort": "non-jp",
            "sub_origin": "KR",
        },
    ]
    return (EMBEDDED_CATALOG,)


@app.cell
def catalog_toggle_control(mo):
    load_full_db = mo.ui.checkbox(
        label="Load Full 40,000+ Title Catalog (Manami Offline DB, 1.1 MB)",
        value=False,
    )
    return (load_full_db,)


@app.cell
async def load_resilient_catalog(
    EMBEDDED_CATALOG,
    load_full_db,
    pd,
    repo_root,
):
    import gzip as _gzip
    import json as _json
    import os as _os
    import sqlite3 as _sqlite3
    import sys as _sys

    records = []
    source_name = "Embedded Standalone Benchmark Dataset"
    catalog_status = "Default Fast Subset Active"

    # Route A: Lazy-load full 40,000+ Manami catalog when toggled
    if load_full_db.value:
        is_emscripten = _sys.platform == "emscripten" or "pyodide" in _sys.modules

        if is_emscripten:
            # Browser WASM execution path via Pyodide pyfetch
            try:
                import posixpath as _posixpath
                import re as _re
                from pyodide.http import pyfetch
                import js as _js

                # -------------------------------------------------------------
                # 1. Fully-Qualified Absolute URL Construction in Web Workers
                # In Marimo WASM, the worker's self.location.href is a blob: URL
                # (e.g. blob:http://localhost:8888/<uuid>). Relative URLs fail
                # with "TypeError: Failed to construct 'Request'". We extract
                # the true document origin and base path to construct absolute URLs.
                # -------------------------------------------------------------
                _origin = ""
                _doc_path = ""

                # Step 1a: Inspect Worker / Window location
                try:
                    _loc = getattr(_js, "location", None)
                    if _loc:
                        _raw_origin = str(getattr(_loc, "origin", "") or "")
                        if _raw_origin and _raw_origin != "null" and _raw_origin.startswith(("http://", "https://")):
                            _origin = _raw_origin.rstrip("/")

                        _raw_href = str(getattr(_loc, "href", "") or "")
                        if not _origin and _raw_href:
                            _m = _re.search(r"https?://[^/]+", _raw_href)
                            if _m:
                                _origin = _m.group(0).rstrip("/")

                        # Check pathname if href is a standard HTTP URL (non-blob)
                        if _raw_href and not _raw_href.startswith("blob:"):
                            _raw_pathname = str(getattr(_loc, "pathname", "") or "")
                            if _raw_pathname and _raw_pathname != "/":
                                _doc_path = _raw_pathname
                except Exception:
                    pass

                # Step 1b: Inspect Document location if accessible (main thread / iframe)
                try:
                    _doc = getattr(_js, "document", None)
                    if _doc and hasattr(_doc, "location"):
                        _d_loc = _doc.location
                        _d_origin = str(getattr(_d_loc, "origin", "") or "")
                        if _d_origin and _d_origin != "null" and _d_origin.startswith(("http://", "https://")):
                            _origin = _d_origin.rstrip("/")
                        _d_pathname = str(getattr(_d_loc, "pathname", "") or "")
                        if _d_pathname and _d_pathname != "/":
                            _doc_path = _d_pathname
                except Exception:
                    pass

                # Derive clean base directory (handles /notebook, /reports/index.html, subpaths)
                _base_dir = ""
                if _doc_path:
                    _clean_p = _doc_path.split("?")[0].split("#")[0]
                    if _clean_p.endswith((".html", ".htm")):
                        _base_dir = _posixpath.dirname(_clean_p)
                    else:
                        _base_dir = _clean_p.rstrip("/")
                    if _base_dir == "/":
                        _base_dir = ""

                # -------------------------------------------------------------
                # 2. Multi-Tier Resilient Fetch Hierarchy
                # -------------------------------------------------------------
                _tier1_candidates = []
                if _origin:
                    if _base_dir:
                        _tier1_candidates.append(f"{_origin}{_base_dir}/data/anime_catalog_compact.json.gz")
                        _tier1_candidates.append(f"{_origin}{_base_dir}/reports/data/anime_catalog_compact.json.gz")
                    _tier1_candidates.append(f"{_origin}/data/anime_catalog_compact.json.gz")
                    _tier1_candidates.append(f"{_origin}/reports/data/anime_catalog_compact.json.gz")

                _tier2_candidates = [
                    "./data/anime_catalog_compact.json.gz",
                    "data/anime_catalog_compact.json.gz",
                    "/data/anime_catalog_compact.json.gz",
                    "./reports/data/anime_catalog_compact.json.gz",
                    "/reports/data/anime_catalog_compact.json.gz",
                ]

                _tier3_candidates = [
                    "https://cdn.jsdelivr.net/gh/fizzflip/ai-powered-data-insights@master/reports/data/anime_catalog_compact.json.gz",
                    "https://raw.githubusercontent.com/fizzflip/ai-powered-data-insights/master/reports/data/anime_catalog_compact.json.gz",
                ]

                def _dedup(urls):
                    seen = set()
                    out = []
                    for u in urls:
                        if u and u not in seen:
                            seen.add(u)
                            out.append(u)
                    return out

                _all_tiers = [
                    ("Tier 1 (Worker-Derived Absolute URL)", _dedup(_tier1_candidates)),
                    ("Tier 2 (Context-Relative URL)", _dedup(_tier2_candidates)),
                    ("Tier 3 (Remote CDN Fallback)", _dedup(_tier3_candidates)),
                ]

                _raw_bytes = None
                _successful_tier = None
                _fetch_errors = []

                for _tier_name, _candidates in _all_tiers:
                    for _url in _candidates:
                        try:
                            _resp = await pyfetch(_url)
                            if _resp.status == 200:
                                _raw_bytes = await _resp.bytes()
                                _successful_tier = _tier_name
                                break
                            else:
                                _fetch_errors.append(f"{_url} -> HTTP {_resp.status}")
                        except Exception as _e:
                            _fetch_errors.append(f"{_url} -> {type(_e).__name__}: {_e}")
                    if _raw_bytes is not None:
                        break

                if _raw_bytes is not None:
                    # Resilient decompression: handle raw gzip vs CDN transparent decompression
                    if len(_raw_bytes) >= 2 and _raw_bytes[:2] == b"\x1f\x8b":
                        decompressed = _gzip.decompress(_raw_bytes)
                    else:
                        decompressed = _raw_bytes

                    records = _json.loads(decompressed.decode("utf-8"))
                    source_name = f"Manami Offline Database ({len(records):,} titles via Pyodide HTTP)"
                    catalog_status = f"Live 40k+ Catalog Ingested Successfully via {_successful_tier}"
                else:
                    _last_err = _fetch_errors[-1] if _fetch_errors else "Unknown fetch failure"
                    if not _origin or _origin == "null":
                        catalog_status = f"Local file:// restricts live fetch ({_last_err}). Serve via python scripts/serve_netlify_preview.py"
                    else:
                        catalog_status = f"Catalog Fetch Fallback: {_last_err}"
            except Exception as ex:
                catalog_status = f"Pyodide Fetch Error: {ex}"

        else:
            # Native desktop / CPython execution path via local filesystem
            local_json_gz = repo_root / "data" / "anime_catalog_compact.json.gz"
            reports_json_gz = repo_root / "reports" / "data" / "anime_catalog_compact.json.gz"
            local_db = repo_root / "data" / "anime_catalog_compact.db"

            target_gz = local_json_gz if local_json_gz.exists() else (reports_json_gz if reports_json_gz.exists() else None)

            if target_gz and target_gz.exists():
                try:
                    with _gzip.open(target_gz, "rt", encoding="utf-8") as f:
                        records = _json.load(f)
                    source_name = f"Local Compact Gzip Catalog ({len(records):,} titles)"
                    catalog_status = "Local Gzip Catalog Loaded"
                except Exception as ex:
                    catalog_status = f"Local Gzip Read Error: {ex}"

            elif local_db.exists():
                try:
                    conn = _sqlite3.connect(str(local_db))
                    conn.row_factory = _sqlite3.Row
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM anime_records")
                    rows = cur.fetchall()
                    for r in rows:
                        records.append({
                            "id": r["id"],
                            "title": r["title"],
                            "seasonYear": r["season_year"],
                            "averageScore": r["average_score"],
                            "popularity": r["popularity"],
                            "favourites": r["favourites"],
                            "episodes": r["episodes"],
                            "duration": r["duration"],
                            "genres": _json.loads(r["genres"]) if r["genres"] else [],
                            "tags": _json.loads(r["tags"]) if r["tags"] else [],
                            "origin_cohort": r["origin_cohort"] or "jp",
                            "sub_origin": r["sub_origin"] or "JP",
                        })
                    conn.close()
                    source_name = f"Local Compact SQLite Catalog ({len(records):,} titles)"
                    catalog_status = "Local SQLite Catalog Loaded"
                except Exception as ex:
                    catalog_status = f"Local SQLite Read Error: {ex}"

    # Route B: Fast default execution (Instant 0 ms latency)
    if not records:
        # Check if local SQLite database exists for standard desktop runs
        db_path = repo_root / "data" / "anime_catalog.db"
        if not load_full_db.value and db_path.exists():
            try:
                conn = _sqlite3.connect(str(db_path))
                conn.row_factory = _sqlite3.Row
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT external_id, id, title_romaji, title_english,
                           season_year, season, episodes, duration,
                           genres_json, tags_json, average_score, popularity,
                           favourites, country_code, is_jp, raw_json
                    FROM anime_records
                    ORDER BY popularity DESC
                    LIMIT 2000
                    """
                )
                rows = cur.fetchall()
                for _row in rows:
                    g_val = _row["genres_json"]
                    genres = _json.loads(g_val) if g_val and g_val.startswith("[") else []
                    t_val = _row["tags_json"]
                    tags = _json.loads(t_val) if t_val and t_val.startswith("[") else []
                    title = _row["title_english"] or _row["title_romaji"] or "Unknown"
                    is_jp_val = int(_row["is_jp"]) if _row["is_jp"] is not None else 1
                    c_code = str(_row["country_code"]) if _row["country_code"] else ("JP" if is_jp_val == 1 else "OTHER")
                    records.append({
                        "id": _row["external_id"] or _row["id"],
                        "title": title,
                        "seasonYear": _row["season_year"],
                        "averageScore": _row["average_score"],
                        "popularity": _row["popularity"],
                        "favourites": _row["favourites"],
                        "episodes": _row["episodes"],
                        "duration": _row["duration"],
                        "genres": genres,
                        "tags": tags,
                        "origin_cohort": "jp" if is_jp_val == 1 else "non-jp",
                        "sub_origin": c_code,
                    })
                conn.close()
                source_name = f"Bundled SQLite Baseline ({len(records):,} titles)"
            except Exception:
                records = []

        # Fallback to zero-dependency embedded benchmark array
        if not records:
            records = EMBEDDED_CATALOG
            source_name = f"Embedded Client-Side Baseline ({len(records)} benchmark titles)"

    raw_catalog_df = pd.DataFrame(records)

    # Normalize column types
    for col in ["averageScore", "popularity", "favourites", "seasonYear", "episodes", "duration"]:
        if col in raw_catalog_df.columns:
            raw_catalog_df[col] = pd.to_numeric(raw_catalog_df[col], errors="coerce")

    def _clean_title(t):
        if isinstance(t, dict):
            return t.get("english") or t.get("romaji") or t.get("userPreferred") or "Unknown"
        return str(t) if pd.notna(t) else "Unknown"

    if "title" in raw_catalog_df.columns:
        raw_catalog_df["title"] = raw_catalog_df["title"].apply(_clean_title)

    if "origin_cohort" not in raw_catalog_df.columns:
        raw_catalog_df["origin_cohort"] = "jp"
    return catalog_status, raw_catalog_df, source_name


@app.cell
def _(raw_catalog_df):
    raw_catalog_df
    return


@app.cell
def section_1_narrative(mo, raw_catalog_df, source_name):
    mo.md(f"""
    ---

    ## 1. Data Ingestion & Cohort Exploration

    We initiate the analytical pipeline by ingesting the catalog metadata. The active data tier is **`{source_name}`**, comprising **{len(raw_catalog_df):,}** animation entities.
    Each observation is characterized by continuous reception metrics (community rating scores, log-scale popularity counts, and favorites counts), temporal coordinates (season release year), structural distribution parameters (episode volume, episode runtime duration), and discrete categorical genres.

    The interactive controls below parameterize the active cohort filter, sample size $N$, and lower-bound score truncation threshold.
    """)
    return


@app.cell
def ingestion_controls(mo, raw_catalog_df):
    cohort_picker = mo.ui.dropdown(
        options={
            "All Productions (Global)": "all",
            "Japanese Domestic (JP)": "jp",
            "Overseas (Non-JP: Donghua / Aeni)": "non-jp",
        },
        value="All Productions (Global)",
        label="Origin Cohort",
    )

    max_samples = min(10000, max(500, len(raw_catalog_df)))
    step_val = 50 if max_samples <= 5000 else 100
    sample_slider = mo.ui.slider(
        start=50,
        stop=max_samples,
        step=step_val,
        value=min(500, max_samples),
        label="Sample Volume (N)",
    )

    min_score_slider = mo.ui.slider(
        start=0,
        stop=85,
        step=5,
        value=0,
        label="Min Score Filter",
    )
    return cohort_picker, min_score_slider, sample_slider


@app.cell
def display_ingestion_controls(
    catalog_status,
    cohort_picker,
    load_full_db,
    min_score_slider,
    mo,
    raw_catalog_df,
    sample_slider,
    source_name,
):
    cohort_counts = raw_catalog_df["origin_cohort"].value_counts().to_dict()
    jp_n = cohort_counts.get("jp", 0)
    non_jp_n = cohort_counts.get("non-jp", 0)
    callout_kind = "success" if (load_full_db.value and len(raw_catalog_df) >= 10000) else ("warn" if load_full_db.value else "info")

    status_card = mo.callout(
        mo.md(
            f"**Dataset Tier**: `{source_name}`  \n"
            f"**Active Partition**: **{len(raw_catalog_df):,}** entities (**{jp_n:,}** JP Domestic, **{non_jp_n:,}** Overseas Non-JP).  \n"
            f"**Ingestion State**: *{catalog_status}*."
        ),
        kind=callout_kind,
    )

    ingestion_controls_view = mo.vstack(
        [
            mo.hstack([cohort_picker, sample_slider, min_score_slider], justify="start", gap=1.5),
            mo.hstack([load_full_db], justify="start"),
            status_card,
        ],
        gap=1.0,
    )
    ingestion_controls_view
    return


@app.cell
def filter_and_subsample(
    cohort_picker,
    min_score_slider,
    raw_catalog_df,
    sample_slider,
):
    _df = raw_catalog_df.copy()

    # Filter cohort
    _cohort = cohort_picker.value
    if _cohort in ("jp", "non-jp"):
        _df = _df[_df["origin_cohort"] == _cohort]

    # Filter min score
    if min_score_slider.value > 0 and "averageScore" in _df.columns:
        _df = _df[_df["averageScore"] >= min_score_slider.value]

    # Subsample top N by popularity to maintain signal-to-noise ratio
    if "popularity" in _df.columns:
        _df = _df.sort_values(by="popularity", ascending=False)

    df_active = _df.head(sample_slider.value).reset_index(drop=True)
    return (df_active,)


@app.cell
def render_raw_inspection_table(df_active, mo):
    _display_cols = [c for c in ["title", "origin_cohort", "averageScore", "popularity", "seasonYear", "episodes", "duration", "genres"] if c in df_active.columns]

    _summary_banner = mo.hstack([
        mo.stat(value=f"{len(df_active):,}", label="Active Observations", caption="Subsampled Cohort Slice", bordered=True),
        mo.stat(value=f"{df_active['averageScore'].mean():.1f}/100", label="Empirical Mean Score", caption="Continuous Scale", bordered=True),
        mo.stat(value=f"{int(df_active['seasonYear'].median())}", label="Median Release Year", caption=f"Temporal Range {int(df_active['seasonYear'].min())}–{int(df_active['seasonYear'].max())}", bordered=True),
    ], justify="start", gap=1.0)

    _table = mo.ui.table(
        df_active[_display_cols].head(10),
        page_size=5,
    )

    raw_inspection_view = mo.vstack([
        _summary_banner,
        mo.md("#### Empirical Ingested Cohort Sample:"),
        _table,
    ])
    raw_inspection_view
    return


@app.cell
def section_2_narrative(mo):
    mo.md(r"""
    ---
    ## 2. Data Cleaning & Feature Engineering

    Raw animation metadata exhibits substantial heterogeneity across numerical and categorical features:
    1. **Variance-Stabilizing Logarithmic Transformation**: Audience engagement signals ($x_{\text{pop}}$ and $x_{\text{fav}}$) span multiple orders of magnitude ($10^2$ to $10^6$), exhibiting extreme right-skewed power-law characteristics. We apply a natural logarithmic transformation:
       $$\tilde{x} = \ln(1 + x)$$
       to compress scale variance and prevent heavy-tailed outliers from dominating Euclidean distance calculations.
    2. **Standard Score Normalization ($z$-Score Scaling)**: Because feature dimensions possess disparate units (ratings $0-100$, runtime $1-150$ minutes, episode counts $1-500+$), all continuous features are centered and scaled to zero empirical mean and unit empirical variance:
       $$z = \frac{x - \mu}{\sigma}$$
    3. **Sparse Categorical & Lexical Encoding**: Categorical genre indicators are transformed into multi-hot binary vectors. Where available, associated lexical tags are weighted via Term Frequency-Inverse Document Frequency (TF-IDF) vectorization:
       $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

    Tune the lexical feature extraction resolution below:
    """)
    return


@app.cell
def feature_engineering_controls(mo):
    max_tag_features_slider = mo.ui.slider(
        start=10,
        stop=50,
        step=5,
        value=20,
        label="TF-IDF Max Tag Features",
    )
    return (max_tag_features_slider,)


@app.cell
def display_fe_controls(max_tag_features_slider):
    fe_controls_view = max_tag_features_slider
    fe_controls_view
    return


@app.cell
def clean_and_engineer_features(
    StandardScaler,
    TfidfVectorizer,
    df_active,
    max_tag_features_slider,
    np,
):
    _df = df_active.copy()

    # Impute missing values
    _df["averageScore"] = _df["averageScore"].fillna(_df["averageScore"].median() if not _df["averageScore"].empty else 70.0)
    _df["popularity"] = _df["popularity"].fillna(100.0)
    _df["favourites"] = _df["favourites"].fillna(10.0)
    _df["episodes"] = _df["episodes"].fillna(12.0)
    _df["duration"] = _df["duration"].fillna(24.0)
    _df["seasonYear"] = _df["seasonYear"].fillna(2018.0)

    # Feature Engineering
    _df["log_popularity"] = np.log1p(_df["popularity"].clip(lower=0))
    _df["log_favourites"] = np.log1p(_df["favourites"].clip(lower=0))
    _df["log_episodes"] = np.log1p(_df["episodes"].clip(lower=1))

    _min_year = _df["seasonYear"].min()
    _max_year = _df["seasonYear"].max()
    _df["recency"] = (_df["seasonYear"] - _min_year) / max(1.0, (_max_year - _min_year))
    _df["favorites_ratio"] = _df["favourites"] / (_df["popularity"] + 1.0)

    # Continuous feature scaling
    _num_cols = ["averageScore", "log_popularity", "log_favourites", "log_episodes", "duration", "recency", "favorites_ratio"]
    _scaler = StandardScaler()
    _X_num = _scaler.fit_transform(_df[_num_cols].values)

    # Multi-label genre binary matrix
    _all_genres = sorted({g for _r in _df["genres"] if isinstance(_r, list) for g in _r})
    _genre_matrix = np.zeros((len(_df), len(_all_genres)), dtype=np.float32)
    for i, _r in enumerate(_df["genres"]):
        if isinstance(_r, list):
            for g in _r:
                if g in _all_genres:
                    _genre_matrix[i, _all_genres.index(g)] = 1.0

    # Tag TF-IDF
    _tag_texts = []
    for tags_val in _df.get("tags", []):
        if isinstance(tags_val, list):
            names = [t.get("name", "") if isinstance(t, dict) else str(t) for t in tags_val]
            _tag_texts.append(" ".join(names))
        else:
            _tag_texts.append("")

    _tfidf = TfidfVectorizer(max_features=max_tag_features_slider.value, stop_words="english")
    try:
        _X_tags = _tfidf.fit_transform(_tag_texts).toarray()
    except ValueError:
        _X_tags = np.zeros((len(_df), 1), dtype=np.float32)

    # Assemble dense feature matrix X
    engineered_features = np.hstack([_X_num, _genre_matrix, _X_tags])

    # Store genres as readable string for Altair tooltips
    _df["genres_str"] = _df["genres"].apply(lambda g: ", ".join(g) if isinstance(g, list) else "Unknown")

    df_cleaned = _df
    return df_cleaned, engineered_features


@app.cell
def plot_feature_transformation_distributions(alt, df_cleaned, mo):
    chart_raw = (
        alt.Chart(df_cleaned)
        .mark_bar(color="#e74c3c", opacity=0.75)
        .encode(
            x=alt.X("popularity:Q", bin=alt.Bin(maxbins=25), title="Raw Popularity (Heavy-Tailed)"),
            y=alt.Y("count()", title="Title Count"),
        )
        .properties(width=340, height=200, title="Raw Feature Distribution: Exponential Skew")
    )

    chart_log = (
        alt.Chart(df_cleaned)
        .mark_bar(color="#2ecc71", opacity=0.75)
        .encode(
            x=alt.X("log_popularity:Q", bin=alt.Bin(maxbins=25), title="Transformed Popularity: ln(1 + pop)"),
            y=alt.Y("count()", title="Title Count"),
        )
        .properties(width=340, height=200, title="Normalized Distribution: Variance-Stabilized")
    )

    fe_plots_view = mo.vstack([
        mo.md("#### Empirical Feature Distributions Before and After Normalization:"),
        alt.hconcat(chart_raw, chart_log),
    ])
    fe_plots_view
    return


@app.cell
def section_3_narrative(mo):
    mo.md(r"""
    ---
    ## 3. Dimensionality Reduction & Optimal Cluster Selection

    Prior to partitioning the feature space $\mathbf{X} \in \mathbb{R}^{N \times D}$, we evaluate candidate cluster counts $k \in [2, 10]$ across two foundational unsupervised heuristics:
    1. **Within-Cluster Sum of Squares (Inertia / Elbow Heuristic)**:
       $$J(C) = \sum_{k=1}^K \sum_{x_i \in C_k} \| x_i - \mu_k \|^2$$
       Measures total intra-cluster compactness. We evaluate the inflection point (diminishing marginal returns) along the inertia curve.
    2. **Mean Silhouette Coefficient**:
       $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}, \quad s(i) \in [-1, 1]$$
       where $a(i)$ denotes mean intra-cluster distance of sample $i$, and $b(i)$ denotes mean nearest-cluster distance. Higher values reflect dense, well-isolated cluster geometry.
    """)
    return


@app.cell
def evaluate_optimal_k_metrics(
    KMeans,
    engineered_features,
    pd,
    silhouette_score,
):
    _X = engineered_features
    _n = len(_X)

    _k_range = list(range(2, min(10, _n)))
    _inertias = []
    _sil_scores = []

    for _k_val in _k_range:
        _km = KMeans(n_clusters=_k_val, random_state=42, n_init=3)
        _lbls = _km.fit_predict(_X)
        _inertias.append(float(_km.inertia_))

        # Subsample for instant reactivity if n > 1000
        _sil_sub = min(1000, _n)
        _s_score = float(silhouette_score(_X[:_sil_sub], _lbls[:_sil_sub]))
        _sil_scores.append(_s_score)

    k_metrics_df = pd.DataFrame({
        "k": _k_range,
        "inertia": _inertias,
        "silhouette": _sil_scores,
    })

    # Recommended optimal k
    suggested_k = int(k_metrics_df.loc[k_metrics_df["silhouette"].idxmax(), "k"]) if not k_metrics_df.empty else 5
    return k_metrics_df, suggested_k


@app.cell
def plot_diagnostic_curves(alt, k_metrics_df, mo, suggested_k):
    chart_inertia = (
        alt.Chart(k_metrics_df)
        .mark_line(point=True, color="#3498db")
        .encode(
            x=alt.X("k:O", title="Candidate Cluster Count (k)"),
            y=alt.Y("inertia:Q", title="Inertia J(C) [WCSS]"),
            tooltip=["k", "inertia"],
        )
        .properties(width=340, height=220, title="Elbow Inertia Curve")
    )

    chart_sil = (
        alt.Chart(k_metrics_df)
        .mark_bar(color="#9b59b6")
        .encode(
            x=alt.X("k:O", title="Candidate Cluster Count (k)"),
            y=alt.Y("silhouette:Q", title="Mean Silhouette Coefficient"),
            color=alt.condition(
                alt.datum.k == suggested_k,
                alt.value("#e67e22"),  # highlight recommended k
                alt.value("#9b59b6"),
            ),
            tooltip=["k", "silhouette"],
        )
        .properties(width=340, height=220, title=f"Silhouette Optimization (Peak at k = {suggested_k})")
    )

    diagnostic_curves_view = mo.vstack([
        mo.callout(
            f"Empirical silhouette peak identified at k = {suggested_k}. Partitions at this resolution maximize intra-cluster cohesion while preserving inter-cluster separation boundaries.",
            kind="info",
        ),
        alt.hconcat(chart_inertia, chart_sil),
    ])
    diagnostic_curves_view
    return


@app.cell
def section_4_narrative(mo):
    mo.md(r"""
    ---
    ## 4. Unsupervised Clustering & Empirical Archetype Profiling

    We fit $K$-Means clustering to discover canonical archetype centroids and complement the partitioning with Density-Based Spatial Clustering of Applications with Noise (DBSCAN) to identify atypical, sparse outliers:
    - **$K$-Means Objective**: Iteratively minimizes $J(C)$ by assigning observations to the nearest centroid $\mu_k = \frac{1}{|C_k|} \sum_{x_i \in C_k} x_i$.
    - **DBSCAN Density Metric**: Observations with fewer than $\text{min\_samples}$ neighbors within Euclidean radius $\varepsilon$ are classified as noise artifacts ($\text{cluster} = -1$).
    - **Latent Space Decomposition**: Principal Component Analysis (PCA) decomposes the standardized feature covariance matrix:
      $$\mathbf{\Sigma} = \frac{1}{N-1} \mathbf{X}^T \mathbf{X}, \quad \mathbf{\Sigma} \mathbf{w}_j = \lambda_j \mathbf{w}_j$$
      projecting observations onto orthogonal eigenvectors $\mathbf{w}_1, \mathbf{w}_2$ that maximize explained variance.

    Adjust the hyperparameter controls below to inspect parametric sensitivity:
    """)
    return


@app.cell
def clustering_hyperparameter_controls(mo, suggested_k):
    k_slider = mo.ui.slider(
        start=2,
        stop=10,
        step=1,
        value=suggested_k,
        label="Cluster Count (k)",
    )

    eps_slider = mo.ui.slider(
        start=0.6,
        stop=2.5,
        step=0.1,
        value=1.4,
        label="DBSCAN Radius (eps)",
    )
    return eps_slider, k_slider


@app.cell
def display_clustering_controls(eps_slider, k_slider, mo):
    clustering_controls_view = mo.hstack([k_slider, eps_slider], justify="start", gap=1.5)
    clustering_controls_view
    return


@app.cell
def run_clustering_and_pca(
    DBSCAN,
    KMeans,
    PCA,
    df_cleaned,
    engineered_features,
    eps_slider,
    k_slider,
    np,
    pd,
):
    _k = k_slider.value
    _eps = eps_slider.value

    # Fit K-Means
    _km = KMeans(n_clusters=_k, random_state=42, n_init=3)
    _cluster_labels = _km.fit_predict(engineered_features)

    # Fit DBSCAN for noise detection
    _dbscan = DBSCAN(eps=_eps, min_samples=4)
    _dbscan_labels = _dbscan.fit_predict(engineered_features)
    n_noise = int(np.sum(_dbscan_labels == -1))

    # Compute 2D PCA Latent Space Coordinates
    _pca = PCA(n_components=2, random_state=42)
    _X_pca = _pca.fit_transform(engineered_features)
    var_exp = _pca.explained_variance_ratio_

    df_clustered = df_cleaned.copy()
    df_clustered["cluster_id"] = _cluster_labels
    df_clustered["dbscan_id"] = _dbscan_labels
    df_clustered["pca_1"] = np.round(_X_pca[:, 0], 3)
    df_clustered["pca_2"] = np.round(_X_pca[:, 1], 3)

    # Derive Empirical Archetype Names based on centroid characteristics
    _archetype_map = {}
    _profile_rows = []

    for cid in range(_k):
        c_mask = _cluster_labels == cid
        c_df = df_clustered[c_mask]
        c_size = len(c_df)

        mean_score = c_df["averageScore"].mean() if c_size > 0 else 0.0
        mean_pop = c_df["popularity"].mean() if c_size > 0 else 0.0
        med_year = c_df["seasonYear"].median() if c_size > 0 else 2015.0

        # Heuristic archetype taxonomy
        if mean_score >= 82.0 and mean_pop >= 300000:
            arch = "Modern Blockbusters"
        elif mean_score >= 80.0 and med_year <= 2008:
            arch = "Historical Classics"
        elif mean_score >= 80.0 and mean_pop < 200000:
            arch = "Cult Favorites"
        elif mean_pop < 100000 and mean_score < 74.0:
            arch = "Low-Profile Long-Tail"
        elif mean_score >= 75.0:
            arch = "Commercial Mainstream"
        else:
            arch = f"Specialized Cluster {cid}"

        # Collision avoidance
        if arch in _archetype_map.values():
            arch = f"{arch} ({cid})"

        _archetype_map[cid] = arch

        # Exemplars
        top_exemplars = [str(t) for t in c_df.sort_values(by="popularity", ascending=False)["title"].head(3).tolist()]
        exemplar_str = ", ".join(top_exemplars)

        _profile_rows.append({
            "Cluster ID": cid,
            "Archetype Label": arch,
            "Size": c_size,
            "Share (%)": f"{c_size / len(df_clustered) * 100:.1f}%",
            "Mean Score": f"{mean_score:.1f}",
            "Mean Popularity": f"{mean_pop:,.0f}",
            "Median Year": int(med_year),
            "Representative Exemplars": exemplar_str,
        })

    df_clustered["archetype"] = df_clustered["cluster_id"].map(_archetype_map)
    archetype_summary_df = pd.DataFrame(_profile_rows)
    return archetype_summary_df, df_clustered, var_exp


@app.cell
def render_archetype_summary_table(archetype_summary_df, mo):
    archetype_summary_view = mo.vstack([
        mo.md("### Discovered Empirical Archetypes Profile Breakdown:"),
        mo.ui.table(archetype_summary_df, page_size=6),
    ])
    archetype_summary_view
    return


@app.cell
def section_5_narrative(mo, var_exp):
    _pc1 = f"{var_exp[0]*100:.1f}%"
    _pc2 = f"{var_exp[1]*100:.1f}%"
    mo.md(
        r"""
        ---
        ## 5. Interactive Map 

        The figure below projects observations into the two-dimensional principal component subspace $\mathbb{R}^2$ computed via PCA (PC1 accounts for **""" + _pc1 + r"""**, PC2 accounts for **""" + _pc2 + r"""** of latent variance).

        ### Subspace Exploration Instructions:
        - **Hover**: Inspect individual observations with metadata attributes including community rating, popularity, year of release, and genre labels.
        - **Interval Bounding Box**: Click and drag across any continuous coordinate region in the projection manifold to isolate cluster subsets.
        - **Reactive Master-Detail Inspector**: Downstream summary tables dynamically recalculate sample statistics based on the active selection.
        """
    )
    return


@app.cell
def render_altair_interactive_cluster_map(alt, df_clustered, mo):
    # Define interval brush selection linked to downstream reactive inspector
    brush = alt.selection_interval(name="brush")

    chart = (
        alt.Chart(df_clustered)
        .mark_circle(size=85, opacity=0.75)
        .encode(
            x=alt.X("pca_1:Q", title="Principal Component 1 (General Acclaim & Volume)"),
            y=alt.Y("pca_2:Q", title="Principal Component 2 (Format & Tag Specificity)"),
            color=alt.Color(
                "archetype:N",
                title="Discovered Archetype",
                scale=alt.Scale(scheme="category10"),
            ),
            tooltip=[
                alt.Tooltip("title:N", title="Anime Title"),
                alt.Tooltip("archetype:N", title="Archetype"),
                alt.Tooltip("averageScore:Q", title="Score"),
                alt.Tooltip("popularity:Q", title="Popularity", format=","),
                alt.Tooltip("seasonYear:O", title="Year"),
                alt.Tooltip("origin_cohort:N", title="Cohort"),
                alt.Tooltip("genres_str:N", title="Genres"),
            ],
        )
        .add_params(brush)
        .properties(
            width=700,
            height=460,
            title="Latent Space Manifold Map (Interval Brush Selection Enabled)",
        )
        .interactive()
    )

    cluster_map_widget = mo.ui.altair_chart(chart)
    return (cluster_map_widget,)


@app.cell
def display_cluster_map(cluster_map_widget):
    cluster_map_widget
    return


@app.cell
def render_brushed_selection_inspector(cluster_map_widget, df_clustered, mo):
    selected = cluster_map_widget.value

    # If nothing is selected via brush, display default top popular titles
    is_brushed = selected is not None and not selected.empty and len(selected) < len(df_clustered)
    display_df = selected if is_brushed else df_clustered.head(15)

    n_selected = len(display_df)
    mean_selected_score = display_df["averageScore"].mean() if n_selected > 0 else 0.0

    cols = [c for c in ["title", "archetype", "averageScore", "popularity", "seasonYear", "origin_cohort", "genres_str"] if c in display_df.columns]

    status_callout = (
        mo.callout(
            f"Interactive Subspace Selection Active: Inspecting {n_selected} titles partitioned in the brushed latent space region. Empirical Mean Score: {mean_selected_score:.1f}/100.",
            kind="success",
        )
        if is_brushed
        else mo.callout(
            "Click and drag an interval bounding box across any manifold region above to isolate and inspect anime titles in that subspace.",
            kind="info",
        )
    )

    detail_table = mo.ui.table(
        display_df[cols],
        page_size=8,
    )

    inspector_view = mo.vstack([
        status_callout,
        detail_table,
    ])
    inspector_view
    return


@app.cell
def section_6_narrative(mo):
    mo.md(r"""
    ---
    ## 6. Comparative Cross-Market Insights (JP Domestic vs Overseas)

    Treating Chinese Donghua and Korean Aeni as structurally identical to Japanese television broadcast anime introduces significant representation bias into catalog evaluations.
    The bivariate distribution below contrasts **community popularity (logarithmic scale) against rating score** across origin cohorts. Notice the structural differences in audience acquisition patterns and format pacing between domestic broadcast franchises and digital web serials.
    """)
    return


@app.cell
def render_cross_market_comparison(alt, df_clustered, mo):
    if "origin_cohort" in df_clustered.columns and len(df_clustered["origin_cohort"].unique()) > 1:
        comp_chart = (
            alt.Chart(df_clustered)
            .mark_circle(size=70, opacity=0.65)
            .encode(
                x=alt.X("popularity:Q", scale=alt.Scale(type="log"), title="Community Popularity (Logarithmic Scale)"),
                y=alt.Y("averageScore:Q", title="Average Rating Score (0-100)"),
                color=alt.Color("origin_cohort:N", title="Cohort", scale=alt.Scale(domain=["jp", "non-jp"], range=["#3498db", "#e74c3c"])),
                tooltip=["title", "origin_cohort", "averageScore", "popularity"],
            )
            .properties(
                width=700,
                height=300,
                title="Cross-Market Acclaim vs Popularity Divergence",
            )
            .interactive()
        )
        cross_market_view = comp_chart
    else:
        cross_market_view = mo.md("*Select 'All Productions (Global)' in Section 1 to view cross-market cohort contrast.*")
    return (cross_market_view,)


@app.cell
def _(cross_market_view):
    cross_market_view
    return


if __name__ == "__main__":
    app.run()
