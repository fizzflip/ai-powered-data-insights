"""
Unit tests for unsupervised clustering module (KMeans, DBSCAN, and archetype mapping).
"""

import numpy as np
import pandas as pd
import pytest
from src.clustering import AnimeClusterer, ClusteringResult
from src.data_fetcher import MOCK_ANIME_DATA
from src.preprocessor import DataPreprocessor


@pytest.fixture
def preprocessed_fixture():
    df_raw = pd.DataFrame(MOCK_ANIME_DATA)
    preprocessor = DataPreprocessor()
    return preprocessor.fit_transform(df_raw)


def test_kmeans_and_archetypes(preprocessed_fixture):
    """Verify KMeans produces valid clusters, inertia, and mapped archetypes."""
    clusterer = AnimeClusterer()
    result = clusterer.run_clustering(preprocessed_fixture, k=5)

    assert isinstance(result, ClusteringResult)
    assert result.k_optimal == 5
    assert len(result.kmeans_labels) == len(preprocessed_fixture.df)
    assert len(set(result.kmeans_labels)) == 5
    assert len(result.archetype_labels) == 5
    assert len(result.cluster_profiles) == 5

    # Check that inertia and silhouette dictionaries have values
    assert len(result.elbow_inertias) > 0
    assert len(result.silhouette_scores) > 0


def test_dbscan_execution(preprocessed_fixture):
    """Verify DBSCAN fits without error and outputs label array."""
    clusterer = AnimeClusterer()
    dbscan_model = clusterer.fit_dbscan(preprocessed_fixture.X, eps=2.5, min_samples=2)
    assert len(dbscan_model.labels_) == len(preprocessed_fixture.df)
