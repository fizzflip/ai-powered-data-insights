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
import sqlite3
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
        """Create a connection with row factory configured."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
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
        raw_id = record.get("id")
        return f"{source_api.lower()}:{raw_id}"

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
                canon_id = self._normalize_record_id(rec, source_api)
                ext_id = int(rec.get("id", 0))

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
                        source_api,
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

        query = f"SELECT raw_json FROM anime_records ORDER BY {order_clause}"
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
                    records.append(json.loads(row["raw_json"]))
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
