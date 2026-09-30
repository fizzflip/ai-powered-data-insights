#!/usr/bin/env python3
"""
CLI entry point for the Anime Unsupervised Clustering & Insights project.

Features:
- Multi-source ingestion: AniList GraphQL + Kitsu JSON:API fallback.
- Incremental SQLite catalog database (data/anime_catalog.db) with JSON export sync.
- Polite rate-limit throttling to prevent API bans during large dataset crawls.
- Robust preprocessing, TF-IDF tag extraction, and continuous feature scaling.
- Unsupervised clustering with strict empirical archetype profiling.
- Latent space projections (PCA 2D/3D, t-SNE) and markdown findings reporting.
"""

import argparse
import logging
import os
import sys

# Ensure headless matplotlib backend before any visualizer import
os.environ["MPLBACKEND"] = "Agg"

from src.pipeline import InsightsPipeline, PipelineConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Anime Unsupervised Clustering, Multi-Source Ingestion & Empirical Archetype Discovery",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=500,
        help="Target number of anime records to retrieve/analyze",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of K-Means clusters (set to 0 for automatic detection based on silhouette score)",
    )
    parser.add_argument(
        "--min-k",
        type=int,
        default=None,
        help="Minimum cluster count for Elbow and Silhouette evaluation (default: 2 or adaptive)",
    )
    parser.add_argument(
        "--max-k",
        type=int,
        default=None,
        help="Maximum cluster count for Elbow and Silhouette evaluation (default: 10 or adaptive)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="auto",
        choices=["auto", "anilist", "kitsu"],
        help="API data source: 'auto' (AniList -> Kitsu fallback), 'anilist', or 'kitsu'",
    )
    parser.add_argument(
        "--rate-delay",
        type=float,
        default=0.6,
        help="Polite inter-request delay in seconds to avoid API rate limits and bans",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/anime_catalog.db",
        help="Path to SQLite persistent incremental database",
    )
    parser.add_argument(
        "--dbscan-eps",
        type=float,
        default=1.2,
        help="DBSCAN epsilon neighborhood distance radius",
    )
    parser.add_argument(
        "--dbscan-min-samples",
        type=int,
        default=4,
        help="DBSCAN minimum samples per core cluster",
    )
    parser.add_argument(
        "--force-fetch",
        action="store_true",
        help="Ignore local cache and fetch fresh data from APIs",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run completely offline using SQLite database or mock fallback",
    )
    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Do not resume from last pagination cursor (restart pagination from page 1)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Directory to save analysis report and generated figures",
    )
    parser.add_argument(
        "--adaptive-k",
        action="store_true",
        help="Dynamically scale candidate [min_k, max_k] and determine optimal k based on database sample size N",
    )
    parser.add_argument(
        "--run-scaling-steps",
        action="store_true",
        help="Execute multi-step incremental database scaling benchmark and generate progression report",
    )
    parser.add_argument(
        "--step-samples",
        type=str,
        default="150,600,1998",
        help="Comma-separated sample sizes for multi-step scaling demonstration",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable figure generation (fast text-only mode)",
    )
    parser.add_argument(
        "--parallel-harvest",
        action="store_true",
        help="Run high-throughput parallel harvesting (AniList + Kitsu) to reach target sample volume",
    )
    parser.add_argument(
        "--deduplicate",
        action="store_true",
        help="Run thorough cross-source and internal deduplication on database and export to JSON",
    )
    parser.add_argument(
        "--ingest-offline-db",
        nargs="?",
        const="data/anime-offline-database.jsonl",
        default=None,
        metavar="JSONL_PATH",
        help="Ingest Manami offline database JSONL into SQLite (mappings, relations, and catalog records)",
    )
    parser.add_argument(
        "--use-offline-db",
        action="store_true",
        help="Prioritize SQLite offline indexed database without querying external APIs",
    )

    return parser.parse_args()


