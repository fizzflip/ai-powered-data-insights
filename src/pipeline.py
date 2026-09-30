"""
Pipeline Orchestration Module for Anime Unsupervised Clustering.

Coordinates end-to-end data acquisition (AniList + Kitsu fallback + SQLite DB),
preprocessing, unsupervised clustering with strict empirical archetype profiling,
visualization generation, and markdown findings reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from typing import Any, Dict, List, Optional
import pandas as pd

from src.database import AnimeCatalogDB
from src.data_fetcher import MultiSourceFetcher
from src.preprocessor import DataPreprocessor, PreprocessedData
from src.clustering import AnimeClusterer, ClusteringResult
from src.visualizer import ClusterVisualizer

logger = logging.getLogger("pipeline")


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
    figures_dir: str = "reports/figures"
    force_fetch: bool = False
    offline_mode: bool = False
    incremental: bool = True
    generate_plots: bool = True


class InsightsPipeline:
    """End-to-end pipeline orchestrator for anime archetype discovery."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
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
        self.visualizer = ClusterVisualizer(random_state=42)

    def run(self) -> Dict[str, Any]:
        """Execute all stages of the clustering pipeline."""
        logger.info("=== Starting Anime Insights Pipeline (Iteration 3) ===")
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(self.config.figures_dir, exist_ok=True)

        # Stage 1: Multi-Source Data Acquisition & Incremental Ingestion
        logger.info(
            "Stage 1: Fetching anime records (target: %d, source: %s, offline: %s)...",
            self.config.num_samples,
            self.config.preferred_source,
            self.config.offline_mode,
        )
        raw_data = self.fetcher.fetch_anime_data(
            limit=self.config.num_samples,
            preferred_source=self.config.preferred_source,
            force_fetch=self.config.force_fetch,
            offline=self.config.offline_mode,
            incremental=self.config.incremental,
        )
        db_count = self.db.count_records()
        logger.info("Acquired %d records for pipeline. Total in SQLite DB: %d.", len(raw_data), db_count)

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

        use_adaptive = self.config.adaptive_k or self.config.k == 0 or self.config.k is None
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

        logger.info("Stage 3: Running KMeans and DBSCAN clustering with empirical archetypes...")
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
        summary_table_md = self.visualizer.format_summary_table(clustering.cluster_profiles)
        report_path = os.path.join(self.config.output_dir, "cluster_analysis_report.md")
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
        """Construct the comprehensive markdown analysis report with empirical archetype findings."""
        df = preprocessed.df.copy()
        df["cluster_id"] = clustering.kmeans_labels
        df["archetype"] = df["cluster_id"].map(clustering.archetype_labels)

        # Extract representative anime titles per cluster
        exemplars: Dict[int, List[str]] = {}
        for cid in sorted(clustering.archetype_labels.keys()):
            cluster_subset = df[df["cluster_id"] == cid]
            top_titles = (
                cluster_subset.sort_values("popularity", ascending=False)["title"]
                .dropna()
                .drop_duplicates()
                .head(5)
                .tolist()
            )
            exemplars[cid] = top_titles

        lines: List[str] = [
            "# Anime Unsupervised Clustering & Empirical Archetype Report",
            "",
            "## Executive Summary",
            f"- **Dataset Analyzed**: {len(df):,} anime entries (Current SQLite Local Database: {db_total_count:,} titles)",
            "- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)",
            "- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting",
            f"- **Feature Dimensionality**: {preprocessed.X.shape[1]} engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)",
            f"- **K-Means Cluster Count ($k$)**: {clustering.k_optimal}",
            f"- **DBSCAN Density Structure**: {clustering.dbscan_n_clusters} dense core clusters, {clustering.dbscan_n_noise} structural noise/outlier points",
            "",
            "---",
            "",
        ]

        k_eval_keys = sorted(clustering.elbow_inertias.keys())
        min_eval_k = min(k_eval_keys) if k_eval_keys else 2
        max_eval_k = max(k_eval_keys) if k_eval_keys else 10

        lines.extend([
            "## 1. Optimal Number of Clusters & Silhouette Diagnostics",
            f"Cluster cohesion and separation were evaluated across candidate cluster counts $k \\in [{min_eval_k}, {max_eval_k}]$:",
            "",
            "| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |",
            "|:--------------:|:----------------:|:----------------:|:--------------------------:|",
        ])

        for k in k_eval_keys:
            inertia_val = f"{clustering.elbow_inertias[k]:.2f}"
            sil_val = f"{clustering.silhouette_scores.get(k, 0.0):.4f}" if k in clustering.silhouette_scores else "N/A"
            status = "Selected" if k == clustering.k_optimal else ("Global Maximum" if sil_val == max(f"{v:.4f}" for v in clustering.silhouette_scores.values()) else "")
            lines.append(f"| {k} | {inertia_val} | {sil_val} | {status} |")

        lines.extend([
            "",
            "> [!NOTE]",
            "> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. "
            "Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, "
            "allowing subtle sub-genres and era distinctions to surface as the database grows.",
            "",
            "---",
            "",
            "## 2. Cluster Profiles Summary Table",
            "Quantitative feature means and dominant categorical traits across each discovered cluster archetype:",
            "",
            summary_table_md,
            "",
            "---",
            "",
            "## 3. Detailed Empirical Archetype Findings",
        ])

        for cid, arch in clustering.archetype_labels.items():
            profile_row = clustering.cluster_profiles[clustering.cluster_profiles["cluster_id"] == cid]
            size_count = int(profile_row["size"].values[0]) if not profile_row.empty else 0
            mean_score = float(profile_row["score"].values[0]) if not profile_row.empty else 0.0
            mean_pop = float(profile_row["popularity"].values[0]) if not profile_row.empty else 0.0
            med_year = int(profile_row["year"].values[0]) if not profile_row.empty else 0
            fav_ratio = float(profile_row["favorites_ratio"].values[0]) if not profile_row.empty else 0.0
            genres = str(profile_row["top_genres"].values[0]) if not profile_row.empty else "N/A"
            tags = str(profile_row["top_tags"].values[0]) if not profile_row.empty else "N/A"
            sample_titles = ", ".join(exemplars.get(cid, ["None"]))

            lines.extend([
                f"### Cluster {cid}: {arch}",
                f"- **Cluster Size**: {size_count} titles ({size_count / len(df) * 100:.1f}% of catalog)",
                f"- **Median Release Year**: {med_year}",
                f"- **Mean Average Score**: {mean_score:.2f} / 100",
                f"- **Mean Popularity**: {mean_pop:,.0f} members",
                f"- **Favorites-to-Popularity Ratio**: {fav_ratio:.4f}",
                f"- **Dominant Genres**: {genres}",
                f"- **Key Thematic Tags**: {tags}",
                f"- **Representative Exemplar Titles**: {sample_titles}",
                "",
            ])

        lines.extend([
            "---",
            "",
            "## 4. Latent Space Visualizations & Manifold Projections",
            "High-dimensional representations projected via PCA (2D & 3D) and t-SNE (2D):",
            "",
        ])

        for fig_name, fig_path in figure_paths.items():
            rel_path = os.path.relpath(fig_path, os.path.dirname(output_file))
            title_text = fig_name.replace("_", " ").title()
            lines.append(f"### {title_text}")
            lines.append(f"![{title_text}]({rel_path})")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 5. Incremental Database Architecture & Fallback Strategy",
            "1. **SQLite Persistent Database (`data/anime_catalog.db`)**: Deduplicates incoming anime by canonical ID (`anilist:{id}`, `kitsu:{id}`), tracking pagination state across runs.",
            "2. **Rate Limit Throttling**: Implements configurable polite delays (`--rate-delay`) to prevent API rate limits or IP bans during large catalog harvests.",
            "3. **Multi-Source Failover**: Queries AniList GraphQL endpoint by default. If AniList is rate-limited, unreachable, or returns insufficient records, queries Kitsu JSON:API, normalizing attributes into the standard schema.",
            "4. **Offline Portability**: The database automatically exports full state to `data/raw_anime_data.json` for offline demonstration.",
            "",
            "---",
            "*Report auto-generated by the Antigravity Data Science Pipeline.*",
        ])

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


# Canonical alias for pipeline
AnimePipeline = InsightsPipeline
