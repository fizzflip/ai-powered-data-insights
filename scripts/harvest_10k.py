#!/usr/bin/env python3
"""
High-Throughput Parallel Anime Harvester & Re-Analysis Pipeline.

Expands the local SQLite incremental database to >= 10,000 unique records:
1. Spawns parallel workers for AniList and Kitsu APIs with independent rate limiters.
2. Strictly respects rate limit ceilings (< 20 req/min per endpoint via >= 3.3s delay).
3. Maximizes per-query yield (AniList: 50 items/batch, Kitsu: 20 items/batch).
4. Handles multi-sort AniList harvesting (POPULARITY_DESC, SCORE_DESC, FAVOURITES_DESC).
5. Thoroughly deduplicates records across and within sources upon completion.
6. Synchronizes to portable JSON cache and executes adaptive clustering re-analysis.
"""

from __future__ import annotations

import argparse
import datetime
import logging
import os
import queue
import sys
import threading
import time
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import AnimeCatalogDB
from src.data_fetcher import AniListGraphQLClient, KitsuFetcher
from src.pipeline import AnimePipeline, PipelineConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("parallel_harvester")


class ParallelAnimeHarvester:
    """Coordinates parallel ingestion from AniList and Kitsu into SQLite."""

    def __init__(
        self,
        db: AnimeCatalogDB,
        target_records: int = 10000,
        rate_delay: float = 3.3,
    ):
        self.db = db
        self.target_records = target_records
        self.rate_delay = max(3.0, rate_delay)  # Guarantee < 20 req/min
        self.stop_event = threading.Event()
        self.write_lock = threading.Lock()
        self.batch_queue: queue.Queue = queue.Queue(maxsize=100)

        self.anilist_client = AniListGraphQLClient(rate_limit_delay=self.rate_delay)
        self.kitsu_client = KitsuFetcher(rate_limit_delay=self.rate_delay)

        self.stats = {
            "anilist_batches": 0,
            "anilist_items": 0,
            "kitsu_batches": 0,
            "kitsu_items": 0,
            "start_time": time.time(),
        }

    def anilist_worker(self) -> None:
        """Worker thread for AniList GraphQL endpoint."""
        logger.info("AniList Worker started (rate delay: %.1fs)...", self.rate_delay)
        sort_plans = [
            ("ID", 1, 100),
            ("ID_DESC", 1, 100),
            ("EPISODES_DESC", 1, 100),
            ("TRENDING_DESC", 1, 100),
            ("UPDATED_AT_DESC", 1, 100),
            ("POPULARITY_DESC", self.db.get_fetch_page("anilist"), 100),
            ("SCORE_DESC", 1, 100),
            ("FAVOURITES_DESC", 1, 100),
            ("START_DATE_DESC", 1, 100),
        ]

        try:
            for sort_name, start_p, max_p in sort_plans:
                if self.stop_event.is_set():
                    break

                logger.info("AniList Worker: switching to sort '%s' (pages %d..%d)...",
                            sort_name, start_p, max_p)

                page = start_p
                while page <= max_p and not self.stop_event.is_set():
                    req_start = time.time()
                    data = self.anilist_client.query_page(
                        page=page,
                        per_page=50,
                        sort=[sort_name],
                    )

                    if not data or "data" not in data or "Page" not in data["data"]:
                        logger.warning("AniList page %d (%s) returned empty/error. Advancing sort.",
                                       page, sort_name)
                        break

                    page_info = data["data"]["Page"]
                    media = page_info.get("media", [])
                    if not media:
                        logger.info("AniList sort '%s' exhausted at page %d.", sort_name, page)
                        break

                    for m in media:
                        if isinstance(m, dict):
                            m["source_api"] = "anilist"

                    with self.write_lock:
                        inserted, updated = self.db.upsert_records(media, source_api="anilist")
                        self.stats["anilist_batches"] += 1
                        self.stats["anilist_items"] += len(media)
                        current_total = self.db.count_records()

                    logger.info(
                        "AniList [%s p.%d/50]: +%d (ins:%d, upd:%d) -> DB Total: %d / %d",
                        sort_name, page, len(media), inserted, updated, current_total, self.target_records,
                    )

                    # Check if stop event requested by coordinator
                    if self.stop_event.is_set():
                        break

                    if not page_info.get("pageInfo", {}).get("hasNextPage", False):
                        break

                    page += 1
                    elapsed = time.time() - req_start
                    sleep_time = max(0.0, self.rate_delay - elapsed)
                    time.sleep(sleep_time)

        except Exception as e:
            logger.error("Exception in AniList Worker: %s", e)

        logger.info("AniList Worker concluded.")

    def kitsu_worker(self) -> None:
        """Worker thread for Kitsu JSON:API endpoint."""
        logger.info("Kitsu Worker started (rate delay: %.1fs)...", self.rate_delay)
        start_offset = (self.db.get_fetch_page("kitsu") - 1) * 20
        offset = start_offset
        max_offset = 22480  # Kitsu has ~22,481 anime

        try:
            while offset <= max_offset and not self.stop_event.is_set():
                req_start = time.time()
                items = self.kitsu_client.query_page(offset=offset, limit=20)

                if not items:
                    logger.info("Kitsu returned no items at offset %d. Concluding Kitsu worker.", offset)
                    break

                for it in items:
                    if isinstance(it, dict):
                        it["source_api"] = "kitsu"

                with self.write_lock:
                    inserted, updated = self.db.upsert_records(items, source_api="kitsu")
                    self.stats["kitsu_batches"] += 1
                    self.stats["kitsu_items"] += len(items)
                    page_num = (offset // 20) + 1
                    self.db.update_fetch_page("kitsu", page_num, len(items))
                    current_total = self.db.count_records()

                logger.info(
                    "Kitsu [offset %d/20]: +%d (ins:%d, upd:%d) -> DB Total: %d / %d",
                    offset, len(items), inserted, updated, current_total, self.target_records,
                )

                if self.stop_event.is_set():
                    break

                offset += len(items)
                elapsed = time.time() - req_start
                sleep_time = max(0.0, self.rate_delay - elapsed)
                time.sleep(sleep_time)

        except Exception as e:
            logger.error("Exception in Kitsu Worker: %s", e)

        logger.info("Kitsu Worker concluded.")

    def run(self) -> int:
        """Execute parallel harvest until target is reached or APIs are exhausted."""
        # 1. Initial deduplication of any preexisting legacy IDs
        logger.info("Running initial database deduplication pass...")
        initial_stats = self.db.thorough_deduplicate()
        logger.info("Initial deduplication: %s", initial_stats)

        current_count = self.db.count_records()
        logger.info("Starting harvest: current clean DB count = %d, target = %d",
                    current_count, self.target_records)

        if current_count >= self.target_records:
            logger.info("Current DB count (%d) already satisfies target (%d).",
                        current_count, self.target_records)
            return current_count

        # 2. Launch concurrent threads for AniList and Kitsu
        t_anilist = threading.Thread(target=self.anilist_worker, name="AniListWorker", daemon=True)
        t_kitsu = threading.Thread(target=self.kitsu_worker, name="KitsuWorker", daemon=True)

        t_anilist.start()
        t_kitsu.start()

        # Wait for workers to complete or reach clean deduplicated target
        last_dedup_time = time.time()
        while (t_anilist.is_alive() or t_kitsu.is_alive()) and not self.stop_event.is_set():
            time.sleep(2.0)
            now = time.time()
            # Periodically deduplicate and check clean record count
            if (now - last_dedup_time >= 25.0) or (self.db.count_records() >= self.target_records + 200):
                with self.write_lock:
                    dedup_check = self.db.thorough_deduplicate()
                clean_count = self.db.count_records()
                last_dedup_time = now
                logger.info(
                    "Periodic dedup check: clean unique count = %d / %d (pruned in check: %d)",
                    clean_count, self.target_records, dedup_check.get("total_pruned", 0),
                )
                if clean_count >= self.target_records:
                    logger.info("Clean deduplicated count reached target (%d >= %d). Stopping workers.",
                                clean_count, self.target_records)
                    self.stop_event.set()
                    break

        t_anilist.join(timeout=10.0)
        t_kitsu.join(timeout=10.0)

        # 3. Final thorough deduplication
        logger.info("Harvest phase finished. Running thorough deduplication across all sources...")
        dedup_stats = self.db.thorough_deduplicate()
        final_count = self.db.count_records()

        elapsed = time.time() - self.stats["start_time"]
        logger.info("=== Harvest Completed in %.1fs ===", elapsed)
        logger.info("Final Clean Unique Anime in SQLite: %d", final_count)
        logger.info("Deduplication Summary: %s", dedup_stats)
        logger.info(
            "AniList: %d queries, %d items | Kitsu: %d queries, %d items",
            self.stats["anilist_batches"], self.stats["anilist_items"],
            self.stats["kitsu_batches"], self.stats["kitsu_items"],
        )

        # 4. Synchronize to JSON cache for offline portability
        self.db.export_to_json("data/raw_anime_data.json")
        return final_count


def run_pipeline_reanalysis(adaptive_k: bool = True) -> None:
    """Run full clustering and visualization pipeline on expanded catalog."""
    logger.info("=== Starting Pipeline Re-Analysis on Expanded Catalog ===")
    config = PipelineConfig(
        num_samples=30000,  # Process all available DB records
        offline_mode=True,  # Work directly from populated local database
        adaptive_k=adaptive_k,
    )
    pipeline = AnimePipeline(config=config)
    pipeline.run()
    logger.info("=== Pipeline Re-Analysis Completed Successfully ===")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parallel Anime Harvester (>= 10,000 entries) & Adaptive Re-Analysis",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=10000,
        help="Target number of unique anime entries in local database (default: 10000)",
    )
    parser.add_argument(
        "--rate-delay",
        type=float,
        default=3.3,
        help="Inter-request delay per API worker in seconds (default: 3.3s = 18.18 req/min)",
    )
    parser.add_argument(
        "--no-reanalyse",
        action="store_true",
        help="Skip clustering re-analysis after harvesting",
    )
    parser.add_argument(
        "--adaptive-k",
        action="store_true",
        default=True,
        help="Enable adaptive k-range selection during re-analysis (default: True)",
    )

    args = parser.parse_args()

    db = AnimeCatalogDB()
    harvester = ParallelAnimeHarvester(
        db=db,
        target_records=args.target,
        rate_delay=args.rate_delay,
    )
    final_count = harvester.run()

    if not args.no_reanalyse:
        run_pipeline_reanalysis(adaptive_k=args.adaptive_k)

    print(f"\n=======================================================")
    print(f" PARALLEL HARVEST & RE-ANALYSIS COMPLETED")
    print(f" Total Unique Anime in SQLite: {final_count}")
    print(f" Target Goal: {args.target}")
    print(f" Goal Satisfied: {'YES' if final_count >= args.target else 'NO (APIs Exhausted)'}")
    print(f"=======================================================\n")


if __name__ == "__main__":
    main()
