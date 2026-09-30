"""
Offline Database Ingestion & Relational Indexer Module.

Ingests the Manami Project Anime Offline Database (data/anime-offline-database.jsonl)
containing 41,000+ anime records. Builds high-performance universal ID crosswalks
(AniList, MyAnimeList, Kitsu, AniDB) and directed relationship graphs for franchise
deduplication and feature engineering without external API rate limits.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from src.database import AnimeCatalogDB
from src.origin_classifier import OriginClassifier

logger = logging.getLogger("offline_indexer")

# Standard anime genres recognized in machine learning feature sets
KNOWN_GENRES = {
    "Action",
    "Adventure",
    "Comedy",
    "Drama",
    "Fantasy",
    "Horror",
    "Mecha",
    "Music",
    "Mystery",
    "Psychological",
    "Romance",
    "Sci-Fi",
    "Slice of Life",
    "Sports",
    "Supernatural",
    "Thriller",
}
KNOWN_GENRES_LOWER = {g.lower(): g for g in KNOWN_GENRES}


class OfflineIndexer:
    """
    Ingests and indexes offline anime database files into SQLite.
    Populates:
    1. external_mappings: universal cross-platform ID crosswalk
    2. anime_relations: franchise relationship edges
    3. anime_records: unrepresented anime catalog entries
    """

    PATTERNS = {
        "anilist": re.compile(r"anilist\.co/anime/(\d+)"),
        "myanimelist": re.compile(r"myanimelist\.net/anime/(\d+)"),
        "kitsu": re.compile(r"kitsu\.(?:app|io)/anime/(\d+)"),
        "anidb": re.compile(r"anidb\.net/anime/(\d+)"),
        "animeplanet": re.compile(r"anime-planet\.com/anime/([^/]+)"),
        "anisearch": re.compile(r"anisearch\.com/anime/(\d+)"),
        "livechart": re.compile(r"livechart\.me/anime/(\d+)"),
    }

    def __init__(
        self,
        db: Optional[AnimeCatalogDB] = None,
        origin_classifier: Optional[OriginClassifier] = None,
    ):
        self.db = db or AnimeCatalogDB()
        self.origin_classifier = origin_classifier or OriginClassifier()

    def _extract_site_id(self, url: str) -> Optional[Tuple[str, str]]:
        """Extract (site, external_id) from URL."""
        for site, pattern in self.PATTERNS.items():
            m = pattern.search(url)
            if m:
                return (site, m.group(1))
        return None

    def _determine_canonical_id(
        self, sources: List[str], line_idx: int
    ) -> Tuple[str, str, int, List[Tuple[str, str]]]:
        """
        Determine canonical composite ID and extract all external platform mappings.
        Priority: anilist > myanimelist > kitsu > anidb > manami
        Returns: (canonical_id, primary_source, primary_ext_id, mappings)
        """
        mappings: List[Tuple[str, str]] = []
        site_map: Dict[str, str] = {}

        for url in sources:
            parsed = self._extract_site_id(url)
            if parsed:
                site, ext_id = parsed
                mappings.append((site, ext_id))
                if site not in site_map:
                    site_map[site] = ext_id

        if "anilist" in site_map:
            ext_int = (
                int(site_map["anilist"]) if site_map["anilist"].isdigit() else line_idx
            )
            return f"anilist:{site_map['anilist']}", "anilist", ext_int, mappings
        elif "myanimelist" in site_map:
            ext_int = (
                int(site_map["myanimelist"])
                if site_map["myanimelist"].isdigit()
                else line_idx
            )
            return (
                f"myanimelist:{site_map['myanimelist']}",
                "myanimelist",
                ext_int,
                mappings,
            )
        elif "kitsu" in site_map:
            ext_int = (
                int(site_map["kitsu"]) if site_map["kitsu"].isdigit() else line_idx
            )
            return f"kitsu:{site_map['kitsu']}", "kitsu", ext_int, mappings
        elif "anidb" in site_map:
            ext_int = (
                int(site_map["anidb"]) if site_map["anidb"].isdigit() else line_idx
            )
            return f"anidb:{site_map['anidb']}", "anidb", ext_int, mappings
        else:
            return f"manami:{line_idx}", "manami", line_idx, mappings

    @staticmethod
    def _convert_manami_to_record(
        item: Dict[str, Any],
        canon_id: str,
        source_api: str,
        external_id: int,
    ) -> Dict[str, Any]:
        """Convert a raw manami JSONL item into canonical anime record dictionary."""
        title_str = str(item.get("title") or "")
        synonyms = item.get("synonyms") or []
        english_title = title_str
        if synonyms and isinstance(synonyms, list) and len(synonyms) > 0:
            english_title = str(synonyms[0])

        anime_season = item.get("animeSeason") or {}
        season_year = anime_season.get("year")
        season = anime_season.get("season") or "UNKNOWN"

        episodes = item.get("episodes") or 1
        duration_obj = item.get("duration") or {}
        duration_val = duration_obj.get("value") or 24
        duration_unit = str(duration_obj.get("unit") or "MINUTES").upper()
        if duration_unit == "SECONDS":
            duration_mins = max(1, round(duration_val / 60))
        else:
            duration_mins = int(duration_val)

        # Extract genres from tags
        raw_tags = item.get("tags") or []
        genres: List[str] = []
        tags_objs: List[Dict[str, Any]] = []
        for t in raw_tags:
            t_str = str(t)
            t_lower = t_str.lower()
            if t_lower in KNOWN_GENRES_LOWER:
                genres.append(KNOWN_GENRES_LOWER[t_lower])
            tags_objs.append({"name": t_str, "rank": 80, "isMediaSpoiler": False})
        if not genres:
            genres = [item.get("type", "Animation").capitalize()]

        studios_raw = item.get("studios") or []
        studios = {
            "nodes": [
                {"name": str(s).title(), "isAnimationStudio": True} for s in studios_raw
            ]
        }

        # Score conversion: 1.0 - 10.0 scale -> 0.0 - 100.0 scale
        score_obj = item.get("score") or {}
        arith_mean = score_obj.get("arithmeticMean")
        if arith_mean is not None:
            average_score = round(float(arith_mean) * 10, 1)
        else:
            average_score = 65.0

        media_type = item.get("type", "UNKNOWN")

        return {
            "id": external_id,
            "source_api": source_api,
            "title": {"romaji": title_str, "english": english_title},
            "seasonYear": season_year,
            "season": season,
            "episodes": episodes,
            "duration": duration_mins,
            "genres": genres,
            "tags": tags_objs,
            "studios": studios,
            "source": media_type,
            "averageScore": average_score,
            "popularity": 1000,
            "favourites": 50,
        }

    def index_file(
        self,
        jsonl_path: str = "data/anime-offline-database.jsonl",
        max_records: Optional[int] = None,
        insert_unrepresented: bool = True,
        batch_size: int = 5000,
    ) -> Dict[str, Any]:
        """
        Stream and ingest the offline database JSONL file.
        Pass 1: Build URL-to-canonical ID index for relationship resolution.
        Pass 2: Ingest external_mappings, anime_relations, and unrepresented anime_records.
        """
        abs_path = os.path.abspath(jsonl_path)
        if not os.path.exists(abs_path):
            if os.path.exists(abs_path + ".gz"):
                abs_path = abs_path + ".gz"
            elif abs_path.endswith(".gz") and os.path.exists(abs_path[:-3]):
                abs_path = abs_path[:-3]
            else:
                raise FileNotFoundError(f"Offline database file not found at: {abs_path}")

        t0 = time.time()
        logger.info("Starting offline database indexing from: %s", abs_path)

        url_to_canon: Dict[str, str] = {}
        items_metadata: List[
            Tuple[int, Dict[str, Any], str, str, int, List[Tuple[str, str]]]
        ] = []

        line_count = 0
        open_fn = (
            lambda p: gzip.open(p, "rt", encoding="utf-8")
            if p.endswith(".gz")
            else open(p, "r", encoding="utf-8")
        )
        with open_fn(abs_path) as f:
            first_line = f.readline()
            try:
                header = json.loads(first_line)
                if "$schema" in header or "license" in header:
                    pass
                else:
                    # Not a header, treat as record
                    item = header
                    cid, src, eid, mappings = self._determine_canonical_id(
                        item.get("sources", []), 1
                    )
                    for s in item.get("sources", []):
                        url_to_canon[s] = cid
                    items_metadata.append((1, item, cid, src, eid, mappings))
                    line_count = 1
            except Exception:
                pass

            for line in f:
                line_count += 1
                if max_records and line_count > max_records:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue

                sources = item.get("sources", [])
                cid, src, eid, mappings = self._determine_canonical_id(
                    sources, line_count
                )
                for s in sources:
                    url_to_canon[s] = cid
                items_metadata.append((line_count, item, cid, src, eid, mappings))

        t_pass1 = time.time()
        logger.info(
            "Pass 1 complete in %.2fs: Indexed %d URL mappings across %d records.",
            t_pass1 - t0,
            len(url_to_canon),
            len(items_metadata),
        )

        # Pass 2: Ingest mappings, relations, and records
        initial_records_count = self.db.count_records()
        total_mappings_inserted = 0
        total_relations_inserted = 0
        new_records_added = 0

        # We will use direct SQLite transaction batching for maximum throughput
        with self.db._get_connection() as conn:
            cursor = conn.cursor()

            mappings_batch: List[Tuple[str, str, str]] = []
            relations_batch: List[Tuple[str, str, str, str]] = []
            records_batch: List[Tuple[Any, ...]] = []

            for line_idx, item, cid, src, eid, mappings in items_metadata:
                # 1. External mappings
                for site, ext_id in mappings:
                    mappings_batch.append((cid, site, ext_id))
                # Also include intrinsic mapping
                mappings_batch.append((cid, src, str(eid)))

                # 2. Anime relations
                related = item.get("relatedAnime", [])
                for rel_url in related:
                    if rel_url in url_to_canon:
                        target_cid = url_to_canon[rel_url]
                        if target_cid != cid:
                            relations_batch.append(
                                (cid, target_cid, "related", "manami")
                            )
                            relations_batch.append(
                                (target_cid, cid, "related", "manami")
                            )

                # 3. Unrepresented anime records
                if insert_unrepresented:
                    rec = self._convert_manami_to_record(item, cid, src, eid)
                    res = self.origin_classifier.classify(rec)
                    country_code = res.sub_origin
                    is_jp = res.is_jp
                    raw_str = json.dumps(rec, ensure_ascii=False)
                    title_romaji = rec["title"]["romaji"]
                    title_english = rec["title"]["english"]
                    genres_str = json.dumps(rec["genres"])
                    tags_str = json.dumps(rec["tags"])
                    studios_str = json.dumps(rec["studios"])

                    records_batch.append(
                        (
                            cid,
                            src,
                            eid,
                            title_romaji,
                            title_english,
                            rec["seasonYear"],
                            rec["season"],
                            rec["episodes"],
                            rec["duration"],
                            genres_str,
                            tags_str,
                            studios_str,
                            rec["source"],
                            rec["averageScore"],
                            rec["popularity"],
                            rec["favourites"],
                            raw_str,
                            country_code,
                            is_jp,
                        )
                    )

                if len(mappings_batch) >= batch_size:
                    cursor.executemany(
                        "INSERT OR IGNORE INTO external_mappings (anime_id, external_site, external_id) VALUES (?, ?, ?)",
                        mappings_batch,
                    )
                    total_mappings_inserted += len(mappings_batch)
                    mappings_batch.clear()

                if len(relations_batch) >= batch_size:
                    cursor.executemany(
                        "INSERT OR IGNORE INTO anime_relations (source_id, target_id, relation_type, source_api) VALUES (?, ?, ?, ?)",
                        relations_batch,
                    )
                    total_relations_inserted += len(relations_batch)
                    relations_batch.clear()

                if len(records_batch) >= batch_size:
                    cursor.executemany(
                        """
                        INSERT OR IGNORE INTO anime_records (
                            id, source_api, external_id, title_romaji, title_english,
                            season_year, season, episodes, duration, genres_json,
                            tags_json, studios_json, source_material, average_score,
                            popularity, favourites, raw_json, country_code, is_jp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        records_batch,
                    )
                    records_batch.clear()

            # Flush remaining batches
            if mappings_batch:
                cursor.executemany(
                    "INSERT OR IGNORE INTO external_mappings (anime_id, external_site, external_id) VALUES (?, ?, ?)",
                    mappings_batch,
                )
                total_mappings_inserted += len(mappings_batch)

            if relations_batch:
                cursor.executemany(
                    "INSERT OR IGNORE INTO anime_relations (source_id, target_id, relation_type, source_api) VALUES (?, ?, ?, ?)",
                    relations_batch,
                )
                total_relations_inserted += len(relations_batch)

            if records_batch:
                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO anime_records (
                        id, source_api, external_id, title_romaji, title_english,
                        season_year, season, episodes, duration, genres_json,
                        tags_json, studios_json, source_material, average_score,
                        popularity, favourites, raw_json, country_code, is_jp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    records_batch,
                )

            conn.commit()

        final_records_count = self.db.count_records()
        new_records_added = final_records_count - initial_records_count
        elapsed = time.time() - t0

        stats = {
            "file_path": abs_path,
            "total_items_processed": len(items_metadata),
            "external_mappings_indexed": total_mappings_inserted,
            "relations_indexed": total_relations_inserted,
            "initial_catalog_records": initial_records_count,
            "new_records_added": new_records_added,
            "final_catalog_records": final_records_count,
            "elapsed_seconds": round(elapsed, 2),
        }
        logger.info("Offline database indexing complete: %s", stats)
        return stats
