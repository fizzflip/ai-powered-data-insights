#!/usr/bin/env python3
"""
Pre-Packaging Pipeline & Catalog Pruner for WebAssembly & Offline Runtimes.

Transforms raw anime catalog stores (SQLite data/anime_catalog.db or Manami
data/anime-offline-database.jsonl) into dual high-performance, compact assets:
1. data/anime_catalog_compact.json.gz (< 2.0 MB target, empirical ~1.14 MB)
2. data/anime_catalog_compact.db      (< 4.0 MB target, empirical ~3.2 MB)

Enforces strict 12-key schema contract and dual-publishing to reports/data/.
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import os
import re
import shutil
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.origin_classifier import AnimeOriginClassifier, classify_anime_origin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("package_catalog")

# Strict 12-key schema contract
REQUIRED_RECORD_KEYS: Set[str] = {
    "id",
    "title",
    "seasonYear",
    "averageScore",
    "popularity",
    "favourites",
    "episodes",
    "duration",
    "genres",
    "tags",
    "origin_cohort",
    "sub_origin",
}

VALID_SUB_ORIGINS: Set[str] = {"JP", "CN", "KR", "WESTERN", "OTHER"}

SUB_ORIGIN_ALIAS_MAP: Dict[str, str] = {
    "TW": "CN",
    "HK": "CN",
    "KP": "KR",
    "US": "WESTERN",
    "GB": "WESTERN",
    "FR": "WESTERN",
    "CA": "WESTERN",
    "DE": "WESTERN",
    "AU": "WESTERN",
    "IT": "WESTERN",
    "ES": "WESTERN",
    "RU": "WESTERN",
}


@dataclass(frozen=True)
class PackagingSummary:
    """Summary metrics of catalog packaging execution."""

    total_records: int
    json_gz_bytes: int
    db_bytes: int
    elapsed_seconds: float
    output_files: List[Path]


def clean_title(
    english: Optional[str],
    romaji: Optional[str],
    fallback: str = "Unknown Title",
    max_length: int = 120,
) -> str:
    """Select and sanitize primary display title."""
    candidate = ""
    if english and isinstance(english, str) and english.strip():
        candidate = english.strip()
    elif romaji and isinstance(romaji, str) and romaji.strip():
        candidate = romaji.strip()
    else:
        candidate = str(fallback).strip() if fallback else "Unknown Title"

    # Normalize whitespace
    cleaned = " ".join(candidate.split())
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()
    return cleaned if cleaned else "Unknown Title"


def parse_genres(raw: Any) -> List[str]:
    """Parse genre list from JSON text, array, or comma-separated string."""
    if not raw:
        return []
    genres: List[str] = []
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("["):
            try:
                items = json.loads(s)
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, str):
                            genres.append(it.strip())
                        elif isinstance(it, dict) and "name" in it:
                            genres.append(str(it["name"]).strip())
            except Exception:
                pass
        elif s:
            genres = [g.strip() for g in s.split(",") if g.strip()]
    elif isinstance(raw, list):
        for it in raw:
            if isinstance(it, str):
                genres.append(it.strip())
            elif isinstance(it, dict) and "name" in it:
                genres.append(str(it["name"]).strip())

    seen: Set[str] = set()
    unique: List[str] = []
    for g in genres:
        if g and g not in seen:
            seen.add(g)
            unique.append(g)
    return unique


def parse_tags(raw: Any, max_tags: int = 6) -> List[str]:
    """Parse tags into list of clean strings capped to max_tags."""
    if not raw:
        return []
    tags: List[str] = []
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("["):
            try:
                items = json.loads(s)
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict) and "name" in it:
                            tags.append(str(it["name"]).strip())
                        elif isinstance(it, str):
                            tags.append(it.strip())
            except Exception:
                pass
        elif s:
            tags = [t.strip() for t in s.split(",") if t.strip()]
    elif isinstance(raw, list):
        for it in raw:
            if isinstance(it, dict) and "name" in it:
                tags.append(str(it["name"]).strip())
            elif isinstance(it, str):
                tags.append(it.strip())

    seen: Set[str] = set()
    unique: List[str] = []
    for t in tags:
        if t and t not in seen:
            seen.add(t)
            unique.append(t)
            if len(unique) >= max_tags:
                break
    return unique


def normalize_score(score: Any) -> Optional[float]:
    """Normalize score to 0.0-100.0 rounded to 1 decimal place."""
    if score is None:
        return None
    try:
        val = float(score)
        if val < 0.0:
            return None
        # Handle 1.0-10.0 scale from raw Manami score fields
        if 0.0 < val <= 10.0:
            val *= 10.0
        val = round(val, 1)
        return max(0.0, min(100.0, val))
    except (ValueError, TypeError):
        return None


def map_sub_origin(country_code: Any, is_jp: int) -> str:
    """Map arbitrary country code to standard 5-cohort sub_origin."""
    if country_code:
        cc = str(country_code).strip().upper()
        if cc in VALID_SUB_ORIGINS:
            return cc
        if cc in SUB_ORIGIN_ALIAS_MAP:
            return SUB_ORIGIN_ALIAS_MAP[cc]
    return "JP" if is_jp == 1 else "OTHER"


def ingest_from_sqlite(db_path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Ingest and project canonical records from SQLite database."""
    logger.info("Ingesting from SQLite: %s", db_path)
    conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT id, external_id, title_romaji, title_english,
               season_year, average_score, popularity, favourites,
               episodes, duration, genres_json, tags_json,
               country_code, is_jp
        FROM anime_records
        ORDER BY popularity DESC
    """
    if limit is not None and limit > 0:
        query += f" LIMIT {int(limit)}"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    records: List[Dict[str, Any]] = []
    seen_ids: Set[int] = set()
    seq_counter = 1

    for row in rows:
        # Determine unique integer ID
        ext_id = row["external_id"]
        rec_id: int
        if ext_id is not None and ext_id > 0:
            rec_id = int(ext_id)
        else:
            raw_id = str(row["id"] or "")
            match = re.search(r"(\d+)$", raw_id)
            if match:
                rec_id = int(match.group(1))
            else:
                rec_id = seq_counter
                seq_counter += 1

        # Prevent duplicate ID collisions in output
        while rec_id in seen_ids:
            rec_id += 1000000
        seen_ids.add(rec_id)

        is_jp_val = 1 if row["is_jp"] == 1 else 0
        origin_cohort = "jp" if is_jp_val == 1 else "non-jp"
        sub_origin = map_sub_origin(row["country_code"], is_jp_val)

        title = clean_title(row["title_english"], row["title_romaji"])
        season_year = int(row["season_year"]) if row["season_year"] is not None else None
        average_score = normalize_score(row["average_score"])
        popularity = int(row["popularity"] or 0)
        favourites = int(row["favourites"] or 0)
        episodes = int(row["episodes"]) if row["episodes"] is not None else None
        duration = int(row["duration"]) if row["duration"] is not None else None

        genres = parse_genres(row["genres_json"])
        tags = parse_tags(row["tags_json"], max_tags=6)

        record = {
            "id": rec_id,
            "title": title,
            "seasonYear": season_year,
            "averageScore": average_score,
            "popularity": popularity,
            "favourites": favourites,
            "episodes": episodes,
            "duration": duration,
            "genres": genres,
            "tags": tags,
            "origin_cohort": origin_cohort,
            "sub_origin": sub_origin,
        }
        records.append(record)

    logger.info("Loaded %d records from SQLite.", len(records))
    return records


def ingest_from_jsonl(jsonl_path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Ingest and project canonical records from JSONL or JSONL.GZ file."""
    logger.info("Ingesting from JSONL: %s", jsonl_path)
    classifier = AnimeOriginClassifier()
    records: List[Dict[str, Any]] = []
    seen_ids: Set[int] = set()
    seq_counter = 1

    opener = gzip.open(jsonl_path, "rt", encoding="utf-8") if str(jsonl_path).endswith(".gz") else open(jsonl_path, "r", encoding="utf-8")

    with opener as f:
        for line in f:
            if limit is not None and len(records) >= limit:
                break
            line_str = line.strip()
            if not line_str or line_str.startswith('{"$schema"'):
                continue
            try:
                raw = json.loads(line_str)
            except Exception:
                continue

            # Classify origin cascade
            origin_res = classifier.classify_record(raw)

            # Determine ID
            rec_id: Optional[int] = None
            sources = raw.get("sources", [])
            for src in sources:
                match = re.search(r"/(?:anime|media)/(\d+)", str(src))
                if match:
                    rec_id = int(match.group(1))
                    break
            if rec_id is None:
                rec_id = seq_counter
                seq_counter += 1

            while rec_id in seen_ids:
                rec_id += 1000000
            seen_ids.add(rec_id)

            title_raw = raw.get("title", "")
            title = clean_title(title_raw, None)

            # Year
            season_obj = raw.get("animeSeason", {})
            season_year = season_obj.get("year") if isinstance(season_obj, dict) else raw.get("seasonYear")
            if season_year is not None:
                try:
                    season_year = int(season_year)
                except (ValueError, TypeError):
                    season_year = None

            # Score
            score_raw = raw.get("score")
            score_val: Optional[float] = None
            if isinstance(score_raw, dict):
                score_val = score_raw.get("arithmeticMean") or score_raw.get("arithmeticGeometricMean")
            else:
                score_val = raw.get("averageScore")
            average_score = normalize_score(score_val)

            popularity = int(raw.get("popularity", 0) or 0)
            favourites = int(raw.get("favourites", 0) or 0)

            episodes = raw.get("episodes")
            if episodes is not None:
                try:
                    episodes = int(episodes)
                except (ValueError, TypeError):
                    episodes = None

            # Duration
            duration_obj = raw.get("duration")
            duration_min: Optional[int] = None
            if isinstance(duration_obj, dict):
                val = duration_obj.get("value")
                unit = str(duration_obj.get("unit", "")).upper()
                if val is not None:
                    try:
                        duration_min = round(float(val) / 60.0) if unit == "SECONDS" else round(float(val))
                    except (ValueError, TypeError):
                        pass
            elif duration_obj is not None:
                try:
                    duration_min = round(float(duration_obj))
                except (ValueError, TypeError):
                    pass

            genres = parse_genres(raw.get("genres"))
            tags = parse_tags(raw.get("tags"), max_tags=6)

            record = {
                "id": rec_id,
                "title": title,
                "seasonYear": season_year,
                "averageScore": average_score,
                "popularity": popularity,
                "favourites": favourites,
                "episodes": episodes,
                "duration": duration_min,
                "genres": genres,
                "tags": tags,
                "origin_cohort": origin_res.origin_cohort,
                "sub_origin": origin_res.sub_origin,
            }
            records.append(record)

    logger.info("Loaded %d records from JSONL.", len(records))
    return records


