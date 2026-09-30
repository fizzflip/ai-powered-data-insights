"""
Anime Unsupervised Clustering Module with Strict Empirical Archetype Engine.

Provides KMeans and DBSCAN clustering, k-range evaluation (inertia and silhouette),
cluster profiling, empirical archetype derivation from centroid coordinates,
and structured result encapsulation.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score


@dataclass(frozen=True)
class ClusteringResult:
    """Encapsulates clustering models, scores, archetypes, and cluster profiles."""
    k_optimal: int
    kmeans_labels: np.ndarray
    dbscan_labels: np.ndarray
    elbow_inertias: Dict[int, float]
    silhouette_scores: Dict[int, float]
    archetype_labels: Dict[int, str]
    cluster_profiles: pd.DataFrame
    dbscan_n_clusters: int
    dbscan_n_noise: int



def compute_adaptive_k_range(
    n_samples: int,
    min_allowed: int = 2,
    max_allowed: int = 12,
) -> Tuple[int, int, int]:
    """
    Dynamically determines a scale-appropriate candidate cluster range [min_k, max_k]
    and target anchor k based on the dataset sample size N.

    Formula:
        k_target = clip(floor(1.15 * N^0.26), min_allowed + 1, max_allowed - 1)
        min_k = max(min_allowed, k_target - 1)
        max_k = min(n_samples - 1, max_allowed, k_target + 1)

    :param n_samples: Number of samples in dataset.
    :param min_allowed: Absolute floor for min_k (default: 2).
    :param max_allowed: Absolute ceiling for max_k (default: 12).
    :return: (min_k, max_k, target_k)
    """
    if n_samples < 4:
        floor_val = max(1, min_allowed)
        return (floor_val, max(floor_val, n_samples - 1), floor_val)

    target = int(np.clip(
        np.floor(1.15 * (float(n_samples) ** 0.26)),
        min_allowed + 1,
        max_allowed - 1,
    ))

    eff_min = max(min_allowed, target - 1)
    eff_max = min(max_allowed, n_samples - 1, target + 1)

    if eff_min > eff_max:
        eff_min = eff_max

    return (eff_min, eff_max, target)


class AnimeClusterer:
    """
    Handles unsupervised clustering of anime data using KMeans and DBSCAN,
    evaluates optimal cluster counts, and labels clusters into empirical archetypes.
    """

    def __init__(self) -> None:
        self.kmeans_model: Optional[KMeans] = None
        self.dbscan_model: Optional[DBSCAN] = None
        self.elbow_inertias_: Dict[int, float] = {}
        self.silhouette_scores_: Dict[int, float] = {}
        self.k_optimal_: int = 5

    @staticmethod
    def get_adaptive_k_range(n_samples: int) -> Tuple[int, int]:
        """Convenience method returning (min_k, max_k) for n_samples."""
        min_k, max_k, _ = compute_adaptive_k_range(n_samples)
        return (min_k, max_k)

    def evaluate_k_range(
        self,
        X: np.ndarray,
        min_k: Optional[int] = None,
        max_k: Optional[int] = None,
        adaptive: bool = False,
        parsimony_penalty: float = 0.005,
    ) -> Tuple[int, Dict[int, float], Dict[int, float]]:
        """
        Computes inertia and silhouette scores for candidate k values.
        If adaptive=True, automatically determines candidate k range from dataset size N,
        and selects optimal k using a parsimony-penalized silhouette score.
        If adaptive=False, evaluates within [min_k, max_k] (defaults 2..10) and selects highest silhouette.
        """
        X_arr = np.asarray(X)
        n_samples = X_arr.shape[0]

        if adaptive and (min_k is None or max_k is None):
            calc_min, calc_max, target_k = compute_adaptive_k_range(n_samples)
            eff_min_k = min_k if min_k is not None else calc_min
            eff_max_k = max_k if max_k is not None else calc_max
        else:
            eff_min_k = min_k if min_k is not None else 2
            eff_max_k = max_k if max_k is not None else 10
            target_k = 5

        eff_max_k = min(eff_max_k, n_samples - 1) if n_samples > 1 else 0
        eff_min_k = min(eff_min_k, eff_max_k)

        elbow_inertias: Dict[int, float] = {}
        silhouette_scores: Dict[int, float] = {}
        sil_sample_size = min(2500, n_samples) if n_samples > 1000 else None

        if eff_min_k >= 2 and eff_max_k >= eff_min_k:
            for k in range(eff_min_k, eff_max_k + 1):
                km = KMeans(n_clusters=k, random_state=42, n_init="auto")
                km.fit(X_arr)
                elbow_inertias[k] = float(km.inertia_)

                try:
                    labels = km.labels_
                    if len(np.unique(labels)) >= 2:
                        sil = float(
                            silhouette_score(
                                X_arr,
                                labels,
                                sample_size=sil_sample_size,
                                random_state=42,
                            )
                        )
                        silhouette_scores[k] = sil
                except Exception:
                    pass

        if not silhouette_scores:
            optimal_k = min(max(2, target_k), max(2, n_samples - 1))
        elif adaptive and len(silhouette_scores) > 1:
            # Score each candidate k with silhouette and parsimony penalty
            k_keys = sorted(silhouette_scores.keys())
            best_k = k_keys[0]
            best_score = -float("inf")

            for k in k_keys:
                sil = silhouette_scores[k]
                comp_penalty = parsimony_penalty * (k - eff_min_k)
                j_score = sil - comp_penalty
                if j_score > best_score:
                    best_score = j_score
                    best_k = k

            optimal_k = best_k
        else:
            optimal_k = max(silhouette_scores.items(), key=lambda item: item[1])[0]

        self.elbow_inertias_ = elbow_inertias
        self.silhouette_scores_ = silhouette_scores
        self.k_optimal_ = optimal_k

        return optimal_k, elbow_inertias, silhouette_scores

    def fit_kmeans(self, X: np.ndarray, k: int) -> KMeans:
        """Runs KMeans(n_clusters=k, random_state=42, n_init='auto')."""
        X_arr = np.asarray(X)
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        km.fit(X_arr)
        self.kmeans_model = km
        return km

    def fit_dbscan(
        self,
        X: np.ndarray,
        eps: float = 1.2,
        min_samples: int = 4,
    ) -> DBSCAN:
        """Runs DBSCAN with PCA-based dimension reduction for high-dimensional spaces."""
        X_arr = np.asarray(X)
        n_samples, n_features = X_arr.shape
        if n_features > 8 and n_samples > 8:
            from sklearn.decomposition import PCA
            n_comp = min(6, n_samples - 1, n_features)
            X_db = PCA(n_components=n_comp, random_state=42).fit_transform(X_arr)
        else:
            X_db = X_arr
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        dbscan.fit(X_db)
        self.dbscan_model = dbscan
        return dbscan

    @staticmethod
    def _extract_series(
        df: pd.DataFrame,
        candidate_names: List[str],
        default_val: float = 0.0,
    ) -> pd.Series:
        for name in candidate_names:
            if name in df.columns:
                return pd.to_numeric(df[name], errors="coerce").fillna(default_val)
            for col in df.columns:
                if col.lower() == name.lower():
                    return pd.to_numeric(df[col], errors="coerce").fillna(default_val)
        return pd.Series(default_val, index=df.index, dtype=float)

    @staticmethod
    def _extract_top_tokens(series: pd.Series, top_n: int = 3) -> str:
        counter: Counter = Counter()
        for item in series.dropna():
            if isinstance(item, list):
                for token in item:
                    if isinstance(token, str) and token.strip():
                        counter[token.strip()] += 1
                    elif isinstance(token, dict) and "name" in token:
                        counter[str(token["name"]).strip()] += 1
            elif isinstance(item, str):
                for part in item.split(","):
                    clean = part.strip()
                    if clean:
                        counter[clean] += 1
        if counter:
            return ", ".join([token for token, _ in counter.most_common(top_n)])
        return ""

    @staticmethod
    def _derive_empirical_archetype(
        year: float,
        score: float,
        pop: float,
        fav_ratio: float,
        pop_median: float,
        pop_high: float,
        fav_median: float,
        top_genres: str,
        top_tags: str,
    ) -> str:
        """
        Derives an accurate, empirical archetype label from centroid coordinates
        without forcing rigid 1-to-1 bijective Hungarian constraints.
        """
        # 1. Classics: Older median year (<= 2012), high acclaim
        if year <= 2012 and score >= 75.0:
            if fav_ratio >= fav_median * 1.5:
                return "Classics (Legacy Masterworks - High Devotion)"
            return "Classics (Historical Favorites)"

        # 2. Modern Blockbusters: Recent year, top-tier popularity, high score
        if year >= 2017 and pop >= pop_high and score >= 76.0:
            genre_hint = top_genres.split(",")[0] if top_genres else "Action"
            return f"Modern Hits (Blockbuster {genre_hint})"

        # 3. Cult Favorites: High score, passionate favorites ratio, moderate reach
        if score >= 78.0 and fav_ratio >= fav_median * 1.2 and pop < pop_high:
            return "Cult Favorites (Acclaimed Theatrical & Psychological)"

        # 4. Low-Profile / Commercial Mid-Tier: Lower popularity, below-average/modest score
        if score < 74.0 and pop <= pop_median * 1.3:
            return "Low-Profile (Commercial Mid-Tier & Long-Tail)"

        # 5. Contemporary Ensemble / Thematic Hits: Recent, solid popularity, comedy/drama
        if year >= 2018 and score >= 76.0:
            genre_hint = top_genres.split(",")[0] if top_genres else "Ensemble"
            return f"Modern Hits (Contemporary {genre_hint})"

        # 6. Fallback / Niche
        if "Avant Garde" in top_tags or "Surreal" in top_tags or "Short" in top_genres:
            return "Niche / Experimental (Arthouse & Avant-Garde)"

        genre_lead = top_genres.split(",")[0] if top_genres else "General"
        return f"Specialized Archetype ({genre_lead} Focus)"

    def profile_and_label_archetypes(
        self,
        df: pd.DataFrame,
        cluster_labels: np.ndarray,
        feature_names: List[str],
        X: np.ndarray,
    ) -> Tuple[Dict[int, str], pd.DataFrame]:
        """
        Calculates centroids and per-cluster summary stats, deriving
        empirical archetype labels dynamically from centroid dimensions.
        """
        X_arr = np.asarray(X)
        labels_arr = np.asarray(cluster_labels)

        year_s = self._extract_series(
            df, ["seasonYear", "year", "start_year", "release_year", "startYear"], default_val=2015.0
        )
        score_s = self._extract_series(
            df, ["averageScore", "score", "mean_score", "meanScore", "rating"], default_val=70.0
        )
        if score_s.max() <= 10.0 and score_s.max() > 0:
            score_s = score_s * 10.0

        pop_s = self._extract_series(
            df, ["popularity", "members", "user_count"], default_val=1000.0
        )

        if any(c in df.columns for c in ["favorites_ratio", "fav_ratio", "favourites_ratio"]):
            fav_ratio_s = self._extract_series(
                df, ["favorites_ratio", "fav_ratio", "favourites_ratio"], default_val=0.0
            )
        else:
            fav_s = self._extract_series(df, ["favourites", "favorites"], default_val=0.0)
            fav_ratio_s = (fav_s / pop_s.replace(0, np.nan)).fillna(0.0)

        unique_clusters = [c for c in sorted(np.unique(labels_arr)) if c != -1]
        if not unique_clusters:
            unique_clusters = [0]

        stats: Dict[int, Dict[str, Any]] = {}
        genre_col = next((c for c in df.columns if c.lower() in ["genres", "genre"]), None)
        tag_col = next((c for c in df.columns if c.lower() in ["tags", "tag"]), None)

        for cid in unique_clusters:
            mask = labels_arr == cid
            if not np.any(mask):
                continue
            c_year = float(year_s[mask].median())
            c_score = float(score_s[mask].mean())
            c_pop = float(pop_s[mask].mean())
            c_fav = float(fav_ratio_s[mask].mean())
            c_size = int(np.sum(mask))

            top_genres = self._extract_top_tokens(df.loc[mask, genre_col], top_n=3) if genre_col else "Various"
            top_tags = self._extract_top_tokens(df.loc[mask, tag_col], top_n=3) if tag_col else "General"

            stats[cid] = {
                "year": c_year,
                "score": c_score,
                "popularity": c_pop,
                "favorites_ratio": c_fav,
                "size": c_size,
                "top_genres": top_genres or "Various",
                "top_tags": top_tags or "General",
            }

        all_pop = [s["popularity"] for s in stats.values()]
        all_fav = [s["favorites_ratio"] for s in stats.values()]
        pop_median = float(np.median(all_pop)) if all_pop else 1.0
        pop_high = float(np.percentile(all_pop, 70)) if len(all_pop) > 2 else (max(all_pop) * 0.8 if all_pop else 1.0)
        fav_median = float(np.median(all_fav)) if all_fav else 0.01

        archetype_labels: Dict[int, str] = {}
        for cid, s in stats.items():
            archetype_labels[cid] = self._derive_empirical_archetype(
                year=s["year"],
                score=s["score"],
                pop=s["popularity"],
                fav_ratio=s["favorites_ratio"],
                pop_median=pop_median,
                pop_high=pop_high,
                fav_median=fav_median,
                top_genres=s["top_genres"],
                top_tags=s["top_tags"],
            )

        # Disambiguate duplicate archetype labels to guarantee 100% uniqueness
        label_counts = Counter(archetype_labels.values())
        if any(count > 1 for count in label_counts.values()):
            for dup_label, count in label_counts.items():
                if count <= 1:
                    continue
                colliding_cids = [cid for cid, lab in archetype_labels.items() if lab == dup_label]
                for idx, cid in enumerate(colliding_cids):
                    s = stats[cid]
                    tags_list = [t.strip() for t in s["top_tags"].split(",") if t.strip()]
                    genres_list = [g.strip() for g in s["top_genres"].split(",") if g.strip()]

                    diff_trait = ""
                    if len(tags_list) > idx:
                        diff_trait = tags_list[idx]
                    elif len(genres_list) > idx:
                        diff_trait = genres_list[idx]
                    elif tags_list:
                        diff_trait = tags_list[0]
                    else:
                        diff_trait = f"Group {idx + 1}"

                    if s["popularity"] >= pop_high:
                        reach_trait = "High Reach"
                    elif s["popularity"] <= pop_median:
                        reach_trait = "Core Reach"
                    else:
                        reach_trait = "Broad Reach"

                    archetype_labels[cid] = f"{dup_label} [{diff_trait} • {reach_trait}]"

        # Final uniqueness guarantee fallback
        seen_labels: set = set()
        for cid in sorted(archetype_labels.keys()):
            cur = archetype_labels[cid]
            if cur in seen_labels:
                archetype_labels[cid] = f"{cur} (Cluster {cid})"
            seen_labels.add(archetype_labels[cid])

        profile_rows = []
        for cid in sorted(stats.keys()):
            s = stats[cid]
            profile_rows.append({
                "cluster_id": cid,
                "archetype": archetype_labels[cid],
                "size": s["size"],
                "score": round(s["score"], 2),
                "mean_score": s["score"],
                "popularity": round(s["popularity"], 1),
                "mean_popularity": s["popularity"],
                "year": int(round(s["year"])),
                "median_year": s["year"],
                "favorites_ratio": round(s["favorites_ratio"], 4),
                "mean_favorites_ratio": s["favorites_ratio"],
                "top_genres": s["top_genres"],
                "top_tags": s["top_tags"],
            })

        cluster_profiles = pd.DataFrame(profile_rows).sort_values("cluster_id").reset_index(drop=True)
        return archetype_labels, cluster_profiles

    def run_clustering(
        self,
        preprocessed: Any,
        k: Optional[int] = None,
        min_k: Optional[int] = None,
        max_k: Optional[int] = None,
        adaptive_k: bool = False,
        dbscan_eps: float = 1.2,
        dbscan_min_samples: int = 4,
    ) -> ClusteringResult:
        """Executes end-to-end clustering on PreprocessedData."""
        if hasattr(preprocessed, "X"):
            X = preprocessed.X
        elif isinstance(preprocessed, dict) and "X" in preprocessed:
            X = preprocessed["X"]
        elif hasattr(preprocessed, "features"):
            X = preprocessed.features
        else:
            raise ValueError("preprocessed must provide an 'X' or 'features' matrix.")

        if hasattr(preprocessed, "df"):
            df = preprocessed.df
        elif isinstance(preprocessed, dict) and "df" in preprocessed:
            df = preprocessed["df"]
        elif hasattr(preprocessed, "data"):
            df = preprocessed.data
        else:
            raise ValueError("preprocessed must provide a 'df' or 'data' DataFrame.")

        if hasattr(preprocessed, "feature_names"):
            feature_names = list(preprocessed.feature_names)
        elif isinstance(preprocessed, dict) and "feature_names" in preprocessed:
            feature_names = list(preprocessed["feature_names"])
        else:
            feature_names = [f"feat_{i}" for i in range(np.asarray(X).shape[1])]

        X_arr = np.asarray(X)

        opt_k, elbow_inertias, silhouette_scores = self.evaluate_k_range(
            X=X_arr,
            min_k=min_k,
            max_k=max_k,
            adaptive=adaptive_k,
        )
        k_optimal = k if (k is not None and k > 0) else opt_k

        km_model = self.fit_kmeans(X_arr, k=k_optimal)
        kmeans_labels = km_model.labels_

        db_model = self.fit_dbscan(X_arr, eps=dbscan_eps, min_samples=dbscan_min_samples)
        dbscan_labels = db_model.labels_
        dbscan_n_clusters = len(set(dbscan_labels) - {-1})
        dbscan_n_noise = int(np.sum(dbscan_labels == -1))

        archetype_labels, cluster_profiles = self.profile_and_label_archetypes(
            df=df,
            cluster_labels=kmeans_labels,
            feature_names=feature_names,
            X=X_arr,
        )

        return ClusteringResult(
            k_optimal=k_optimal,
            kmeans_labels=kmeans_labels,
            dbscan_labels=dbscan_labels,
            elbow_inertias=elbow_inertias,
            silhouette_scores=silhouette_scores,
            archetype_labels=archetype_labels,
            cluster_profiles=cluster_profiles,
            dbscan_n_clusters=dbscan_n_clusters,
            dbscan_n_noise=dbscan_n_noise,
        )


def run_clustering(
    preprocessed: Any,
    k: Optional[int] = None,
    min_k: Optional[int] = None,
    max_k: Optional[int] = None,
    adaptive_k: bool = False,
    dbscan_eps: float = 1.2,
    dbscan_min_samples: int = 4,
) -> ClusteringResult:
    """Convenience functional wrapper around AnimeClusterer().run_clustering()."""
    clusterer = AnimeClusterer()
    return clusterer.run_clustering(
        preprocessed=preprocessed,
        k=k,
        min_k=min_k,
        max_k=max_k,
        adaptive_k=adaptive_k,
        dbscan_eps=dbscan_eps,
        dbscan_min_samples=dbscan_min_samples,
    )
