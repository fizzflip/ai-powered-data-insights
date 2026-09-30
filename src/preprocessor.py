"""
Data preprocessing module for anime unsupervised clustering.

Handles missing value imputation, feature engineering, categorical encoding,
tag text vectorization, continuous feature scaling, and dense matrix assembly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, List, Optional, Set

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class PreprocessedData:
    """
    Immutable container holding preprocessed anime data and artifacts.

    Attributes:
        df: DataFrame containing metadata and cleaned raw features:
            id, title, seasonYear, averageScore, popularity, favourites,
            episodes, duration, genres, tags, source, season, studio,
            recency, favorites_ratio.
        X: 2D float64 feature matrix for clustering.
        feature_names: List of all column names corresponding to columns in X.
        scaler: Fitted StandardScaler used for continuous numerical features.
        tfidf: Fitted TfidfVectorizer used for anime tags.
        numerical_features: Names of standardized continuous numerical features.
        genre_features: Names of multi-label binary genre indicator features.
        tag_features: Names of TF-IDF tag features.
    """

    df: pd.DataFrame
    X: np.ndarray
    feature_names: List[str]
    scaler: StandardScaler
    tfidf: TfidfVectorizer
    numerical_features: List[str]
    genre_features: List[str]
    tag_features: List[str]

    @property
    def categorical_features(self) -> List[str]:
        """Names of one-hot encoded categorical features (source, season)."""
        excluded = set(self.numerical_features + self.genre_features + self.tag_features)
        return [f for f in self.feature_names if f not in excluded]


def _extract_title(val: Any) -> str:
    """Extract string title from string or dictionary format."""
    if isinstance(val, dict):
        return (
            val.get("english")
            or val.get("romaji")
            or val.get("native")
            or "Unknown Title"
        )
    if pd.isna(val) or val is None:
        return "Unknown Title"
    s = str(val).strip()
    return s if s else "Unknown Title"


def _extract_studio(val: Any) -> str:
    """Extract studio name from string, dict, or list representation."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "UNKNOWN"
    if isinstance(val, dict):
        if "name" in val and val["name"]:
            return str(val["name"]).strip()
        nodes = val.get("nodes")
        if isinstance(nodes, list) and len(nodes) > 0 and isinstance(nodes[0], dict):
            name = nodes[0].get("name")
            if name:
                return str(name).strip()
        return "UNKNOWN"
    if isinstance(val, list):
        if len(val) > 0:
            first = val[0]
            if isinstance(first, dict):
                return str(first.get("name", "UNKNOWN")).strip()
            return str(first).strip()
        return "UNKNOWN"
    s = str(val).strip()
    return s if s else "UNKNOWN"


def _extract_genres(val: Any) -> List[str]:
    """Parse genres into a list of clean string genre labels."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return []
    if isinstance(val, (list, tuple, set)):
        return [str(g).strip() for g in val if g and str(g).strip()]
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return []
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(g).strip() for g in parsed if g and str(g).strip()]
            except Exception:
                pass
        return [g.strip() for g in s.split(",") if g.strip()]
    return [str(val).strip()]


def _extract_tags(val: Any) -> List[str]:
    """Extract tag name strings from list of dicts, strings, or JSON."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return []
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return []
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                return _extract_tags(parsed)
            except Exception:
                pass
        return [t.strip() for t in s.split(",") if t.strip()]
    if isinstance(val, (list, tuple)):
        tags: List[str] = []
        for item in val:
            if isinstance(item, dict):
                name = item.get("name")
                if name:
                    tags.append(str(name).strip())
            elif isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    tags.append(cleaned)
            elif item is not None:
                cleaned = str(item).strip()
                if cleaned:
                    tags.append(cleaned)
        return tags
    return [str(val).strip()]


