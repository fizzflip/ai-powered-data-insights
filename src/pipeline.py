"""
Pipeline Orchestration Module for Anime Unsupervised Clustering.

Coordinates end-to-end data acquisition (AniList + Kitsu fallback + SQLite DB),
preprocessing, unsupervised clustering with strict empirical archetype profiling,
visualization generation, and markdown findings reporting.
"""

from __future__ import annotations

import concurrent.futures
import copy
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd

from src.clustering import AnimeClusterer, ClusteringResult
from src.comparative_visualizer import ComparativeVisualizer
from src.data_fetcher import MultiSourceFetcher
from src.database import AnimeCatalogDB
from src.preprocessor import DataPreprocessor, PreprocessedData
from src.visualizer import ClusterVisualizer

logger = logging.getLogger("pipeline")
from src.report_builder import generate_cluster_report, generate_comparative_report, _extract_exemplars_for_df, _compute_genre_proportions, _generate_comparative_report


@dataclass
class PipelineConfig:
    """Configuration settings for the anime clustering pipeline."""

    num_samples: int = 500
    k: Optional[int] = 5
    min_k: Optional[int] = None
    max_k: Optional[int] = None
    adaptive_k: bool = False
    dbscan_eps: float = 1.2
    dbscan_min_samples: int = 4
    cache_path: str = "data/raw_anime_data.json"
    db_path: str = "data/anime_catalog.db"
    preferred_source: str = "auto"
    rate_limit_delay: float = 0.6
    output_dir: str = "reports"
    figures_dir: Optional[str] = None
    force_fetch: bool = False
    offline_mode: bool = False
    incremental: bool = True
    generate_plots: bool = True
    origin: str = "all"  # 'all', 'jp', 'non-jp', 'compare'
    dpi: int = 150


