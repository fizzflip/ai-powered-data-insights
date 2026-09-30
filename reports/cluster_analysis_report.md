# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 500 anime entries (Current SQLite Local Database: 40,654 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 73 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 5
- **DBSCAN Density Structure**: 3 dense core clusters, 99 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [2, 10]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 2 | 4836.75 | 0.1545 |  |
| 3 | 4099.22 | 0.1767 | Global Maximum |
| 4 | 3839.22 | 0.1078 |  |
| 5 | 3637.32 | 0.1134 | Selected |
| 6 | 3511.35 | 0.1067 |  |
| 7 | 3362.43 | 0.1003 |  |
| 8 | 3198.98 | 0.1194 |  |
| 9 | 3146.70 | 0.1183 |  |
| 10 | 3037.21 | 0.1202 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                     |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                  | top_tags                                      |
|--------------|-----------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|-----------------------------|-----------------------------------------------|
|            0 | Modern Hits (Contemporary Drama)              |    176 |   80.41 |        80.41 |    244923.70 |         244923.69 |   2020 |       2020.00 |              0.03 |                   0.03 | Drama, Comedy, Action       | Male Protagonist, Heterosexual, Ensemble Cast |
|            1 | Low-Profile (Commercial Mid-Tier & Long-Tail) |    155 |   71.39 |        71.39 |    210790.20 |         210790.17 |   2016 |       2016.00 |              0.02 |                   0.02 | Action, Comedy, Fantasy     | Male Protagonist, Heterosexual, School        |
|            2 | Modern Hits (Blockbuster Action)              |     91 |   81.78 |        81.78 |    521807.80 |         521807.82 |   2017 |       2017.00 |              0.05 |                   0.05 | Action, Drama, Supernatural | Male Protagonist, Tragedy, Ensemble Cast      |
|            3 | Specialized Archetype (Drama Focus)           |     47 |   82.31 |        82.31 |    259890.70 |         259890.74 |   2017 |       2017.00 |              0.04 |                   0.04 | Drama, Fantasy, Action      | Female Protagonist, Male Protagonist, Tragedy |
|            4 | Classics (Legacy Masterworks - High Devotion) |     31 |   81.39 |        81.39 |    293789.00 |         293789.03 |   2002 |       2002.00 |              0.05 |                   0.05 | Action, Comedy, Adventure   | Male Protagonist, Philosophy, Tragedy         |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Modern Hits (Contemporary Drama)
- **Cluster Size**: 176 titles (35.2% of catalog)
- **Median Release Year**: 2020
- **Mean Average Score**: 80.41 / 100
- **Mean Popularity**: 244,924 members
- **Favorites-to-Popularity Ratio**: 0.0332
- **Dominant Genres**: Drama, Comedy, Action
- **Key Thematic Tags**: Male Protagonist, Heterosexual, Ensemble Cast
- **Representative Exemplar Titles**: My Hero Academia, My Hero Academia Season 2, My Hero Academia Season 3, One-Punch Man Season 2, Kakegurui

### Cluster 1: Low-Profile (Commercial Mid-Tier & Long-Tail)
- **Cluster Size**: 155 titles (31.0% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 71.39 / 100
- **Mean Popularity**: 210,790 members
- **Favorites-to-Popularity Ratio**: 0.0166
- **Dominant Genres**: Action, Comedy, Fantasy
- **Key Thematic Tags**: Male Protagonist, Heterosexual, School
- **Representative Exemplar Titles**: Blue Exorcist, Sword Art Online II, The Future Diary, Tokyo Ghoul √A, The Devil is a Part-Timer!

### Cluster 2: Modern Hits (Blockbuster Action)
- **Cluster Size**: 91 titles (18.2% of catalog)
- **Median Release Year**: 2017
- **Mean Average Score**: 81.78 / 100
- **Mean Popularity**: 521,808 members
- **Favorites-to-Popularity Ratio**: 0.0497
- **Dominant Genres**: Action, Drama, Supernatural
- **Key Thematic Tags**: Male Protagonist, Tragedy, Ensemble Cast
- **Representative Exemplar Titles**: Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, Death Note, My Hero Academia

### Cluster 3: Specialized Archetype (Drama Focus)
- **Cluster Size**: 47 titles (9.4% of catalog)
- **Median Release Year**: 2017
- **Mean Average Score**: 82.31 / 100
- **Mean Popularity**: 259,891 members
- **Favorites-to-Popularity Ratio**: 0.0356
- **Dominant Genres**: Drama, Fantasy, Action
- **Key Thematic Tags**: Female Protagonist, Male Protagonist, Tragedy
- **Representative Exemplar Titles**: A Silent Voice, Your Name., Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, Spirited Away, JUJUTSU KAISEN 0

### Cluster 4: Classics (Legacy Masterworks - High Devotion)
- **Cluster Size**: 31 titles (6.2% of catalog)
- **Median Release Year**: 2002
- **Mean Average Score**: 81.39 / 100
- **Mean Popularity**: 293,789 members
- **Favorites-to-Popularity Ratio**: 0.0540
- **Dominant Genres**: Action, Comedy, Adventure
- **Key Thematic Tags**: Male Protagonist, Philosophy, Tragedy
- **Representative Exemplar Titles**: Naruto, Naruto: Shippuden, Bleach, Neon Genesis Evangelion, Cowboy Bebop

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