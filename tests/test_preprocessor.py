"""
Unit tests for data preprocessing and feature engineering.
"""

import numpy as np
import pandas as pd
import pytest
from src.data_fetcher import MOCK_ANIME_DATA
from src.preprocessor import DataPreprocessor, PreprocessedData


def test_preprocessor_output_structure():
    """Verify preprocessor produces correct PreprocessedData shapes and types."""
    df_raw = pd.DataFrame(MOCK_ANIME_DATA)
    preprocessor = DataPreprocessor()
    result = preprocessor.fit_transform(df_raw)

    assert isinstance(result, PreprocessedData)
    assert isinstance(result.X, np.ndarray)
    assert result.X.dtype == np.float64
    assert result.X.shape[0] == len(df_raw)
    assert result.X.shape[1] == len(result.feature_names)
    assert not np.isnan(result.X).any(), "Feature matrix contains NaNs"


def test_preprocessor_recency_and_ratios():
    """Verify engineered features like recency and favorites_ratio exist and are valid."""
    df_raw = pd.DataFrame(MOCK_ANIME_DATA)
    preprocessor = DataPreprocessor()
    result = preprocessor.fit_transform(df_raw)

    assert "recency" in result.df.columns
    assert "favorites_ratio" in result.df.columns
    assert (result.df["recency"] >= 0.0).all()
    assert (result.df["recency"] <= 1.0 + 1e-5).all()
    assert (result.df["favorites_ratio"] >= 0.0).all()


def test_preprocessor_missing_value_handling():
    """Verify preprocessor imputes missing numerical and categorical values."""
    messy_data = [
        {"id": 101, "title": "Test Incomplete", "averageScore": None, "episodes": None},
        {"id": 102, "title": "Test 2", "seasonYear": None, "source": None},
    ]
    df_messy = pd.DataFrame(messy_data)
    preprocessor = DataPreprocessor()
    result = preprocessor.fit_transform(df_messy)

    assert not np.isnan(result.X).any()
    assert result.df["averageScore"].isna().sum() == 0
    assert result.df["seasonYear"].isna().sum() == 0