class InsightsPipeline:
    """End-to-end pipeline orchestrator for anime archetype discovery."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()

        # Dynamic figure directory resolution based on origin cohort
        if self.config.figures_dir is None:
            norm_o = str(self.config.origin).strip().lower()
            if norm_o in ("jp", "japan"):
                self.config.figures_dir = os.path.join(
                    self.config.output_dir, "figures_jp"
                )
            elif norm_o in ("non-jp", "non_jp", "international"):
                self.config.figures_dir = os.path.join(
                    self.config.output_dir, "figures_non_jp"
                )
            else:
                self.config.figures_dir = os.path.join(
                    self.config.output_dir, "figures"
                )

        self.db = AnimeCatalogDB(db_path=self.config.db_path)
        self.fetcher = MultiSourceFetcher(
            db=self.db,
            cache_json_path=self.config.cache_path,
            rate_limit_delay=self.config.rate_limit_delay,
        )
        self.preprocessor = DataPreprocessor(
            max_tag_features=35,
            min_tag_df=2,
        )
        self.clusterer = AnimeClusterer()
        self.visualizer = ClusterVisualizer(random_state=42, dpi=self.config.dpi)

    def run(self) -> Dict[str, Any]:
        """Execute all stages of the clustering pipeline."""
        if str(self.config.origin).strip().lower() == "compare":
            return run_comparative_pipeline(self.config)

        logger.info(
            "=== Starting Anime Insights Pipeline (Cohort: %s) ===", self.config.origin
        )
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(self.config.figures_dir, exist_ok=True)

        # Stage 1: Multi-Source Data Acquisition & Incremental Ingestion
        logger.info(
            "Stage 1: Fetching anime records (target: %d, source: %s, offline: %s, origin: %s)...",
            self.config.num_samples,
            self.config.preferred_source,
            self.config.offline_mode,
            self.config.origin,
        )
        raw_data = self.fetcher.fetch_anime_data(
            limit=self.config.num_samples,
            preferred_source=self.config.preferred_source,
            force_fetch=self.config.force_fetch,
            offline=self.config.offline_mode,
            incremental=self.config.incremental,
            origin=self.config.origin if self.config.origin != "all" else None,
        )
        db_count = self.db.count_records()
        logger.info(
            "Acquired %d records for pipeline. Total in SQLite DB: %d.",
            len(raw_data),
            db_count,
        )

        df_raw = pd.DataFrame(raw_data)

        # Stage 2: Data Preprocessing & Feature Engineering
        logger.info("Stage 2: Preprocessing and feature engineering...")
        preprocessed: PreprocessedData = self.preprocessor.fit_transform(df_raw)
        logger.info(
            "Feature matrix assembled: Shape %s across %d features.",
            preprocessed.X.shape,
            len(preprocessed.feature_names),
        )

        # Stage 3: Unsupervised Clustering & Adaptive Cluster Scaling
        from src.clustering import compute_adaptive_k_range

        use_adaptive = (
            self.config.adaptive_k or self.config.k == 0 or self.config.k is None
        )
        cluster_k = None if use_adaptive else self.config.k

        if use_adaptive:
            calc_min, calc_max, target_k = compute_adaptive_k_range(len(df_raw))
            eff_min = self.config.min_k if self.config.min_k is not None else calc_min
            eff_max = self.config.max_k if self.config.max_k is not None else calc_max
            logger.info(
                "Adaptive k-selection enabled: candidate range [%d, %d] (target anchor: %d) for N=%d records.",
                eff_min,
                eff_max,
                target_k,
                len(df_raw),
            )
        else:
            eff_min = self.config.min_k if self.config.min_k is not None else 2
            eff_max = self.config.max_k if self.config.max_k is not None else 10

        logger.info(
            "Stage 3: Running KMeans and DBSCAN clustering with empirical archetypes..."
        )
        clustering: ClusteringResult = self.clusterer.run_clustering(
            preprocessed=preprocessed,
            k=cluster_k,
            min_k=eff_min,
            max_k=eff_max,
            adaptive_k=use_adaptive,
            dbscan_eps=self.config.dbscan_eps,
            dbscan_min_samples=self.config.dbscan_min_samples,
        )

        logger.info(
            "Clustering complete. Optimal k=%d. Empirical archetypes: %s",
            clustering.k_optimal,
            list(clustering.archetype_labels.values()),
        )

        # Stage 4: Visualizations
        figure_paths: Dict[str, str] = {}
        if self.config.generate_plots:
            logger.info("Stage 4: Generating projection and diagnostic plots...")
            figure_paths = self.visualizer.generate_all(
                preprocessed=preprocessed,
                clustering=clustering,
                output_dir=self.config.figures_dir,
            )

        # Stage 5: Summary Table & Findings Report Generation
        logger.info("Stage 5: Compiling analytical findings report...")
        summary_table_md = self.visualizer.format_summary_table(
            clustering.cluster_profiles
        )

        norm_origin = str(self.config.origin).strip().lower()
        if norm_origin in ("jp", "japan"):
            report_filename = "cluster_analysis_report_jp.md"
        elif norm_origin in ("non-jp", "non_jp", "international"):
            report_filename = "cluster_analysis_report_non_jp.md"
        else:
            report_filename = "cluster_analysis_report.md"

        report_path = os.path.join(self.config.output_dir, report_filename)
        self._generate_report(
            preprocessed=preprocessed,
            clustering=clustering,
            figure_paths=figure_paths,
            summary_table_md=summary_table_md,
            output_file=report_path,
            db_total_count=db_count,
        )

        logger.info("Report generated successfully at %s", report_path)
        logger.info("=== Anime Insights Pipeline Completed Successfully ===")

        return {
            "num_samples": len(preprocessed.df),
            "db_total_count": db_count,
            "k_optimal": clustering.k_optimal,
            "archetype_labels": clustering.archetype_labels,
            "cluster_profiles": clustering.cluster_profiles,
            "dbscan_clusters": clustering.dbscan_n_clusters,
            "dbscan_noise": clustering.dbscan_n_noise,
            "figure_paths": figure_paths,
            "report_path": report_path,
            "df": preprocessed.df,
            "preprocessed": preprocessed,
            "clustering": clustering,
        }

    def _generate_report(
        self,
        preprocessed: PreprocessedData,
        clustering: ClusteringResult,
        figure_paths: Dict[str, str],
        summary_table_md: str,
        output_file: str,
        db_total_count: int,
    ) -> None:
        """Construct the comprehensive markdown analysis report via ReportBuilder."""
        generate_cluster_report(
            preprocessed=preprocessed,
            clustering=clustering,
            figure_paths=figure_paths,
            summary_table_md=summary_table_md,
            output_file=output_file,
            db_total_count=db_total_count,
        )


def run_comparative_pipeline(config: PipelineConfig) -> Dict[str, Any]:
    """
    Executes independent clustering pipelines for Japanese (JP) and Non-Japanese (Non-JP)
    cohorts, renders cross-market comparative figures, and compiles an analytical comparative report.
    """
    logger.info("=== Starting Comparative Origin Pipeline (JP vs Non-JP) ===")

    # 1. Run Japanese Domestic and Non-Japanese Overseas pipelines concurrently
    jp_config = copy.copy(config)
    jp_config.origin = "jp"
    jp_config.figures_dir = os.path.join(config.output_dir, "figures_jp")

    non_jp_config = copy.copy(config)
    non_jp_config.origin = "non-jp"
    non_jp_config.figures_dir = os.path.join(config.output_dir, "figures_non_jp")

    logger.info("Executing JP and Non-JP cohort pipelines concurrently...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f_jp = executor.submit(InsightsPipeline(jp_config).run)
        f_njp = executor.submit(InsightsPipeline(non_jp_config).run)
        jp_results = f_jp.result()
        non_jp_results = f_njp.result()

    df_jp = jp_results["df"]
    df_non_jp = non_jp_results["df"]

    # Combined dataset for overall distribution
    df_all = pd.concat([df_jp, df_non_jp], ignore_index=True)

    # 3. Generate Comparative Figures
    comp_figures_dir = os.path.join(config.output_dir, "figures_compare")
    os.makedirs(comp_figures_dir, exist_ok=True)

    comp_figures: Dict[str, str] = {}
    if config.generate_plots:
        comp_visualizer = ComparativeVisualizer(dpi=config.dpi)
        comp_figures = comp_visualizer.generate_all_comparative(
            df_all=df_all,
            df_jp=df_jp,
            df_non_jp=df_non_jp,
            output_dir=comp_figures_dir,
        )

    # 4. Generate Comparative Markdown Report
    comp_report_path = os.path.join(config.output_dir, "comparative_origin_report.md")
    _generate_comparative_report(
        df_all=df_all,
        df_jp=df_jp,
        df_non_jp=df_non_jp,
        jp_results=jp_results,
        non_jp_results=non_jp_results,
        comp_figures=comp_figures,
        output_file=comp_report_path,
        db_total_count=jp_results.get("db_total_count", len(df_all)),
    )

    logger.info("Comparative report generated successfully at %s", comp_report_path)
    logger.info("=== Comparative Origin Pipeline Completed Successfully ===")

    merged_figures = {
        **{f"jp_{k}": v for k, v in jp_results.get("figure_paths", {}).items()},
        **{f"non_jp_{k}": v for k, v in non_jp_results.get("figure_paths", {}).items()},
        **comp_figures,
    }

    return {
        "origin": "compare",
        "num_samples": len(df_all),
        "num_jp": len(df_jp),
        "num_non_jp": len(df_non_jp),
        "db_total_count": jp_results.get("db_total_count", len(df_all)),
        "k_optimal": {
            "jp": jp_results["k_optimal"],
            "non_jp": non_jp_results["k_optimal"],
        },
        "archetype_labels": {
            "jp": jp_results["archetype_labels"],
            "non_jp": non_jp_results["archetype_labels"],
        },
        "cluster_profiles": {
            "jp": jp_results["cluster_profiles"],
            "non_jp": non_jp_results["cluster_profiles"],
        },
        "dbscan_clusters": {
            "jp": jp_results["dbscan_clusters"],
            "non_jp": non_jp_results["dbscan_clusters"],
        },
        "dbscan_noise": {
            "jp": jp_results["dbscan_noise"],
            "non_jp": non_jp_results["dbscan_noise"],
        },
        "jp_results": jp_results,
        "non_jp_results": non_jp_results,
        "figure_paths": merged_figures,
        "report_path": comp_report_path,
        "df_all": df_all,
        "df_jp": df_jp,
        "df_non_jp": df_non_jp,
    }


# Canonical alias for pipeline
AnimePipeline = InsightsPipeline