class DataPreprocessor:
    """
    Data preprocessor for anime dataset.

    Imputes missing values, engineers recency and popularity features,
    standardizes continuous features, one-hot encodes categorical features,
    binary encodes genres, vectorizes tags using TF-IDF, and stacks into a
    dense feature matrix.
    """

    DEFAULT_NUMERICAL_FEATURES = [
        "averageScore",
        "log_popularity",
        "log_favourites",
        "log_episodes",
        "duration",
        "recency",
        "favorites_ratio",
    ]

    REQUIRED_RAW_METADATA_COLS = [
        "id",
        "title",
        "seasonYear",
        "averageScore",
        "popularity",
        "favourites",
        "episodes",
        "duration",
        "genres",
        "tags",
        "source",
        "season",
        "studio",
        "recency",
        "favorites_ratio",
    ]

    def __init__(
        self,
        top_n_sources: int = 5,
        max_tag_features: int = 35,
        min_tag_df: int = 2,
        numerical_features: Optional[List[str]] = None,
    ) -> None:
        self.top_n_sources = top_n_sources
        self.max_tag_features = max_tag_features
        self.min_tag_df = min_tag_df
        self.numerical_features = (
            list(numerical_features)
            if numerical_features is not None
            else list(self.DEFAULT_NUMERICAL_FEATURES)
        )

        self.medians_: dict[str, float] = {}
        self.min_year_: float = 2000.0
        self.max_year_: float = 2024.0
        self.top_sources_: Set[str] = set()

        self.scaler: StandardScaler = StandardScaler()
        self.one_hot_encoder: OneHotEncoder = OneHotEncoder(
            handle_unknown="ignore", sparse_output=False
        )
        self.mlb: MultiLabelBinarizer = MultiLabelBinarizer()
        self.tfidf: TfidfVectorizer = TfidfVectorizer(
            max_features=self.max_tag_features,
            stop_words="english",
            min_df=self.min_tag_df,
        )

        self.categorical_features: List[str] = []
        self.genre_features: List[str] = []
        self.tag_features: List[str] = []
        self.feature_names: List[str] = []
        self._is_fitted: bool = False

    def _prepare_cleaned_df(self, df: pd.DataFrame, is_fit: bool = False) -> pd.DataFrame:
        """Impute missing values and perform feature engineering."""
        df_clean = df.copy()
        n_rows = len(df_clean)

        if "id" not in df_clean.columns:
            df_clean["id"] = list(range(n_rows))
        if "title" not in df_clean.columns:
            df_clean["title"] = "Unknown Title"
        else:
            df_clean["title"] = df_clean["title"].apply(_extract_title)

        if "studio" not in df_clean.columns:
            df_clean["studio"] = "UNKNOWN"
        else:
            df_clean["studio"] = df_clean["studio"].apply(_extract_studio)

        if "source" not in df_clean.columns:
            df_clean["source"] = "UNKNOWN"
        else:
            df_clean["source"] = df_clean["source"].fillna("UNKNOWN").astype(str).str.strip()
            df_clean.loc[df_clean["source"] == "", "source"] = "UNKNOWN"

        if "season" not in df_clean.columns:
            df_clean["season"] = "UNKNOWN"
        else:
            df_clean["season"] = df_clean["season"].fillna("UNKNOWN").astype(str).str.strip().str.upper()
            df_clean.loc[df_clean["season"] == "", "season"] = "UNKNOWN"

        if "genres" not in df_clean.columns:
            df_clean["genres"] = [[] for _ in range(n_rows)]
        else:
            df_clean["genres"] = df_clean["genres"].apply(_extract_genres)

        if "tags" not in df_clean.columns:
            df_clean["tags"] = [[] for _ in range(n_rows)]
        else:
            df_clean["tags"] = df_clean["tags"].apply(_extract_tags)

        num_impute_cols = {
            "averageScore": 65.0,
            "episodes": 12.0,
            "duration": 24.0,
            "seasonYear": 2020.0,
        }
        for col, default_val in num_impute_cols.items():
            if col not in df_clean.columns:
                df_clean[col] = default_val
            else:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

            if is_fit:
                median = df_clean[col].median()
                self.medians_[col] = float(median) if not pd.isna(median) else default_val

            df_clean[col] = df_clean[col].fillna(self.medians_.get(col, default_val))

        for col in ["popularity", "favourites"]:
            if col not in df_clean.columns:
                df_clean[col] = 0.0
            else:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0.0)

        if is_fit:
            self.min_year_ = float(df_clean["seasonYear"].min())
            self.max_year_ = float(df_clean["seasonYear"].max())

        # Feature engineering
        df_clean["log_popularity"] = np.log1p(df_clean["popularity"].clip(lower=0.0))
        df_clean["log_favourites"] = np.log1p(df_clean["favourites"].clip(lower=0.0))
        df_clean["log_episodes"] = np.log1p(df_clean["episodes"].clip(lower=0.0))

        year_denom = (self.max_year_ - self.min_year_) + 1e-6
        df_clean["recency"] = (df_clean["seasonYear"] - self.min_year_) / year_denom
        df_clean["favorites_ratio"] = df_clean["favourites"] / (df_clean["popularity"] + 1.0)

        # Origin classification annotation
        if "origin_cohort" not in df_clean.columns or "sub_origin" not in df_clean.columns:
            from src.origin_classifier import classify_anime_origin

            # Fast path: vectorized check if is_jp is present and valid
            if "is_jp" in df_clean.columns and df_clean["is_jp"].notna().all():
                is_jp_arr = pd.to_numeric(df_clean["is_jp"], errors="coerce").fillna(1).astype(int).to_numpy()
                df_clean["origin_cohort"] = np.where(is_jp_arr == 1, "jp", "non-jp")
                country_col = df_clean.get("country_code")
                if country_col is not None:
                    fallback_country = np.where(is_jp_arr == 1, "JP", "OTHER")
                    df_clean["sub_origin"] = country_col.fillna(pd.Series(fallback_country, index=df_clean.index)).astype(str)
                else:
                    df_clean["sub_origin"] = np.where(is_jp_arr == 1, "JP", "OTHER")
            else:
                cohorts: List[str] = []
                suborigins: List[str] = []
                # Fast iteration using to_dict('records') avoiding expensive pd.Series per-row overhead of iterrows()
                records_list = df_clean.to_dict(orient="records")
                for row_dict in records_list:
                    cohort_val = row_dict.get("origin_cohort")
                    sub_val = row_dict.get("sub_origin")
                    is_jp_val = row_dict.get("is_jp")

                    if cohort_val and str(cohort_val) in ("jp", "non-jp"):
                        cohorts.append(str(cohort_val))
                        suborigins.append(str(sub_val) if sub_val else ("JP" if cohort_val == "jp" else "OTHER"))
                    elif is_jp_val is not None and not pd.isna(is_jp_val):
                        is_jp_int = int(is_jp_val)
                        cohorts.append("jp" if is_jp_int == 1 else "non-jp")
                        suborigins.append(str(row_dict.get("country_code") or ("JP" if is_jp_int == 1 else "OTHER")))
                    else:
                        res = classify_anime_origin(row_dict)
                        cohorts.append(res.origin_cohort)
                        suborigins.append(res.sub_origin)

                df_clean["origin_cohort"] = cohorts
                df_clean["sub_origin"] = suborigins

        return df_clean

    def _fit_transformers_from_cleaned(self, df_clean: pd.DataFrame) -> None:
        """Fit all transformers on pre-cleaned DataFrame."""
        X_num = df_clean[self.numerical_features].to_numpy(dtype=np.float64)
        self.scaler.fit(X_num)

        top_srcs = (
            df_clean["source"]
            .value_counts()
            .nlargest(self.top_n_sources)
            .index.tolist()
        )
        self.top_sources_ = set(top_srcs)
        self.top_sources_.add("OTHER")

        binned_source = df_clean["source"].apply(
            lambda s: s if s in self.top_sources_ else "OTHER"
        )
        cat_df = pd.DataFrame({
            "source": binned_source,
            "season": df_clean["season"],
        })
        self.one_hot_encoder.fit(cat_df)
        self.categorical_features = list(
            self.one_hot_encoder.get_feature_names_out(["source", "season"])
        )

        self.mlb.fit(df_clean["genres"])
        self.genre_features = [f"genre_{g}" for g in self.mlb.classes_]

        combined_tags = [" ".join(t) for t in df_clean["tags"]]
        non_empty_docs = [doc for doc in combined_tags if doc.strip()]
        effective_min_df = (
            self.min_tag_df if len(non_empty_docs) >= self.min_tag_df else 1
        )
        self.tfidf = TfidfVectorizer(
            max_features=self.max_tag_features,
            stop_words="english",
            min_df=effective_min_df,
        )
        try:
            self.tfidf.fit(combined_tags)
            self.tag_features = [f"tag_{t}" for t in self.tfidf.get_feature_names_out()]
        except ValueError:
            self.tag_features = []

        self.feature_names = (
            list(self.numerical_features)
            + list(self.categorical_features)
            + list(self.genre_features)
            + list(self.tag_features)
        )
        self._is_fitted = True

    def _transform_from_cleaned(self, df_clean: pd.DataFrame) -> PreprocessedData:
        """Transform pre-cleaned DataFrame using fitted transformers."""
        n_rows = len(df_clean)

        X_num = self.scaler.transform(df_clean[self.numerical_features].to_numpy(dtype=np.float64))

        binned_source = df_clean["source"].apply(
            lambda s: s if s in self.top_sources_ else "OTHER"
        )
        cat_df = pd.DataFrame({
            "source": binned_source,
            "season": df_clean["season"],
        })
        X_cat = self.one_hot_encoder.transform(cat_df).astype(np.float64)

        if len(self.mlb.classes_) > 0:
            X_genre = self.mlb.transform(df_clean["genres"]).astype(np.float64)
        else:
            X_genre = np.zeros((n_rows, 0), dtype=np.float64)

        combined_tags = [" ".join(t) for t in df_clean["tags"]]
        if hasattr(self.tfidf, "vocabulary_") and len(self.tfidf.vocabulary_) > 0:
            X_tag = self.tfidf.transform(combined_tags).toarray().astype(np.float64)
        else:
            X_tag = np.zeros((n_rows, 0), dtype=np.float64)

        matrices = [X_num, X_cat, X_genre, X_tag]
        non_empty_matrices = [m for m in matrices if m.shape[1] > 0]
        if non_empty_matrices:
            X = np.hstack(non_empty_matrices).astype(np.float64)
        else:
            X = np.zeros((n_rows, 0), dtype=np.float64)

        extra_cols = [c for c in df_clean.columns if c not in self.REQUIRED_RAW_METADATA_COLS]
        final_cols = self.REQUIRED_RAW_METADATA_COLS + extra_cols
        ordered_df = df_clean[[c for c in final_cols if c in df_clean.columns]].copy()

        return PreprocessedData(
            df=ordered_df,
            X=X,
            feature_names=list(self.feature_names),
            scaler=self.scaler,
            tfidf=self.tfidf,
            numerical_features=list(self.numerical_features),
            genre_features=list(self.genre_features),
            tag_features=list(self.tag_features),
        )

    def fit(self, df: pd.DataFrame) -> "DataPreprocessor":
        """Fit all transformers and imputation values on input DataFrame."""
        df_clean = self._prepare_cleaned_df(df, is_fit=True)
        self._fit_transformers_from_cleaned(df_clean)
        return self

    def transform(self, df: pd.DataFrame) -> PreprocessedData:
        """Transform input DataFrame into PreprocessedData."""
        if not self._is_fitted:
            raise RuntimeError("DataPreprocessor must be fitted before calling transform().")

        df_clean = self._prepare_cleaned_df(df, is_fit=False)
        return self._transform_from_cleaned(df_clean)

    def fit_transform(self, df: pd.DataFrame) -> PreprocessedData:
        """Fit and transform input DataFrame in one single pass."""
        df_clean = self._prepare_cleaned_df(df, is_fit=True)
        self._fit_transformers_from_cleaned(df_clean)
        return self._transform_from_cleaned(df_clean)

    def preprocess(self, df: pd.DataFrame) -> PreprocessedData:
        """Alias for fit_transform."""
        return self.fit_transform(df)
