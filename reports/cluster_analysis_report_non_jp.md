# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 50 anime entries (Current SQLite Local Database: 40,654 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 65 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 5
- **DBSCAN Density Structure**: 0 dense core clusters, 50 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [2, 10]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 2 | 442.47 | 0.1635 |  |
| 3 | 406.34 | 0.1396 |  |
| 4 | 346.55 | 0.1642 |  |
| 5 | 307.05 | 0.1452 | Selected |
| 6 | 285.87 | 0.1410 |  |
| 7 | 266.51 | 0.1392 |  |
| 8 | 235.37 | 0.1557 |  |
| 9 | 218.47 | 0.1643 |  |
| 10 | 199.05 | 0.1761 | Global Maximum |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                                                                 |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                    | top_tags                                           |
|--------------|-------------------------------------------------------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|-------------------------------|----------------------------------------------------|
|            0 | Modern Hits (Contemporary Drama)                                                          |     18 |   81.06 |        81.06 |     33776.90 |          33776.89 |   2021 |       2021.00 |              0.03 |                   0.03 | Drama, Fantasy, Action        | Historical, Ancient China, Male Protagonist        |
|            1 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach]             |     16 |   70.25 |        70.25 |     26729.50 |          26729.50 |   2018 |       2018.50 |              0.02 |                   0.02 | Action, Drama, Comedy         | Male Protagonist, Martial Arts, Female Protagonist |
|            2 | Specialized Archetype (Action Focus)                                                      |      3 |   71.67 |        71.67 |    315194.30 |         315194.33 |   2011 |       2011.00 |              0.02 |                   0.02 | Action, Fantasy, Supernatural | Male Protagonist, Demons, Shounen                  |
|            3 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach] (Cluster 3) |      3 |   69.33 |        69.33 |     13583.00 |          13583.00 |   1992 |       1992.00 |              0.02 |                   0.02 | Action, Adventure, Sci-Fi     | Super Power, Male Protagonist, Shounen             |
|            4 | Modern Hits (Blockbuster Drama)                                                           |     10 |   84.60 |        84.60 |    199565.40 |         199565.40 |   2018 |       2018.50 |              0.06 |                   0.06 | Drama, Mystery, Supernatural  | Tragedy, Male Protagonist, Historical              |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Modern Hits (Contemporary Drama)
- **Cluster Size**: 18 titles (36.0% of catalog)
- **Median Release Year**: 2021
- **Mean Average Score**: 81.06 / 100
- **Mean Popularity**: 33,777 members
- **Favorites-to-Popularity Ratio**: 0.0265
- **Dominant Genres**: Drama, Fantasy, Action
- **Key Thematic Tags**: Historical, Ancient China, Male Protagonist
- **Representative Exemplar Titles**: Ya Boy Kongming!, The Apothecary Diaries Season 3, Raven of the Inner Palace, Though I Am an Inept Villainess, Yona of the Dawn OVA

### Cluster 1: Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach]
- **Cluster Size**: 16 titles (32.0% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 70.25 / 100
- **Mean Popularity**: 26,730 members
- **Favorites-to-Popularity Ratio**: 0.0177
- **Dominant Genres**: Action, Drama, Comedy
- **Key Thematic Tags**: Male Protagonist, Martial Arts, Female Protagonist
- **Representative Exemplar Titles**: Kingdom, Hitori no Shita - The Outcast, Lookism, Kingdom Season 2, The Silver Guardian

### Cluster 2: Specialized Archetype (Action Focus)
- **Cluster Size**: 3 titles (6.0% of catalog)
- **Median Release Year**: 2011
- **Mean Average Score**: 71.67 / 100
- **Mean Popularity**: 315,194 members
- **Favorites-to-Popularity Ratio**: 0.0239
- **Dominant Genres**: Action, Fantasy, Supernatural
- **Key Thematic Tags**: Male Protagonist, Demons, Shounen
- **Representative Exemplar Titles**: Blue Exorcist, The Rising of the Shield Hero Season 2, Dragon Ball

### Cluster 3: Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach] (Cluster 3)
- **Cluster Size**: 3 titles (6.0% of catalog)
- **Median Release Year**: 1992
- **Mean Average Score**: 69.33 / 100
- **Mean Popularity**: 13,583 members
- **Favorites-to-Popularity Ratio**: 0.0177
- **Dominant Genres**: Action, Adventure, Sci-Fi
- **Key Thematic Tags**: Super Power, Male Protagonist, Shounen
- **Representative Exemplar Titles**: Dragon Ball: Mystical Adventure, Noblesse: The Beginning of Destruction, Giant Robo the Animation: The Day the Earth Stood Still

### Cluster 4: Modern Hits (Blockbuster Drama)
- **Cluster Size**: 10 titles (20.0% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 84.60 / 100
- **Mean Popularity**: 199,565 members
- **Favorites-to-Popularity Ratio**: 0.0561
- **Dominant Genres**: Drama, Mystery, Supernatural
- **Key Thematic Tags**: Tragedy, Male Protagonist, Historical
- **Representative Exemplar Titles**: Your lie in April, The Apothecary Diaries, Yona of the Dawn, The Apothecary Diaries Season 2, Link Click

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