def validate_records(records: List[Dict[str, Any]]) -> None:
    """Verify that every record matches the strict 12-key schema contract."""
    for idx, rec in enumerate(records):
        keys = set(rec.keys())
        if keys != REQUIRED_RECORD_KEYS:
            missing = REQUIRED_RECORD_KEYS - keys
            extra = keys - REQUIRED_RECORD_KEYS
            raise ValueError(
                f"Record at index {idx} violates schema contract. "
                f"Missing: {missing}, Extra: {extra}"
            )
        assert isinstance(rec["id"], int), f"Record {idx}: id must be int"
        assert isinstance(rec["title"], str), f"Record {idx}: title must be str"
        assert rec["origin_cohort"] in ("jp", "non-jp"), f"Record {idx}: invalid cohort"
        assert rec["sub_origin"] in VALID_SUB_ORIGINS, f"Record {idx}: invalid sub_origin"
        assert isinstance(rec["genres"], list), f"Record {idx}: genres must be list"
        assert isinstance(rec["tags"], list), f"Record {idx}: tags must be list"


def generate_compact_json_gz(records: List[Dict[str, Any]], target_path: Path) -> int:
    """Write compact JSON gzip asset with fixed mtime=0 and compresslevel=9."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    json_bytes = json.dumps(records, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    with open(target_path, "wb") as f_out:
        with gzip.GzipFile(fileobj=f_out, mode="wb", mtime=0, compresslevel=9) as gz:
            gz.write(json_bytes)

    size = target_path.stat().st_size
    logger.info("Generated compact JSON.GZ: %s (%.2f MB)", target_path, size / (1024 * 1024))
    return size


def generate_compact_sqlite_db(records: List[Dict[str, Any]], target_path: Path) -> int:
    """Generate high-performance indexed compact SQLite database."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        target_path.unlink()

    conn = sqlite3.connect(str(target_path.resolve()))
    cur = conn.cursor()

    cur.execute("PRAGMA page_size = 4096;")
    cur.execute("PRAGMA journal_mode = OFF;")
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("PRAGMA locking_mode = EXCLUSIVE;")

    cur.execute("""
        CREATE TABLE anime_records (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            season_year INTEGER,
            average_score REAL,
            popularity INTEGER NOT NULL DEFAULT 0,
            favourites INTEGER NOT NULL DEFAULT 0,
            episodes INTEGER,
            duration INTEGER,
            genres TEXT NOT NULL,
            tags TEXT NOT NULL,
            origin_cohort TEXT NOT NULL,
            sub_origin TEXT NOT NULL,
            seasonYear INTEGER GENERATED ALWAYS AS (season_year) VIRTUAL,
            averageScore REAL GENERATED ALWAYS AS (average_score) VIRTUAL
        );
    """)

    rows = [
        (
            r["id"],
            r["title"],
            r["seasonYear"],
            r["averageScore"],
            r["popularity"],
            r["favourites"],
            r["episodes"],
            r["duration"],
            json.dumps(r["genres"], separators=(",", ":"), ensure_ascii=False),
            json.dumps(r["tags"], separators=(",", ":"), ensure_ascii=False),
            r["origin_cohort"],
            r["sub_origin"],
        )
        for r in records
    ]

    cur.executemany(
        """
        INSERT INTO anime_records (
            id, title, season_year, average_score, popularity, favourites,
            episodes, duration, genres, tags, origin_cohort, sub_origin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    # Required query indexes
    cur.execute("CREATE INDEX idx_compact_pop ON anime_records(popularity DESC);")
    cur.execute("CREATE INDEX idx_compact_score ON anime_records(average_score DESC);")
    cur.execute("CREATE INDEX idx_compact_origin ON anime_records(origin_cohort);")

    conn.commit()

    # Reclaim free pages and enforce physical layout
    cur.execute("PRAGMA journal_mode = DELETE;")
    cur.execute("VACUUM;")
    conn.close()

    size = target_path.stat().st_size
    logger.info("Generated compact SQLite DB: %s (%.2f MB)", target_path, size / (1024 * 1024))
    return size


def package_catalog(
    source_path: Optional[str] = None,
    output_dir: str = "data",
    publish_dir: str = "reports/data",
    limit: Optional[int] = None,
) -> PackagingSummary:
    """Main packaging orchestrator routine."""
    start_time = time.perf_counter()
    repo_root = Path(__file__).resolve().parent.parent

    # Resolve source path
    src_file: Path
    if source_path:
        src_file = Path(source_path)
        if not src_file.is_absolute():
            src_file = repo_root / src_file
    else:
        src_file = repo_root / "data" / "anime_catalog.db"
        if not src_file.exists():
            src_file = repo_root / "data" / "anime-offline-database.jsonl"

    if not src_file.exists():
        raise FileNotFoundError(f"Source catalog file not found: {src_file}")

    # Ingestion branch
    if src_file.suffix in (".db", ".sqlite", ".sqlite3"):
        records = ingest_from_sqlite(src_file, limit=limit)
    else:
        records = ingest_from_jsonl(src_file, limit=limit)

    validate_records(records)

    out_dir_path = repo_root / output_dir if not Path(output_dir).is_absolute() else Path(output_dir)
    pub_dir_path = repo_root / publish_dir if not Path(publish_dir).is_absolute() else Path(publish_dir)

    out_dir_path.mkdir(parents=True, exist_ok=True)
    pub_dir_path.mkdir(parents=True, exist_ok=True)

    json_primary = out_dir_path / "anime_catalog_compact.json.gz"
    db_primary = out_dir_path / "anime_catalog_compact.db"

    json_bytes = generate_compact_json_gz(records, json_primary)
    db_bytes = generate_compact_sqlite_db(records, db_primary)

    # Sync to publish directory
    json_pub = pub_dir_path / "anime_catalog_compact.json.gz"
    db_pub = pub_dir_path / "anime_catalog_compact.db"

    shutil.copy2(json_primary, json_pub)
    shutil.copy2(db_primary, db_pub)

    elapsed = time.perf_counter() - start_time

    # Verify constraints
    json_mb = json_bytes / (1024 * 1024)
    db_mb = db_bytes / (1024 * 1024)
    if json_mb >= 2.0:
        logger.warning("Compact JSON.GZ exceeds 2.0 MB budget: %.2f MB", json_mb)
    if db_mb >= 4.0:
        logger.warning("Compact SQLite DB exceeds 4.0 MB budget: %.2f MB", db_mb)

    summary = PackagingSummary(
        total_records=len(records),
        json_gz_bytes=json_bytes,
        db_bytes=db_bytes,
        elapsed_seconds=elapsed,
        output_files=[json_primary, db_primary, json_pub, db_pub],
    )

    print("\n" + "=" * 70)
    print(" CATALOG PRE-PACKAGING PIPELINE SUMMARY")
    print("=" * 70)
    print(f" Source Catalog:      {src_file}")
    print(f" Records Processed:   {len(records):,}")
    print(f" Compact JSON.GZ:     {json_mb:.2f} MB  (Budget: < 2.00 MB)")
    print(f" Compact SQLite DB:   {db_mb:.2f} MB  (Budget: < 4.00 MB)")
    print(f" Primary Directory:   {out_dir_path}")
    print(f" Publish Directory:   {pub_dir_path}")
    print(f" Execution Time:      {elapsed:.2f} seconds")
    print(f" Acceptance Status:   {'PASSED' if (json_mb < 2.0 and db_mb < 4.0) else 'FAILED'}")
    print("=" * 70 + "\n")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Package anime catalog into compact WebAssembly and offline assets."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Path to source SQLite catalog (.db) or JSONL file (default: data/anime_catalog.db or data/anime-offline-database.jsonl).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Primary output directory for compact assets.",
    )
    parser.add_argument(
        "--publish-dir",
        type=str,
        default="reports/data",
        help="Publishing directory for static dashboard / web assets.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional record limit for testing or benchmarks.",
    )
    args = parser.parse_args()

    try:
        package_catalog(
            source_path=args.source,
            output_dir=args.output_dir,
            publish_dir=args.publish_dir,
            limit=args.limit,
        )
    except Exception as err:
        logger.error("Catalog packaging failed: %s", err, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
