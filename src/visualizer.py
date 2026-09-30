"""
Visualization module for unsupervised anime clustering.

Provides ClusterVisualizer for rendering evaluation diagnostics (Elbow, Silhouette),
dimensionality reduction projections (2D/3D PCA, 2D t-SNE), archetype heatmaps,
and markdown summary tables.
"""

import logging
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib

# Headless backend configuration for server/CLI environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.mplot3d import (
    Axes3D,  # noqa: F401 - required for 3d projection registration
)
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from tabulate import tabulate

warnings.filterwarnings("ignore", message=".*Glyph.*missing from font.*")
from src.visualization_base import BaseVisualizer

logger = logging.getLogger(__name__)


class ClusterVisualizer(BaseVisualizer):
    """Visualizer for clustering metrics, latent projections, and archetype profiles."""

    def __init__(
        self,
        style: str = "whitegrid",
        palette: str = "tab10",
        random_state: int = 42,
        dpi: int = 150,
    ) -> None:
        """Initialize visualizer styling and parameters.

        Parameters
        ----------
        style : str, default='whitegrid'
            Seaborn theme style.
        palette : str, default='tab10'
            Color palette for distinct cluster archetypes.
        random_state : int, default=42
            Random seed for stochastic algorithms (e.g. t-SNE, PCA).
        dpi : int, default=150
            Rasterization dots per inch for saved figure outputs.
        """
        super().__init__(style=style, dpi=dpi)
        self.palette_name = palette
        self.random_state = random_state

    @staticmethod
    def _sanitize_title(title: str, max_chars: int = 35) -> str:
        """Sanitize title text for clean plot rendering across all font environments."""
        if not title:
            return "Unknown"
        s = str(title).strip().replace("\n", " ")
        if len(s) > max_chars:
            return s[: max_chars - 3] + "..."
        return s

    def _get_color_map(
        self, unique_labels: List[int]
    ) -> Dict[int, Union[str, Tuple[float, ...]]]:
        """Generate consistent color mapping across cluster labels."""
        num_clusters = len(unique_labels)
        if num_clusters > 20:
            palette = sns.color_palette("husl", max(num_clusters, 1))
        elif num_clusters > 10:
            palette = sns.color_palette("tab20", max(num_clusters, 1))
        else:
            palette = sns.color_palette(self.palette_name, max(num_clusters, 1))
        color_map = {}
        for idx, lbl in enumerate(unique_labels):
            if lbl == -1:
                color_map[lbl] = "#7f7f7f"  # Noise / outlier color in gray
            else:
                color_map[lbl] = palette[idx % len(palette)]
        return color_map

    def _ensure_dir(self, file_path: Union[str, Path]) -> Path:
        """Ensure parent directory of target save path exists."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _to_numpy(data: Any) -> np.ndarray:
        """Convert input data to 2D numpy array."""
        if hasattr(data, "to_numpy"):
            return data.to_numpy()
        if hasattr(data, "toarray"):
            return data.toarray()
        return np.asarray(data)

    def plot_elbow_and_silhouette(
        self,
        elbow_inertias: Union[Dict[int, float], List[float]],
        silhouette_scores: Union[Dict[int, float], List[float]],
        k_optimal: Optional[int] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """Plot a 2-panel chart showing Elbow inertia curve and Silhouette scores across k."""
        if isinstance(elbow_inertias, dict):
            k_elbow = sorted(elbow_inertias.keys())
            inertias = [elbow_inertias[k] for k in k_elbow]
        else:
            inertias = list(elbow_inertias)
            k_elbow = list(range(2, len(inertias) + 2))

        if isinstance(silhouette_scores, dict):
            k_sil = sorted(silhouette_scores.keys())
            sil_scores = [silhouette_scores[k] for k in k_sil]
        else:
            sil_scores = list(silhouette_scores)
            k_sil = list(range(2, len(sil_scores) + 2))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Panel 1: Elbow Inertia Curve
        ax1.plot(
            k_elbow,
            inertias,
            marker="o",
            color="#1f77b4",
            linewidth=2,
            markersize=6,
            label="Inertia",
        )
        ax1.set_title("Elbow Method (Inertia vs. k)", fontsize=13, pad=12)
        ax1.set_xlabel("Number of Clusters (k)", fontsize=11)
        ax1.set_ylabel("Inertia (Sum of Squared Distances)", fontsize=11)
        ax1.grid(True, linestyle="--", alpha=0.6)

        if k_optimal is not None and k_optimal in k_elbow:
            idx = k_elbow.index(k_optimal)
            opt_inertia = inertias[idx]
            ax1.axvline(
                x=k_optimal,
                color="#d62728",
                linestyle="--",
                linewidth=1.5,
                label=f"Optimal k={k_optimal}",
            )
            ax1.scatter(
                [k_optimal],
                [opt_inertia],
                color="#d62728",
                s=120,
                zorder=5,
                edgecolor="black",
            )
            ax1.legend(loc="upper right", frameon=True)

        # Panel 2: Silhouette Scores across k
        ax2.plot(
            k_sil,
            sil_scores,
            marker="s",
            color="#2ca02c",
            linewidth=2,
            markersize=6,
            label="Silhouette Score",
        )
        ax2.set_title("Silhouette Analysis Across k", fontsize=13, pad=12)
        ax2.set_xlabel("Number of Clusters (k)", fontsize=11)
        ax2.set_ylabel("Silhouette Score", fontsize=11)
        ax2.grid(True, linestyle="--", alpha=0.6)

        if k_optimal is not None and k_optimal in k_sil:
            idx = k_sil.index(k_optimal)
            opt_sil = sil_scores[idx]
            ax2.axvline(
                x=k_optimal,
                color="#d62728",
                linestyle="--",
                linewidth=1.5,
                label=f"Optimal k={k_optimal}",
            )
            ax2.scatter(
                [k_optimal],
                [opt_sil],
                color="#d62728",
                s=120,
                zorder=5,
                edgecolor="black",
            )
            ax2.legend(loc="best", frameon=True)

        plt.tight_layout()

        if save_path:
            p = self._ensure_dir(save_path)
            fig.savefig(p, bbox_inches="tight", dpi=self.dpi)
            logger.info("Saved elbow & silhouette plot to %s", p)

        return fig

    def plot_pca_2d(
        self,
        X: Any,
        labels: Any,
        archetype_map: Optional[Dict[int, str]] = None,
        titles: Optional[Any] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """Plot 2D PCA scatter plot colored by archetype with legend and exemplar titles."""
        X_arr = self._to_numpy(X)
        labels_arr = np.asarray(labels)

        pca = PCA(n_components=2, random_state=self.random_state)
        X_pca = pca.fit_transform(X_arr)
        evr = pca.explained_variance_ratio_ * 100

        unique_labels = sorted(np.unique(labels_arr))
        color_map = self._get_color_map(unique_labels)
        archetype_map = archetype_map or {}

        fig, ax = plt.subplots(figsize=(11, 8))

        for lbl in unique_labels:
            mask = labels_arr == lbl
            name = archetype_map.get(lbl, f"Cluster {lbl}")
            color = color_map[lbl]
            ax.scatter(
                X_pca[mask, 0],
                X_pca[mask, 1],
                label=f"{name} (n={np.sum(mask)})",
                color=color,
                alpha=0.65,
                s=40,
                edgecolor="white",
                linewidth=0.3,
            )

        if titles is not None:
            if hasattr(titles, "__len__") and len(titles) == len(labels_arr):
                titles_list = list(titles)
                for lbl in unique_labels:
                    if lbl == -1:
                        continue
                    mask = labels_arr == lbl
                    pts = X_pca[mask]
                    if len(pts) == 0:
                        continue
                    centroid = pts.mean(axis=0)
                    dist = np.linalg.norm(pts - centroid, axis=1)
                    best_local_idx = np.argmin(dist)
                    global_idx = np.where(mask)[0][best_local_idx]
                    exemplar_title = self._sanitize_title(str(titles_list[global_idx]))

                    color = color_map[lbl]
                    ax.scatter(
                        X_pca[global_idx, 0],
                        X_pca[global_idx, 1],
                        color=color,
                        edgecolor="black",
                        marker="*",
                        s=160,
                        zorder=6,
                    )
                    ax.annotate(
                        exemplar_title,
                        (X_pca[global_idx, 0], X_pca[global_idx, 1]),
                        xytext=(15, 12),
                        textcoords="offset points",
                        fontsize=8.5,
                        fontweight="bold",
                        bbox=dict(
                            boxstyle="round,pad=0.25",
                            facecolor="white",
                            edgecolor=color,
                            alpha=0.9,
                            lw=1.2,
                        ),
                        arrowprops=dict(
                            arrowstyle="->",
                            connectionstyle="arc3,rad=0.15",
                            color="#333333",
                            lw=1.0,
                        ),
                        zorder=7,
                    )

        ax.set_title("2D PCA Projection with Cluster Archetypes", fontsize=14, pad=15)
        ax.set_xlabel(f"Principal Component 1 ({evr[0]:.1f}% variance)", fontsize=11)
        ax.set_ylabel(f"Principal Component 2 ({evr[1]:.1f}% variance)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            frameon=True,
            title="Archetypes",
            fontsize=9.5,
        )
        plt.tight_layout()

        if save_path:
            p = self._ensure_dir(save_path)
            fig.savefig(p, bbox_inches="tight", dpi=self.dpi)
            logger.info("Saved 2D PCA plot to %s", p)

        return fig

    def plot_pca_3d(
        self,
        X: Any,
        labels: Any,
        archetype_map: Optional[Dict[int, str]] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """Plot 3D PCA scatter plot showing spatial cluster separation."""
        X_arr = self._to_numpy(X)
        labels_arr = np.asarray(labels)

        n_components = min(3, X_arr.shape[1])
        pca = PCA(n_components=n_components, random_state=self.random_state)
        X_pca = pca.fit_transform(X_arr)
        evr = pca.explained_variance_ratio_ * 100

        if X_pca.shape[1] < 3:
            pad = np.zeros((X_pca.shape[0], 3 - X_pca.shape[1]))
            X_pca = np.hstack([X_pca, pad])

        unique_labels = sorted(np.unique(labels_arr))
        color_map = self._get_color_map(unique_labels)
        archetype_map = archetype_map or {}

        fig = plt.figure(figsize=(11, 8.5))
        ax = fig.add_subplot(111, projection="3d")

        for lbl in unique_labels:
            mask = labels_arr == lbl
            name = archetype_map.get(lbl, f"Cluster {lbl}")
            color = color_map[lbl]
            ax.scatter(
                X_pca[mask, 0],
                X_pca[mask, 1],
                X_pca[mask, 2],
                label=f"{name} (n={np.sum(mask)})",
                color=color,
                alpha=0.6,
                s=35,
                edgecolor="none",
            )

        ax.set_title("3D PCA Latent Space Separation", fontsize=14, pad=18)
        pc1_label = f"PC1 ({evr[0]:.1f}%)" if len(evr) > 0 else "PC1"
        pc2_label = f"PC2 ({evr[1]:.1f}%)" if len(evr) > 1 else "PC2"
        pc3_label = f"PC3 ({evr[2]:.1f}%)" if len(evr) > 2 else "PC3"

        ax.set_xlabel(pc1_label, labelpad=9, fontsize=10)
        ax.set_ylabel(pc2_label, labelpad=9, fontsize=10)
        ax.set_zlabel(pc3_label, labelpad=9, fontsize=10)
        ax.view_init(elev=22, azim=130)
        ax.legend(
            bbox_to_anchor=(1.08, 1),
            loc="upper left",
            frameon=True,
            title="Archetypes",
            fontsize=9,
        )
        plt.tight_layout()

        if save_path:
            p = self._ensure_dir(save_path)
            fig.savefig(p, bbox_inches="tight", dpi=self.dpi)
            logger.info("Saved 3D PCA plot to %s", p)

        return fig

    def plot_tsne_2d(
        self,
        X: Any,
        labels: Any,
        archetype_map: Optional[Dict[int, str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        perplexity: float = 30.0,
        random_state: Optional[int] = None,
        max_samples: int = 2000,
    ) -> plt.Figure:
        """Plot 2D t-SNE manifold visualization with stratified subsampling for large datasets."""
        X_arr = self._to_numpy(X)
        labels_arr = np.asarray(labels)
        seed = random_state if random_state is not None else self.random_state

        n_samples = X_arr.shape[0]

        max_pca_comp = min(50, n_samples - 1, X_arr.shape[1])
        if X_arr.shape[1] > 50 and max_pca_comp >= 2:
            X_reduced = PCA(n_components=max_pca_comp, random_state=seed).fit_transform(
                X_arr
            )
        else:
            X_reduced = X_arr

        # Stratified subsampling for fast, collision-free t-SNE rendering on large datasets
        if n_samples > max_samples:
            rng = np.random.RandomState(seed)
            sub_indices = []
            for lbl in np.unique(labels_arr):
                lbl_indices = np.where(labels_arr == lbl)[0]
                sample_n = max(5, int(len(lbl_indices) / n_samples * max_samples))
                sub_indices.extend(
                    rng.choice(
                        lbl_indices, size=min(len(lbl_indices), sample_n), replace=False
                    )
                )
            sub_indices = np.array(sorted(sub_indices))
            X_tsne_input = X_reduced[sub_indices]
            labels_tsne = labels_arr[sub_indices]
        else:
            X_tsne_input = X_reduced
            labels_tsne = labels_arr

        effective_perp = min(perplexity, max(1.0, float(len(X_tsne_input) - 1) / 3.0))
        if effective_perp >= len(X_tsne_input):
            effective_perp = max(1.0, float(len(X_tsne_input) - 1))

        tsne = TSNE(
            n_components=2,
            perplexity=effective_perp,
            random_state=seed,
            init="pca" if effective_perp < len(X_tsne_input) else "random",
            learning_rate="auto",
            max_iter=500,
            n_jobs=-1,
        )
        X_tsne = tsne.fit_transform(X_tsne_input)

        unique_labels = sorted(np.unique(labels_tsne))
        color_map = self._get_color_map(unique_labels)
        archetype_map = archetype_map or {}

        fig, ax = plt.subplots(figsize=(11, 8))

        for lbl in unique_labels:
            mask = labels_tsne == lbl
            name = archetype_map.get(lbl, f"Cluster {lbl}")
            color = color_map[lbl]
            ax.scatter(
                X_tsne[mask, 0],
                X_tsne[mask, 1],
                label=f"{name} (n={np.sum(mask)})",
                color=color,
                alpha=0.65,
                s=40,
                edgecolor="white",
                linewidth=0.3,
            )

        ax.set_title("2D t-SNE Manifold Visualization", fontsize=14, pad=15)
        ax.set_xlabel("t-SNE Dimension 1", fontsize=11)
        ax.set_ylabel("t-SNE Dimension 2", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            frameon=True,
            title="Archetypes",
            fontsize=9.5,
        )
        plt.tight_layout()

        if save_path:
            p = self._ensure_dir(save_path)
            fig.savefig(p, bbox_inches="tight", dpi=self.dpi)
            logger.info("Saved 2D t-SNE plot to %s", p)

        return fig

    def plot_cluster_heatmap(
        self,
        cluster_profiles: pd.DataFrame,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """Plot Seaborn heatmap of normalized feature means across clusters."""
        df = cluster_profiles.copy()

        for col in ["archetype", "archetype_name", "cluster_name"]:
            if col in df.columns:
                df = df.set_index(col)
                break
        else:
            if "cluster" in df.columns and not isinstance(df.index, pd.Index):
                df = df.set_index("cluster")

        ignored_cols = {"cluster", "cluster_id", "id", "count", "size", "n_samples"}
        numeric_cols = [
            c
            for c in df.select_dtypes(include=[np.number]).columns
            if str(c).lower() not in ignored_cols
        ]
        if not numeric_cols:
            numeric_cols = list(df.select_dtypes(include=[np.number]).columns)

        data = df[numeric_cols].astype(float)
        stds = data.std(axis=0).replace(0, 1.0)
        means = data.mean(axis=0)
        normalized = (data - means) / stds
        normalized = normalized.fillna(0.0)

        fig_width = max(8.0, len(numeric_cols) * 0.85)
        fig_height = max(5.0, len(df) * 0.8)
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        sns.heatmap(
            normalized,
            cmap="coolwarm",
            center=0,
            annot=True,
            fmt=".2f",
            linewidths=0.8,
            cbar_kws={"label": "Normalized Mean (Z-score)"},
            ax=ax,
        )

        ax.set_title("Normalized Feature Means Across Clusters", fontsize=14, pad=15)
        ax.set_xlabel("Features", fontsize=11, labelpad=10)
        ax.set_ylabel("Clusters / Archetypes", fontsize=11, labelpad=10)
        plt.xticks(rotation=45, ha="right", fontsize=9.5)
        plt.yticks(rotation=0, fontsize=9.5)
        plt.tight_layout()

        if save_path:
            p = self._ensure_dir(save_path)
            fig.savefig(p, bbox_inches="tight", dpi=self.dpi)
            logger.info("Saved cluster heatmap to %s", p)

        return fig

    def format_summary_table(self, cluster_profiles: pd.DataFrame) -> str:
        """Format cluster profiles DataFrame into a GitHub-flavored Markdown table."""
        if cluster_profiles is None or cluster_profiles.empty:
            return ""

        df = cluster_profiles.copy()
        show_index = not (isinstance(df.index, pd.RangeIndex) and df.index.name is None)
        return tabulate(
            df,
            headers="keys",
            tablefmt="github",
            showindex=show_index,
            floatfmt=".2f",
        )

    @staticmethod
    def _extract(source: Any, candidates: List[str]) -> Any:
        """Extract first matching attribute or dictionary key from source."""
        if source is None:
            return None
        for key in candidates:
            if isinstance(source, dict) and key in source:
                val = source[key]
                if val is not None:
                    return val
            if hasattr(source, key):
                val = getattr(source, key)
                if val is not None:
                    return val
        return None

    def generate_all(
        self,
        preprocessed: Any,
        clustering: Any,
        output_dir: Union[str, Path] = "reports/figures",
    ) -> Dict[str, str]:
        """Generate and save all diagnostic and projection figures."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        saved_paths: Dict[str, str] = {}

        X = self._extract(preprocessed, ["X", "features", "data", "X_scaled", "matrix"])
        if X is None:
            X = self._extract(clustering, ["X", "features", "data"])

        titles = self._extract(
            preprocessed, ["titles", "title", "names", "anime_titles"]
        )
        if titles is None:
            raw_df = self._extract(preprocessed, ["df", "data_frame", "dataset"])
            if raw_df is not None and isinstance(raw_df, pd.DataFrame):
                for col in ["title", "name", "anime_title", "title_english"]:
                    if col in raw_df.columns:
                        titles = raw_df[col].tolist()
                        break

        labels = self._extract(
            clustering,
            ["labels", "kmeans_labels", "labels_", "cluster_labels", "clusters"],
        )
        archetype_map = self._extract(
            clustering,
            [
                "archetype_labels",
                "archetype_map",
                "archetypes",
                "cluster_names",
                "archetype_mapping",
            ],
        )
        elbow_inertias = self._extract(
            clustering,
            ["elbow_inertias", "inertias", "elbow_inertia", "inertia_scores"],
        )
        silhouette_scores = self._extract(
            clustering,
            [
                "silhouette_scores",
                "silhouettes",
                "silhouette_curve",
                "silhouette_values",
            ],
        )
        k_optimal = self._extract(clustering, ["k_optimal", "optimal_k", "best_k", "k"])
        cluster_profiles = self._extract(
            clustering,
            ["cluster_profiles", "profiles", "summary_df", "cluster_summary"],
        )

        # 1. Elbow & Silhouette
        if elbow_inertias is not None and silhouette_scores is not None:
            p = out_path / "elbow_silhouette.png"
            fig = self.plot_elbow_and_silhouette(
                elbow_inertias, silhouette_scores, k_optimal, save_path=p
            )
            plt.close(fig)
            saved_paths["elbow_silhouette"] = str(p)

        # 2. PCA 2D
        if X is not None and labels is not None:
            p = out_path / "pca_2d.png"
            fig = self.plot_pca_2d(
                X, labels, archetype_map=archetype_map, titles=titles, save_path=p
            )
            plt.close(fig)
            saved_paths["pca_2d"] = str(p)

        # 3. PCA 3D
        if X is not None and labels is not None:
            p = out_path / "pca_3d.png"
            fig = self.plot_pca_3d(X, labels, archetype_map=archetype_map, save_path=p)
            plt.close(fig)
            saved_paths["pca_3d"] = str(p)

        # 4. t-SNE 2D
        if X is not None and labels is not None:
            p = out_path / "tsne_2d.png"
            fig = self.plot_tsne_2d(X, labels, archetype_map=archetype_map, save_path=p)
            plt.close(fig)
            saved_paths["tsne_2d"] = str(p)

        # 5. Cluster Heatmap
        if cluster_profiles is not None and isinstance(cluster_profiles, pd.DataFrame):
            p = out_path / "cluster_heatmap.png"
            fig = self.plot_cluster_heatmap(cluster_profiles, save_path=p)
            plt.close(fig)
            saved_paths["cluster_heatmap"] = str(p)

        logger.info("Generated %d figures in %s", len(saved_paths), out_path)
        return saved_paths
