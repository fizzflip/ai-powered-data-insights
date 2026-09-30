#!/usr/bin/env python3
"""
CLI Runner for High-Throughput Parallel Anime Harvesting.
Imports production harvesting engine from src.harvester.
"""

from __future__ import annotations

import argparse
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import AnimeCatalogDB
from src.harvester import ParallelAnimeHarvester, run_pipeline_reanalysis


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

    print("\n=======================================================")
    print(" PARALLEL HARVEST & RE-ANALYSIS COMPLETED")
    print(f" Total Unique Anime in SQLite: {final_count}")
    print(f" Target Goal: {args.target}")
    print(f" Goal Satisfied: {'YES' if final_count >= args.target else 'NO (APIs Exhausted)'}")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
