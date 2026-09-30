# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 50 anime entries (Current SQLite Local Database: 40,654 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 67 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 5
- **DBSCAN Density Structure**: 4 dense core clusters, 26 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [2, 10]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 2 | 471.91 | 0.1104 |  |
| 3 | 394.03 | 0.1296 |  |
| 4 | 368.51 | 0.0940 |  |
| 5 | 309.97 | 0.1238 | Selected |
| 6 | 285.68 | 0.1205 |  |
| 7 | 272.89 | 0.1180 |  |
| 8 | 238.92 | 0.1761 | Global Maximum |
| 9 | 216.94 | 0.1738 |  |
| 10 | 204.14 | 0.1723 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                     |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                   | top_tags                                       |
|--------------|-----------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|------------------------------|------------------------------------------------|
|            0 | Modern Hits (Blockbuster Action)              |     15 |   83.20 |        83.20 |    712588.50 |         712588.47 |   2019 |       2019.00 |              0.05 |                   0.05 | Action, Drama, Supernatural  | Male Protagonist, Shounen, Tragedy             |
|            1 | Specialized Archetype (Comedy Focus)          |     12 |   81.50 |        81.50 |    574256.50 |         574256.50 |   2016 |       2016.50 |              0.05 |                   0.05 | Comedy, Drama, Romance       | Male Protagonist, Heterosexual, Ensemble Cast  |
|            2 | Classics (Legacy Masterworks - High Devotion) |      8 |   84.50 |        84.50 |    778416.10 |         778416.12 |   2006 |       2006.50 |              0.08 |                   0.08 | Action, Fantasy, Adventure   | Male Protagonist, Shounen, Super Power         |
|            3 | Specialized Archetype (Adventure Focus)       |     12 |   78.34 |        78.34 |    577561.30 |         577561.33 |   2015 |       2015.00 |              0.02 |                   0.02 | Adventure, Action, Comedy    | Male Protagonist, Super Power, Shounen         |
|            4 | Specialized Archetype (Drama Focus)           |      3 |   85.67 |        85.67 |    649730.30 |         649730.33 |   2016 |       2016.00 |              0.06 |                   0.06 | Drama, Romance, Supernatural | Male Protagonist, Tragedy, Primarily Teen Cast |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Modern Hits (Blockbuster Action)
- **Cluster Size**: 15 titles (30.0% of catalog)
- **Median Release Year**: 2019
- **Mean Average Score**: 83.20 / 100
- **Mean Popularity**: 712,588 members
- **Favorites-to-Popularity Ratio**: 0.0454
- **Dominant Genres**: Action, Drama, Supernatural
- **Key Thematic Tags**: Male Protagonist, Shounen, Tragedy
- **Representative Exemplar Titles**: Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, My Hero Academia, One-Punch Man, Tokyo Ghoul

### Cluster 1: Specialized Archetype (Comedy Focus)
- **Cluster Size**: 12 titles (24.0% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 81.50 / 100
- **Mean Popularity**: 574,256 members
- **Favorites-to-Popularity Ratio**: 0.0543
- **Dominant Genres**: Comedy, Drama, Romance
- **Key Thematic Tags**: Male Protagonist, Heterosexual, Ensemble Cast
- **Representative Exemplar Titles**: Assassination Classroom, Re:ZERO -Starting Life in Another World-, Steins;Gate, Black Clover, HAIKYU!!

### Cluster 2: Classics (Legacy Masterworks - High Devotion)
- **Cluster Size**: 8 titles (16.0% of catalog)
- **Median Release Year**: 2006
- **Mean Average Score**: 84.50 / 100
- **Mean Popularity**: 778,416 members
- **Favorites-to-Popularity Ratio**: 0.0835
- **Dominant Genres**: Action, Fantasy, Adventure
- **Key Thematic Tags**: Male Protagonist, Shounen, Super Power
- **Representative Exemplar Titles**: Attack on Titan, Death Note, Hunter x Hunter (2011), ONE PIECE, Fullmetal Alchemist: Brotherhood

### Cluster 3: Specialized Archetype (Adventure Focus)
- **Cluster Size**: 12 titles (24.0% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 78.34 / 100
- **Mean Popularity**: 577,561 members
- **Favorites-to-Popularity Ratio**: 0.0197
- **Dominant Genres**: Adventure, Action, Comedy
- **Key Thematic Tags**: Male Protagonist, Super Power, Shounen
- **Representative Exemplar Titles**: Sword Art Online, My Hero Academia Season 2, Attack on Titan, My Hero Academia Season 3, My Hero Academia

### Cluster 4: Specialized Archetype (Drama Focus)
- **Cluster Size**: 3 titles (6.0% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 85.67 / 100
- **Mean Popularity**: 649,730 members
- **Favorites-to-Popularity Ratio**: 0.0555
- **Dominant Genres**: Drama, Romance, Supernatural
- **Key Thematic Tags**: Male Protagonist, Tragedy, Primarily Teen Cast
- **Representative Exemplar Titles**: A Silent Voice, Your Name., Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train

---

## 4. Latent Space Visualizations & Manifold Projections
High-dimensional representations projected via PCA (2D & 3D) and t-SNE (2D):

---

## 5. Incremental Database Architecture & Fallback Strategy
1. **SQLite Persistent Database (`data/anime_catalog.db`)**: Deduplicates incoming anime by canonical ID (`anilist:{id}`, `kitsu:{id}`), tracking pagination state across runs.
2. **Rate Limit Throttling**: Implements configurable polite delays (`--rate-delay`) to prevent API rate limits or IP bans during large catalog harvests.
3. **Multi-Source Failover**: Queries AniList GraphQL endpoint by default. If AniList is rate-limited, unreachable, or returns insufficient records, queries Kitsu JSON:API, normalizing attributes into the standard schema.
4. **Offline Portability**: The database automatically exports full state to `data/raw_anime_data.json` for offline demonstration.

---
*Report auto-generated by the Antigravity Data Science Pipeline.*