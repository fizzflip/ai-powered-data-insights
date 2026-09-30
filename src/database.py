"""
SQLite Incremental Database Module for Anime Catalog.

Manages persistent local storage of anime metadata, deduplication by canonical ID,
incremental pagination resumption, slow rate-throttling buffers, and automatic
synchronization to data/raw_anime_data.json for offline portability.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import re
import sqlite3
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("database")


class AnimeCatalogDB:
    """
    Persistent SQLite storage engine for incremental anime records.
    Provides schema migration, deduplication, incremental merging,
    and bi-directional export/import with JSON caches.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(root_dir, "data", "anime_catalog.db")
        else:
            self.db_path = os.path.abspath(db_path)

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a connection with row factory, WAL mode, and busy timeout configured."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        return conn

    def _init_db(self) -> None:
        """Initialize database schema if not present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS anime_records (
                    id TEXT PRIMARY KEY,
                    source_api TEXT NOT NULL,
                    external_id INTEGER NOT NULL,
                    title_romaji TEXT,
                    title_english TEXT,
                    season_year INTEGER,
                    season TEXT,
                    episodes INTEGER,
                    duration INTEGER,
                    genres_json TEXT,
                    tags_json TEXT,
                    studios_json TEXT,
                    source_material TEXT,
                    average_score REAL,
                    popularity INTEGER,
                    favourites INTEGER,
                    raw_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS fetch_state (
                    source_api TEXT PRIMARY KEY,
                    last_page INTEGER DEFAULT 1,
                    total_fetched INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_anime_pop ON anime_records(popularity DESC);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_anime_score ON anime_records(average_score DESC);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_anime_year ON anime_records(season_year DESC);"
            )
            conn.commit()
        logger.debug("Initialized SQLite database at %s", self.db_path)

    @staticmethod
    def _normalize_record_id(record: Dict[str, Any], source_api: str) -> str:
        """Construct canonical composite ID for deduplication."""
        src = str(record.get("source_api") or source_api).lower()
        if src == "api":
            src = "anilist"
        raw_id = record.get("id")
        return f"{src}:{raw_id}"

    @staticmethod
    def clean_title(title: Optional[str]) -> str:
        """Normalize anime title for robust deduplication across sources."""
        if not title:
            return ""
        t = unicodedata.normalize("NFKC", str(title)).lower()
        t = re.sub(
            r"[\(\[\{]\s*(?:tv|ova|ona|movie|special|the animation|part\s*\d+|\d{4})\s*[\)\]\}]",
            " ",
            t,
            flags=re.IGNORECASE,
        )
        t = re.sub(
            r"\b(the\s+animation|tv|ova|ona|movie|special)\b",
            " ",
            t,
            flags=re.IGNORECASE,
        )
        t = re.sub(r"[^a-z0-9\s]", " ", t)
        return " ".join(t.split())

    def thorough_deduplicate(self) -> Dict[str, int]:
        """
        Perform thorough cross-source and internal deduplication:
        1. Consolidate legacy 'api:' prefix IDs into 'anilist:' canonical IDs.
        2. Detect and merge cross-source records (e.g. AniList vs Kitsu) matching on
           canonical normalized title, release year, and episode count.
        3. Prune redundant duplicate rows while preserving the richest metadata.
        """
        initial_count = self.count_records()
        consolidated_ids = 0
        cross_source_merged = 0

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Step 1: Consolidate legacy 'api:' prefix IDs
            cursor.execute(
                "SELECT id, external_id FROM anime_records WHERE source_api = 'api' OR id LIKE 'api:%'"
            )
            api_rows = cursor.fetchall()
            for row in api_rows:
                old_id = row["id"]
                ext_id = row["external_id"]
                canon_id = f"anilist:{ext_id}"

                cursor.execute("SELECT id FROM anime_records WHERE id = ?", (canon_id,))
                exists = cursor.fetchone()
                if exists:
                    cursor.execute("DELETE FROM anime_records WHERE id = ?", (old_id,))
                    consolidated_ids += 1
                else:
                    cursor.execute(
                        "UPDATE anime_records SET id = ?, source_api = 'anilist' WHERE id = ?",
                        (canon_id, old_id),
                    )
                    consolidated_ids += 1
            conn.commit()

            # Step 2: Cross-source title + year deduplication (e.g. AniList vs Kitsu)
            cursor.execute(
                "SELECT id, source_api, external_id, title_romaji, title_english, "
                "season_year, episodes, average_score, popularity, raw_json FROM anime_records"
            )
            all_rows = cursor.fetchall()

            primary_index: Dict[Tuple[str, int, int], str] = {}
            primary_title_year: Dict[Tuple[str, int], str] = {}

            for r in all_rows:
                if r["source_api"] == "anilist":
                    y = r["season_year"] or 0
                    ep = r["episodes"] or 0
                    for t_raw in (r["title_romaji"], r["title_english"]):
                        t_clean = self.clean_title(t_raw)
                        if len(t_clean) >= 4:
                            primary_title_year[(t_clean, y)] = r["id"]
                            if ep > 0:
                                primary_index[(t_clean, y, ep)] = r["id"]

            to_delete_ids = []
            for r in all_rows:
                if r["source_api"] != "anilist":
                    y = r["season_year"] or 0
                    ep = r["episodes"] or 0
                    matched_primary_id = None
                    for t_raw in (r["title_romaji"], r["title_english"]):
                        t_clean = self.clean_title(t_raw)
                        if len(t_clean) >= 4:
                            if ep > 0 and (t_clean, y, ep) in primary_index:
                                matched_primary_id = primary_index[(t_clean, y, ep)]
                                break
                            elif (t_clean, y) in primary_title_year:
                                matched_primary_id = primary_title_year[(t_clean, y)]
                                break
                    if matched_primary_id and matched_primary_id != r["id"]:
                        to_delete_ids.append(r["id"])

            for del_id in to_delete_ids:
                cursor.execute("DELETE FROM anime_records WHERE id = ?", (del_id,))
                cross_source_merged += 1

            conn.commit()

        final_count = self.count_records()
        stats = {
            "initial_count": initial_count,
            "legacy_ids_consolidated": consolidated_ids,
            "cross_source_merged": cross_source_merged,
            "total_pruned": initial_count - final_count,
            "final_count": final_count,
        }
        logger.info("Thorough deduplication complete: %s", stats)
        return stats

    def upsert_records(
        self,
        records: List[Dict[str, Any]],
        source_api: str = "anilist",
    ) -> Tuple[int, int]:
        """
        Insert or update a list of canonical anime records.

        :param records: List of anime dictionary objects.
        :param source_api: Name of the originating source ('anilist', 'kitsu', 'mock').
        :return: (inserted_count, updated_count)
        """
        if not records:
            return (0, 0)

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        inserted = 0
        updated = 0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            for rec in records:
                rec_src = str(rec.get("source_api") or source_api)
                canon_id = self._normalize_record_id(rec, rec_src)
                ext_id = int(rec.get("id") or 0)

                title = rec.get("title", {})
                if isinstance(title, dict):
                    t_romaji = title.get("romaji")
                    t_english = title.get("english")
                else:
                    t_romaji = str(title)
                    t_english = str(title)

                genres = rec.get("genres", [])
                tags = rec.get("tags", [])
                studios = rec.get("studios", {})

                # Check if already exists
                cursor.execute("SELECT id FROM anime_records WHERE id = ?", (canon_id,))
                exists = cursor.fetchone() is not None

                genres_str = json.dumps(genres if isinstance(genres, list) else [])
                tags_str = json.dumps(tags if isinstance(tags, list) else [])
                studios_str = json.dumps(studios if isinstance(studios, (dict, list)) else {})
                raw_str = json.dumps(rec, ensure_ascii=False)

                cursor.execute(
                    """
                    INSERT INTO anime_records (
                        id, source_api, external_id, title_romaji, title_english,
                        season_year, season, episodes, duration, genres_json,
                        tags_json, studios_json, source_material, average_score,
                        popularity, favourites, raw_json, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        title_romaji=excluded.title_romaji,
                        title_english=excluded.title_english,
                        season_year=excluded.season_year,
                        season=excluded.season,
                        episodes=excluded.episodes,
                        duration=excluded.duration,
                        genres_json=excluded.genres_json,
                        tags_json=excluded.tags_json,
                        studios_json=excluded.studios_json,
                        source_material=excluded.source_material,
                        average_score=excluded.average_score,
                        popularity=excluded.popularity,
                        favourites=excluded.favourites,
                        raw_json=excluded.raw_json,
                        updated_at=excluded.updated_at;
                    """,
                    (
                        canon_id,
                        rec_src,
                        ext_id,
                        t_romaji,
                        t_english,
                        rec.get("seasonYear"),
                        rec.get("season"),
                        rec.get("episodes"),
                        rec.get("duration"),
                        genres_str,
                        tags_str,
                        studios_str,
                        rec.get("source"),
                        rec.get("averageScore"),
                        rec.get("popularity"),
                        rec.get("favourites"),
                        raw_str,
                        now,
                    ),
                )
                if exists:
                    updated += 1
                else:
                    inserted += 1

            conn.commit()

        logger.info(
            "Upserted %d records to SQLite (inserted: %d, updated: %d). Total in DB: %d",
            len(records),
            inserted,
            updated,
            self.count_records(),
        )
        return (inserted, updated)

    def count_records(self) -> int:
        """Count total anime records in database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM anime_records")
            return cursor.fetchone()[0]

    def get_all_records(
        self,
        limit: Optional[int] = None,
        sort_by: str = "popularity DESC",
    ) -> List[Dict[str, Any]]:
        """
        Retrieve records from database parsed into canonical dictionaries.

        :param limit: Maximum number of records to return.
        :param sort_by: SQL sort order (e.g. 'popularity DESC', 'average_score DESC').
        :return: List of canonical anime dictionaries.
        """
        valid_sorts = {
            "popularity DESC": "popularity DESC",
            "popularity ASC": "popularity ASC",
            "average_score DESC": "average_score DESC",
            "season_year DESC": "season_year DESC",
        }
        order_clause = valid_sorts.get(sort_by, "popularity DESC")

        query = f"SELECT raw_json, source_api FROM anime_records ORDER BY {order_clause}"
        params: List[Any] = []
        if limit is not None and limit > 0:
            query += " LIMIT ?"
            params.append(limit)

        records: List[Dict[str, Any]] = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                try:
                    item = json.loads(row["raw_json"])
                    if isinstance(item, dict):
                        item["source_api"] = row["source_api"]
                    records.append(item)
                except json.JSONDecodeError:
                    continue

        return records

    def export_to_json(self, json_path: str = "data/raw_anime_data.json") -> int:
        """Export all current records to portable JSON file for offline demonstration."""
        records = self.get_all_records()
        if not records:
            return 0

        target_file = os.path.abspath(json_path)
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        logger.info("Exported %d records from SQLite to %s", len(records), target_file)
        return len(records)

    def import_from_json(
        self,
        json_path: str = "data/raw_anime_data.json",
        source_api: str = "anilist",
    ) -> int:
        """Import existing JSON records into SQLite if database is empty."""
        target_file = os.path.abspath(json_path)
        if not os.path.exists(target_file):
            return 0

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                inserted, updated = self.upsert_records(data, source_api=source_api)
                logger.info(
                    "Imported %d existing records from %s into SQLite.",
                    len(data),
                    target_file,
                )
                return len(data)
        except Exception as e:
            logger.warning("Could not import from JSON %s: %s", target_file, e)
        return 0

    def get_fetch_page(self, source_api: str = "anilist") -> int:
        """Get the next page to fetch for incremental pagination."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT last_page FROM fetch_state WHERE source_api = ?",
                (source_api,),
            )
            row = cursor.fetchone()
            if row:
                return int(row["last_page"]) + 1
            return 1

    def update_fetch_page(
        self,
        source_api: str,
        page: int,
        batch_size: int,
    ) -> None:
        """Update last fetched page cursor for incremental resumption."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO fetch_state (source_api, last_page, total_fetched, last_updated)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(source_api) DO UPDATE SET
                    last_page = excluded.last_page,
                    total_fetched = fetch_state.total_fetched + excluded.total_fetched,
                    last_updated = excluded.last_updated;
                """,
                (source_api, page, batch_size, now),
            )
            conn.commit()