def main() -> int:
    """Execute main CLI workflow."""
    args = parse_arguments()

    if args.run_scaling_steps:
        from scripts.demonstrate_scaling import run_incremental_scaling_demonstration
        try:
            sample_steps = [int(s.strip()) for s in args.step_samples.split(",") if s.strip()]
        except ValueError as e:
            logger.error("Invalid format for --step-samples. Expected comma-separated integers, got %r: %s", args.step_samples, e)
            return 1
        return run_incremental_scaling_demonstration(
            sample_steps=sample_steps,
            output_dir=args.output_dir,
        )

    if args.ingest_offline_db:
        from src.database import AnimeCatalogDB
        from src.offline_indexer import OfflineIndexer

        db = AnimeCatalogDB(args.db_path)
        indexer = OfflineIndexer(db)
        stats = indexer.index_file(args.ingest_offline_db, insert_unrepresented=True)

        print("\n" + "=" * 65)
        print(" OFFLINE DATABASE INGESTION COMPLETED")
        print("=" * 65)
        print(f"File processed: {stats['file_path']}")
        print(f"Total anime items parsed: {stats['total_items_processed']}")
        print(f"External platform mappings indexed: {stats['external_mappings_indexed']}")
        print(f"Franchise relationship edges indexed: {stats['relations_indexed']}")
        print(f"Initial catalog size: {stats['initial_catalog_records']}")
        print(f"New anime records added: {stats['new_records_added']}")
        print(f"Total anime in catalog: {stats['final_catalog_records']}")
        print(f"Duration: {stats['elapsed_seconds']}s")
        print("=" * 65 + "\n")

        if args.deduplicate:
            dedup_stats = db.thorough_deduplicate()
            db.export_to_json("data/raw_anime_data.json")
            print(f"Deduplication completed: {dedup_stats}")
        return 0

    if args.deduplicate:
        from src.database import AnimeCatalogDB
        db = AnimeCatalogDB(args.db_path)
        stats = db.thorough_deduplicate()
        db.export_to_json("data/raw_anime_data.json")
        logger.info("Deduplication completed: %s", stats)
        return 0

    if args.parallel_harvest:
        from scripts.harvest_10k import ParallelAnimeHarvester, run_pipeline_reanalysis
        from src.database import AnimeCatalogDB
        db = AnimeCatalogDB(args.db_path)
        harvester = ParallelAnimeHarvester(
            db=db,
            target_records=args.samples,
            rate_delay=args.rate_delay,
        )
        final_count = harvester.run()
        if not args.no_plots:
            run_pipeline_reanalysis(adaptive_k=args.adaptive_k)
        return 0

    figures_dir = os.path.join(args.output_dir, "figures")
    k_param = None if (args.k == 0 or args.adaptive_k) else args.k

    config = PipelineConfig(
        num_samples=args.samples,
        k=k_param,
        min_k=args.min_k,
        max_k=args.max_k,
        adaptive_k=args.adaptive_k or args.k == 0,
        preferred_source=args.source,
        rate_limit_delay=args.rate_delay,
        db_path=args.db_path,
        dbscan_eps=args.dbscan_eps,
        dbscan_min_samples=args.dbscan_min_samples,
        cache_path="data/raw_anime_data.json",
        output_dir=args.output_dir,
        figures_dir=figures_dir,
        force_fetch=args.force_fetch,
        offline_mode=args.offline or args.use_offline_db,
        incremental=not args.no_incremental,
        generate_plots=not args.no_plots,
    )

    try:
        pipeline = InsightsPipeline(config)
        results = pipeline.run()

        print("\n" + "=" * 65)
        print(" PIPELINE EXECUTION COMPLETED")
        print("=" * 65)
        print(f"Total anime analyzed: {results['num_samples']}")
        print(f"Total in SQLite database: {results['db_total_count']}")
        print(f"Cluster count: {results['k_optimal']}")
        print("Empirical Archetypes Discovered:")
        for cid, arch in results["archetype_labels"].items():
            print(f"  • Cluster {cid}: {arch}")
        print(f"DBSCAN: {results['dbscan_clusters']} dense clusters, {results['dbscan_noise']} noise points")
        if results.get("figure_paths"):
            print(f"Generated {len(results['figure_paths'])} visualization figures in: {figures_dir}")
        print(f"Detailed analytical report saved to: {results['report_path']}")
        print("=" * 65 + "\n")
        return 0

    except Exception as e:
        logger.exception("Fatal error in pipeline execution: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
