# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 50 anime entries (Current SQLite Local Database: 40,654 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 68 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 5
- **DBSCAN Density Structure**: 3 dense core clusters, 33 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [2, 10]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 2 | 467.04 | 0.1224 |  |
| 3 | 389.99 | 0.1396 |  |
| 4 | 370.44 | 0.1059 |  |
| 5 | 338.28 | 0.1205 | Selected |
| 6 | 328.89 | 0.1037 |  |
| 7 | 265.67 | 0.1408 |  |
| 8 | 225.76 | 0.1770 |  |
| 9 | 199.59 | 0.1960 | Global Maximum |
| 10 | 196.92 | 0.1830 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                     |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                  | top_tags                                           |
|--------------|-----------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|-----------------------------|----------------------------------------------------|
|            0 | Modern Hits (Blockbuster Drama)               |     18 |   84.00 |        84.00 |    691753.10 |         691753.06 |   2018 |       2017.50 |              0.05 |                   0.05 | Drama, Action, Supernatural | Male Protagonist, Tragedy, Shounen                 |
|            1 | Specialized Archetype (Romance Focus)         |      9 |   79.33 |        79.33 |    577454.70 |         577454.67 |   2016 |       2016.00 |              0.05 |                   0.05 | Romance, Comedy, Fantasy    | Male Protagonist, Heterosexual, Female Protagonist |
|            2 | Classics (Legacy Masterworks - High Devotion) |      6 |   87.33 |        87.33 |    826227.00 |         826227.00 |   2010 |       2010.00 |              0.10 |                   0.10 | Action, Drama, Fantasy      | Tragedy, Male Protagonist, Ensemble Cast           |
|            3 | Specialized Archetype (Action Focus)          |     13 |   79.16 |        79.16 |    594736.60 |         594736.62 |   2016 |       2016.00 |              0.02 |                   0.02 | Action, Adventure, Comedy   | Shounen, Male Protagonist, Super Power             |
|            4 | Classics (Historical Favorites)               |      4 |   80.00 |        80.00 |    613787.50 |         613787.50 |   2006 |       2005.50 |              0.06 |                   0.06 | Action, Adventure, Comedy   | Shounen, Male Protagonist, Super Power             |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Modern Hits (Blockbuster Drama)
- **Cluster Size**: 18 titles (36.0% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 84.00 / 100
- **Mean Popularity**: 691,753 members
- **Favorites-to-Popularity Ratio**: 0.0504
- **Dominant Genres**: Drama, Action, Supernatural
- **Key Thematic Tags**: Male Protagonist, Tragedy, Shounen
- **Representative Exemplar Titles**: Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, One-Punch Man, Tokyo Ghoul, Attack on Titan Season 2

### Cluster 1: Specialized Archetype (Romance Focus)
- **Cluster Size**: 9 titles (18.0% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 79.33 / 100
- **Mean Popularity**: 577,455 members
- **Favorites-to-Popularity Ratio**: 0.0487
- **Dominant Genres**: Romance, Comedy, Fantasy
- **Key Thematic Tags**: Male Protagonist, Heterosexual, Female Protagonist
- **Representative Exemplar Titles**: Sword Art Online, Re:ZERO -Starting Life in Another World-, Rascal Does Not Dream of Bunny Girl Senpai, Kaguya-sama: Love is War, Violet Evergarden

### Cluster 2: Classics (Legacy Masterworks - High Devotion)
- **Cluster Size**: 6 titles (12.0% of catalog)
- **Median Release Year**: 2010
- **Mean Average Score**: 87.33 / 100
- **Mean Popularity**: 826,227 members
- **Favorites-to-Popularity Ratio**: 0.0956
- **Dominant Genres**: Action, Drama, Fantasy
- **Key Thematic Tags**: Tragedy, Male Protagonist, Ensemble Cast
- **Representative Exemplar Titles**: Attack on Titan, Death Note, Hunter x Hunter (2011), ONE PIECE, Fullmetal Alchemist: Brotherhood

### Cluster 3: Specialized Archetype (Action Focus)
- **Cluster Size**: 13 titles (26.0% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 79.16 / 100
- **Mean Popularity**: 594,737 members
- **Favorites-to-Popularity Ratio**: 0.0215
- **Dominant Genres**: Action, Adventure, Comedy
- **Key Thematic Tags**: Shounen, Male Protagonist, Super Power
- **Representative Exemplar Titles**: My Hero Academia, My Hero Academia Season 2, Assassination Classroom, Attack on Titan, My Hero Academia Season 3

### Cluster 4: Classics (Historical Favorites)
- **Cluster Size**: 4 titles (8.0% of catalog)
- **Median Release Year**: 2006
- **Mean Average Score**: 80.00 / 100
- **Mean Popularity**: 613,788 members
- **Favorites-to-Popularity Ratio**: 0.0592
- **Dominant Genres**: Action, Adventure, Comedy
- **Key Thematic Tags**: Shounen, Male Protagonist, Super Power
- **Representative Exemplar Titles**: Naruto, Naruto: Shippuden, Black Clover, Bleach

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