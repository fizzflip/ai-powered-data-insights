"""
Comparative Cross-Market Visualizer Module.

Generates comparative diagnostic plots contrasting Japanese Domestic (JP)
and International / Overseas (Non-JP: Donghua, Aeni, Western) animation:
1. Sub-origin market distribution (JP vs CN vs KR vs Western).
2. Score & Popularity distribution divergences (dual KDE / violin plots).
3. Episode format & runtime structures (TV broadcast cours vs Web/ONA formats).
4. Top genre affinity divergence between cohorts.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import matplotlib
# Headless backend guarantee
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger("comparative_visualizer")


class ComparativeVisualizer:
    """
    Renders high-resolution comparative charts contrasting JP and Non-JP anime markets.
    """

    def __init__(self, style: str = "whitegrid") -> None:
        sns.set_theme(style=style)
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False

    def plot_origin_distribution(
        self,
        df_all: pd.DataFrame,
        save_path: Union[str, Path] = "reports/figures_compare/origin_distribution.png",
    ) -> str:
        """Plot market breakdown by sub-origin (JP, CN, KR, Western, Other)."""
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 1. Binary Cohort Pie
        cohort_counts = df_all["origin_cohort"].value_counts()
        labels = [f"JP Domestic\n({cohort_counts.get('jp', 0):,})" , f"Non-JP Overseas\n({cohort_counts.get('non-jp', 0):,})"]
        colors = ["#4C72B0", "#DD8452"]
        values = [cohort_counts.get("jp", 0), cohort_counts.get("non-jp", 0)]

        ax1.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            explode=(0, 0.08),
            textprops={"fontsize": 11, "weight": "bold"},
        )
        ax1.set_title("Overall Catalog Cohort Distribution", fontsize=13, pad=15)

        # 2. Granular Non-JP Sub-Origin Bar Chart
        non_jp_df = df_all[df_all["origin_cohort"] == "non-jp"]
        if not non_jp_df.empty:
            subtag_counts = non_jp_df["sub_origin"].value_counts()
            subtag_labels = {
                "CN": "Chinese (Donghua)",
                "KR": "Korean (Aeni)",
                "WESTERN": "Western / Global",
                "OTHER": "Other Foreign",
            }
            renamed_labels = [subtag_labels.get(k, k) for k in subtag_counts.index]
            sub_colors = sns.color_palette("Set2", len(subtag_counts))

            bars = ax2.barh(renamed_labels, subtag_counts.values, color=sub_colors, edgecolor="black", alpha=0.85)
            ax2.bar_label(bars, fmt="%d", padding=5, fontsize=10, weight="bold")
            ax2.set_xlabel("Number of Titles", fontsize=11)
            ax2.set_title(f"Non-JP Cohort Breakdown (n={len(non_jp_df):,})", fontsize=13, pad=15)
            ax2.grid(True, linestyle="--", alpha=0.5)
        else:
            ax2.text(0.5, 0.5, "No Non-JP Titles Found", ha="center", va="center")

        plt.tight_layout()
        fig.savefig(save_file, dpi=300, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved origin distribution plot to %s", save_file)
        return str(save_file)

    def plot_score_popularity_comparison(
        self,
        df_jp: pd.DataFrame,
        df_non_jp: pd.DataFrame,
        save_path: Union[str, Path] = "reports/figures_compare/score_popularity_comparison.png",
    ) -> str:
        """Dual distribution comparison of Average Score and Popularity."""
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 1. Score Distribution (KDE)
        jp_scores = df_jp["averageScore"].dropna()
        njp_scores = df_non_jp["averageScore"].dropna()

        sns.kdeplot(jp_scores, ax=ax1, label=f"JP (Mean: {jp_scores.mean():.1f})", color="#4C72B0", fill=True, alpha=0.35, linewidth=2)
        if len(njp_scores) > 1:
            sns.kdeplot(njp_scores, ax=ax1, label=f"Non-JP (Mean: {njp_scores.mean():.1f})", color="#DD8452", fill=True, alpha=0.35, linewidth=2)
        ax1.set_title("Average Score Distribution (0-100 Scale)", fontsize=13, pad=15)
        ax1.set_xlabel("Average Score", fontsize=11)
        ax1.set_ylabel("Density", fontsize=11)
        ax1.legend(loc="upper left", frameon=True, fontsize=10)
        ax1.grid(True, linestyle="--", alpha=0.5)

        # 2. Log Popularity Distribution (KDE)
        jp_pop = np.log10(df_jp["popularity"].clip(lower=1.0))
        njp_pop = np.log10(df_non_jp["popularity"].clip(lower=1.0))

        sns.kdeplot(jp_pop, ax=ax2, label=f"JP (Median: 10^{jp_pop.median():.1f})", color="#4C72B0", fill=True, alpha=0.35, linewidth=2)
        if len(njp_pop) > 1:
            sns.kdeplot(njp_pop, ax=ax2, label=f"Non-JP (Median: 10^{njp_pop.median():.1f})", color="#DD8452", fill=True, alpha=0.35, linewidth=2)
        ax2.set_title("Log10 Popularity Distribution", fontsize=13, pad=15)
        ax2.set_xlabel("Log10(Popularity Members)", fontsize=11)
        ax2.set_ylabel("Density", fontsize=11)
        ax2.legend(loc="upper right", frameon=True, fontsize=10)
        ax2.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        fig.savefig(save_file, dpi=300, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved score & popularity comparison to %s", save_file)
        return str(save_file)

    def plot_format_comparison(
        self,
        df_jp: pd.DataFrame,
        df_non_jp: pd.DataFrame,
        save_path: Union[str, Path] = "reports/figures_compare/format_comparison.png",
    ) -> str:
        """Compare Episode Counts and Duration structures between markets."""
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 1. Episode Count Boxplot (Log Scale)
        data_ep = []
        for v in df_jp["episodes"].dropna():
            if v > 0:
                data_ep.append({"Cohort": "JP Domestic", "Episodes": v})
        for v in df_non_jp["episodes"].dropna():
            if v > 0:
                data_ep.append({"Cohort": "Non-JP Overseas", "Episodes": v})

        df_ep = pd.DataFrame(data_ep)
        if not df_ep.empty:
            sns.boxplot(data=df_ep, x="Cohort", y="Episodes", hue="Cohort", ax=ax1, palette=["#4C72B0", "#DD8452"], legend=False, showfliers=False)
            ax1.set_title("Episode Count Distribution (per Title)", fontsize=13, pad=15)
            ax1.set_ylabel("Episodes (Excl. Outliers)", fontsize=11)
            ax1.grid(True, linestyle="--", alpha=0.5)

        # 2. Episode Duration Boxplot (Minutes)
        data_dur = []
        for v in df_jp["duration"].dropna():
            if 0 < v <= 180:
                data_dur.append({"Cohort": "JP Domestic", "Duration (mins)": v})
        for v in df_non_jp["duration"].dropna():
            if 0 < v <= 180:
                data_dur.append({"Cohort": "Non-JP Overseas", "Duration (mins)": v})

        df_dur = pd.DataFrame(data_dur)
        if not df_dur.empty:
            sns.boxplot(data=df_dur, x="Cohort", y="Duration (mins)", hue="Cohort", ax=ax2, palette=["#4C72B0", "#DD8452"], legend=False, showfliers=False)
            ax2.set_title("Episode Duration Distribution (Minutes)", fontsize=13, pad=15)
            ax2.set_ylabel("Duration (Minutes)", fontsize=11)
            ax2.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        fig.savefig(save_file, dpi=300, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved format comparison plot to %s", save_file)
        return str(save_file)

    def plot_genre_divergence(
        self,
        df_jp: pd.DataFrame,
        df_non_jp: pd.DataFrame,
        save_path: Union[str, Path] = "reports/figures_compare/genre_divergence.png",
        top_n: int = 10,
    ) -> str:
        """Compare relative frequency of top genres between cohorts."""
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)

        def count_genres(df: pd.DataFrame) -> pd.Series:
            genres_list = []
            for item in df["genres"].dropna():
                if isinstance(item, list):
                    genres_list.extend(item)
                elif isinstance(item, str):
                    genres_list.extend([g.strip() for g in item.split(",") if g.strip()])
            return pd.Series(genres_list).value_counts(normalize=True) * 100

        s_jp = count_genres(df_jp)
        s_njp = count_genres(df_non_jp)

        # Top genres overall
        all_genres = (s_jp.add(s_njp, fill_value=0.0)).nlargest(top_n).index

        plot_data = []
        for g in all_genres:
            plot_data.append({"Genre": g, "Cohort": "JP Domestic", "Prevalence (%)": s_jp.get(g, 0.0)})
            plot_data.append({"Genre": g, "Cohort": "Non-JP Overseas", "Prevalence (%)": s_njp.get(g, 0.0)})

        df_plot = pd.DataFrame(plot_data)

        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(data=df_plot, y="Genre", x="Prevalence (%)", hue="Cohort", ax=ax, palette=["#4C72B0", "#DD8452"], edgecolor="black")
        ax.set_title(f"Top {top_n} Genre Prevalence: JP vs Non-JP Cohorts", fontsize=14, pad=15)
        ax.set_xlabel("Prevalence (% of titles in cohort featuring genre)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Cohort", fontsize=10)

        plt.tight_layout()
        fig.savefig(save_file, dpi=300, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved genre divergence plot to %s", save_file)
        return str(save_file)

    def generate_all_comparative(
        self,
        df_all: pd.DataFrame,
        df_jp: pd.DataFrame,
        df_non_jp: pd.DataFrame,
        output_dir: Union[str, Path] = "reports/figures_compare",
    ) -> Dict[str, str]:
        """Generate full suite of comparative charts."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        return {
            "origin_distribution": self.plot_origin_distribution(df_all, out_path / "origin_distribution.png"),
            "score_popularity": self.plot_score_popularity_comparison(df_jp, df_non_jp, out_path / "score_popularity_comparison.png"),
            "format_comparison": self.plot_format_comparison(df_jp, df_non_jp, out_path / "format_comparison.png"),
            "genre_divergence": self.plot_genre_divergence(df_jp, df_non_jp, out_path / "genre_divergence.png"),
        }
