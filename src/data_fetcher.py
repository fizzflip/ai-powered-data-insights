"""
Multi-Source Data Fetcher & Incremental Ingestion Module.

Fetches anime metadata from:
1. Primary: AniList GraphQL API (https://graphql.anilist.co)
2. Secondary Fallback: Kitsu REST API (https://kitsu.io/api/edge/anime)
3. Offline Local: SQLite Incremental Database (data/anime_catalog.db)
4. Static Fallback: Built-in 55-item curated mock dataset

Features rate limiting to prevent API bans, incremental pagination resumption,
and automatic synchronization to data/raw_anime_data.json.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from src.database import AnimeCatalogDB

logger = logging.getLogger("data_fetcher")


# Re-export curated built-in mock dataset from dedicated domain module
from src.mock_data import MOCK_ANIME_DATA


# ---------------------------------------------------------------------------
# AniList GraphQL Query Definition
# ---------------------------------------------------------------------------
ANILIST_GRAPHQL_QUERY = """
query ($page: Int, $perPage: Int, $sort: [MediaSort] = [POPULARITY_DESC]) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      total
      currentPage
      lastPage
      hasNextPage
      perPage
    }
    media(type: ANIME, sort: $sort) {
      id
      countryOfOrigin
      title {
        romaji
        english
        native
      }
      seasonYear
      season
      episodes
      duration
      genres
      tags {
        name
        rank
        isMediaSpoiler
      }
      studios(isMain: true) {
        nodes {
          name
          isAnimationStudio
        }
      }
      source
      averageScore
      popularity
      favourites
    }
  }
}
"""


class AniListGraphQLClient:
    """Fetcher for AniList GraphQL API with rate limiting and retry handling."""

    ANILIST_API_URL = "https://graphql.anilist.co"
    PAGE_SIZE = 50

    def __init__(
        self,
        rate_limit_delay: float = 0.5,
        max_retries: int = 3,
        timeout: int = 15,
    ):
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AnimeInsights/1.0 (DataSciencePipeline)",
            }
        )

    def query_page(
        self,
        page: int,
        per_page: int,
        sort: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Query a single page from AniList with backoff."""
        variables: Dict[str, Any] = {"page": page, "perPage": per_page}
        if sort:
            variables["sort"] = sort
        payload = {
            "query": ANILIST_GRAPHQL_QUERY,
            "variables": variables,
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    self.ANILIST_API_URL,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    if remaining is not None and int(remaining) < 10:
                        logger.warning(
                            "AniList rate limit low (%s left), cooling down for 2s...",
                            remaining,
                        )
                        time.sleep(2.0)
                    return data

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(
                        "HTTP 429 from AniList. Cooling down for %ds (attempt %d/%d)...",
                        retry_after,
                        attempt,
                        self.max_retries,
                    )
                    time.sleep(retry_after)
                    continue

                logger.warning(
                    "AniList HTTP %d: %s", response.status_code, response.text[:150]
                )
                time.sleep(1.0 * attempt)

            except requests.RequestException as e:
                logger.warning("AniList request exception on page %d: %s", page, e)
                time.sleep(1.5 * attempt)

        return None


class KitsuFetcher:
    """
    Secondary fallback fetcher for Kitsu JSON:API (https://kitsu.io/api/edge/anime).
    Maps Kitsu anime attributes into canonical schema.
    """

    KITSU_API_URL = "https://kitsu.io/api/edge/anime"
    PAGE_SIZE = 20

    def __init__(
        self,
        rate_limit_delay: float = 0.5,
        max_retries: int = 3,
        timeout: int = 15,
    ):
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.api+json",
                "User-Agent": "AnimeInsights/1.0 (DataSciencePipeline)",
            }
        )

    def query_page(
        self, offset: int = 0, limit: int = 20
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch a page from Kitsu and map into canonical schema."""
        params = {
            "page[offset]": offset,
            "page[limit]": limit,
            "sort": "-userCount",
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    self.KITSU_API_URL,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("data", [])
                    return [self._map_kitsu_item(it) for it in items]

                if response.status_code == 429:
                    time.sleep(3.0 * attempt)
                    continue

                time.sleep(1.0 * attempt)

            except requests.RequestException as e:
                logger.warning("Kitsu request exception: %s", e)
                time.sleep(1.5 * attempt)

        return None

    @staticmethod
    def _map_kitsu_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw Kitsu attributes to canonical anime schema."""
        attrs = item.get("attributes", {})
        date_str = attrs.get("startDate") or "2020-01-01"
        try:
            year = int(date_str.split("-")[0])
            month = int(date_str.split("-")[1]) if len(date_str.split("-")) > 1 else 1
        except Exception:
            year = 2020
            month = 1

        season = (
            "WINTER"
            if month <= 3
            else "SPRING"
            if month <= 6
            else "SUMMER"
            if month <= 9
            else "FALL"
        )
        titles = attrs.get("titles", {}) or {}
        canon_title = attrs.get("canonicalTitle") or "Unknown Title"
        english_title = titles.get("en") or titles.get("en_us") or canon_title
        romaji_title = titles.get("en_jp") or canon_title

        subtype = attrs.get("subtype", "TV")
        genre_label = subtype.capitalize() if subtype else "Anime"

        return {
            "id": int(item.get("id", 0)),
            "title": {"romaji": romaji_title, "english": english_title},
            "seasonYear": year,
            "season": season,
            "episodes": attrs.get("episodeCount") or 12,
            "duration": attrs.get("episodeLength") or 24,
            "genres": [genre_label, "Animation"],
            "tags": [
                {
                    "name": attrs.get("showType", "TV"),
                    "rank": 80,
                    "isMediaSpoiler": False,
                }
            ],
            "studios": {"nodes": []},
            "source": "MANGA" if subtype == "TV" else "ORIGINAL",
            "averageScore": float(attrs.get("averageRating") or 70.0),
            "popularity": int(attrs.get("userCount") or 1000),
            "favourites": int(attrs.get("favoritesCount") or 50),
        }


class MultiSourceFetcher:
    """
    Unified multi-source ingestion coordinator.
    Chains Primary (AniList) -> Secondary (Kitsu) -> Local SQLite DB -> Static Mock,
    enforcing slow rate-limiting to prevent bans and incremental accumulation.
    """

    def __init__(
        self,
        db: Optional[AnimeCatalogDB] = None,
        cache_json_path: Optional[str] = None,
        cache_path: Optional[str] = None,
        rate_limit_delay: float = 0.6,
    ):
        chosen_path = cache_path or cache_json_path or "data/raw_anime_data.json"
        self.cache_json_path = chosen_path
        self.cache_path = chosen_path
        self._custom_cache = bool(cache_path or cache_json_path)
        self.db = db or AnimeCatalogDB()
        self.rate_limit_delay = rate_limit_delay
        self.anilist = AniListGraphQLClient(rate_limit_delay=rate_limit_delay)
        self.kitsu = KitsuFetcher(rate_limit_delay=rate_limit_delay)

        # On initial boot, import existing JSON into SQLite if DB is empty
        if self.db.count_records() == 0 and os.path.exists(self.cache_json_path):
            self.db.import_from_json(self.cache_json_path, source_api="anilist")

    def save_cache(self, records: List[Dict[str, Any]]) -> None:
        """Save records directly to the JSON cache file."""
        target_path = os.path.abspath(self.cache_json_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    def load_cache(self) -> Optional[List[Dict[str, Any]]]:
        """Load records from the JSON cache file if it exists."""
        target_path = os.path.abspath(self.cache_json_path)
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception:
                pass
        return None

    def fetch_anime_data(
        self,
        limit: int = 500,
        preferred_source: str = "auto",
        force_fetch: bool = False,
        offline: bool = False,
        incremental: bool = True,
        origin: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve anime records with incremental database management and multi-source fallbacks.

        :param limit: Desired number of records.
        :param preferred_source: 'auto' (AniList -> Kitsu), 'anilist', or 'kitsu'.
        :param force_fetch: Bypass existing DB and fetch new records from API.
        :param offline: Run purely offline from SQLite database or mock.
        :param incremental: Resume from last fetched page/offset without duplicating.
        :param origin: Origin filter: 'jp', 'non-jp', or specific country code (e.g. 'CN', 'KR').
        """
        # 1. Offline Mode: Return existing DB records or mock
        if offline:
            # If custom cache was set and exists
            cached = self.load_cache()
            if cached is not None and len(cached) > 0:
                if origin:
                    from src.origin_classifier import classify_anime_origin

                    norm_o = str(origin).strip().lower()
                    filtered = []
                    for c in cached:
                        cohort = c.get("origin_cohort")
                        if not cohort:
                            res = classify_anime_origin(c)
                            cohort = res.origin_cohort
                        if norm_o in ("jp", "japan") and cohort == "jp":
                            filtered.append(c)
                        elif norm_o in ("non-jp", "non_jp") and cohort == "non-jp":
                            filtered.append(c)
                        elif norm_o not in ("all", "*"):
                            sub = c.get("sub_origin")
                            if sub and sub.upper() == origin.strip().upper():
                                filtered.append(c)
                    return filtered[:limit]
                return cached[:limit]

            if not self._custom_cache:
                db_count = self.db.count_records(origin=origin)
                if db_count > 0:
                    logger.info(
                        "Offline mode: loaded %d records from SQLite incremental database (origin=%s).",
                        min(db_count, limit),
                        origin,
                    )
                    return self.db.get_all_records(limit=limit, origin=origin)
            logger.info("Offline mode: using built-in mock dataset.")
            return MOCK_ANIME_DATA[:limit]

        # 2. Check if local DB already has sufficient records and force_fetch is False
        db_count = self.db.count_records(origin=origin)
        if not force_fetch and db_count >= limit:
            logger.info(
                "Local database satisfies request (%d cached records >= %d requested, origin=%s).",
                db_count,
                limit,
                origin,
            )
            return self.db.get_all_records(limit=limit, origin=origin)

        records_needed = limit if force_fetch else max(0, limit - db_count)
        logger.info(
            "Fetching %d additional records (current DB count: %d, target: %d)...",
            records_needed,
            db_count,
            limit,
        )

        fetched_records: List[Dict[str, Any]] = []

        # 3. Source Strategy: Try AniList unless Kitsu explicitly requested
        if preferred_source in ("auto", "anilist"):
            fetched_records = self._fetch_from_anilist(
                records_needed, incremental=incremental
            )

        # 4. Fallback to Kitsu if AniList returned insufficient data
        if len(fetched_records) < records_needed and preferred_source in (
            "auto",
            "kitsu",
        ):
            remaining = records_needed - len(fetched_records)
            logger.info(
                "Attempting secondary source (Kitsu) for %d records...", remaining
            )
            kitsu_records = self._fetch_from_kitsu(remaining, incremental=incremental)
            fetched_records.extend(kitsu_records)

        # 5. Persist fetched records into SQLite & sync cache if missing
        if fetched_records:
            default_src = "anilist" if preferred_source == "auto" else preferred_source
            self.db.upsert_records(fetched_records, source_api=default_src)
            if not os.path.exists(self.cache_json_path) and not os.path.exists(self.cache_json_path + ".gz"):
                self.db.export_to_json(self.cache_json_path)

        total_db = self.db.count_records()
        if total_db > 0:
            return self.db.get_all_records(limit=limit)

        # Fallback to mock if nothing in DB
        return MOCK_ANIME_DATA[:limit]

    def _fetch_from_anilist(
        self, count: int, incremental: bool = True
    ) -> List[Dict[str, Any]]:
        """Fetch records from AniList with polite pagination."""
        start_page = self.db.get_fetch_page("anilist") if incremental else 1
        page = start_page
        results: List[Dict[str, Any]] = []
        per_page = min(50, count)

        try:
            while len(results) < count:
                batch_size = min(per_page, count - len(results))
                logger.info(
                    "AniList: requesting page %d (batch: %d)...", page, batch_size
                )
                data = self.anilist.query_page(page, batch_size)

                if not data or "data" not in data or "Page" not in data["data"]:
                    logger.warning(
                        "AniList page %d returned invalid data. Ending AniList fetch.",
                        page,
                    )
                    break

                page_info = data["data"]["Page"]
                media = page_info.get("media", [])
                if not media:
                    break

                for m in media:
                    if isinstance(m, dict):
                        m["source_api"] = "anilist"
                results.extend(media)
                self.db.update_fetch_page("anilist", page, len(media))

                if not page_info.get("pageInfo", {}).get("hasNextPage", False):
                    break

                page += 1
                time.sleep(self.rate_limit_delay)

        except Exception as e:
            logger.error("Exception during AniList fetch: %s", e)

        return results

    def _fetch_from_kitsu(
        self, count: int, incremental: bool = True
    ) -> List[Dict[str, Any]]:
        """Fetch records from Kitsu with polite pagination."""
        start_offset = (self.db.get_fetch_page("kitsu") - 1) * 20 if incremental else 0
        offset = start_offset
        results: List[Dict[str, Any]] = []

        try:
            while len(results) < count:
                batch_size = min(20, count - len(results))
                logger.info(
                    "Kitsu: requesting offset %d (limit: %d)...", offset, batch_size
                )
                items = self.kitsu.query_page(offset=offset, limit=batch_size)

                if not items:
                    break

                for it in items:
                    if isinstance(it, dict):
                        it["source_api"] = "kitsu"
                results.extend(items)
                page_num = (offset // 20) + 1
                self.db.update_fetch_page("kitsu", page_num, len(items))

                if len(items) < batch_size:
                    break

                offset += len(items)
                time.sleep(self.rate_limit_delay)

        except Exception as e:
            logger.error("Exception during Kitsu fetch: %s", e)

        return results


# Backward compatibility alias
AniListFetcher = MultiSourceFetcher
