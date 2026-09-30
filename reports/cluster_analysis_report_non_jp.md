# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 2,000 anime entries (Current SQLite Local Database: 40,654 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 76 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 7
- **DBSCAN Density Structure**: 3 dense core clusters, 83 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [7, 9]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 7 | 10147.56 | 0.1898 | Selected |
| 8 | 9906.96 | 0.1593 |  |
| 9 | 9445.21 | 0.1599 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                                                                  |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                 | top_tags                                  |
|--------------|--------------------------------------------------------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|----------------------------|-------------------------------------------|
|            0 | Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach]             |    202 |   60.08 |        60.08 |      1000.00 |           1000.00 |   1980 |       1980.00 |              0.05 |                   0.05 | Movie, Action, Adventure   | chinese animation, kids, shorts           |
|            1 | Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 1) |    629 |   64.44 |        64.44 |      1000.00 |           1000.00 |   2014 |       2014.00 |              0.05 |                   0.05 | Tv, Comedy, Fantasy        | kids, chinese animation, family friendly  |
|            2 | Specialized Archetype (Drama Focus)                                                        |     47 |   78.55 |        78.55 |     83570.30 |          83570.26 |   2016 |       2016.00 |              0.03 |                   0.03 | Drama, Action, Fantasy     | Male Protagonist, Historical, Tragedy     |
|            3 | Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]                       |    453 |   63.60 |        63.60 |      1000.00 |           1000.00 |   2019 |       2019.00 |              0.05 |                   0.05 | Fantasy, Action, Drama     | chinese animation, shorts, fantasy        |
|            4 | Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 4) |    220 |   61.83 |        61.83 |      1003.50 |           1003.46 |   2016 |       2016.00 |              0.05 |                   0.05 | Adventure, Fantasy, Action | chinese animation, kids, adventure        |
|            5 | Specialized Archetype (Fantasy Focus)                                                      |    101 |   70.24 |        70.24 |      3751.00 |           3751.05 |   2016 |       2016.00 |              0.02 |                   0.02 | Fantasy, Action, Adventure | Full CGI, Cultivation, Male Protagonist   |
|            6 | Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Broad Reach]            |    348 |   66.67 |        66.67 |      1043.90 |           1043.85 |   2019 |       2019.00 |              0.05 |                   0.05 | Comedy, Fantasy, Action    | chinese animation, short episodes, comedy |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach]
- **Cluster Size**: 202 titles (10.1% of catalog)
- **Median Release Year**: 1980
- **Mean Average Score**: 60.08 / 100
- **Mean Popularity**: 1,000 members
- **Favorites-to-Popularity Ratio**: 0.0500
- **Dominant Genres**: Movie, Action, Adventure
- **Key Thematic Tags**: chinese animation, kids, shorts
- **Representative Exemplar Titles**: 15 Children Space Adventure, 77 Danui Bimil, A Long He Lili, Agi Gongnyong Doolie, Agi Gongnyong Dooly (1988)

### Cluster 1: Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 1)
- **Cluster Size**: 629 titles (31.4% of catalog)
- **Median Release Year**: 2014
- **Mean Average Score**: 64.44 / 100
- **Mean Popularity**: 1,000 members
- **Favorites-to-Popularity Ratio**: 0.0500
- **Dominant Genres**: Tv, Comedy, Fantasy
- **Key Thematic Tags**: kids, chinese animation, family friendly
- **Representative Exemplar Titles**: 12生肖全家福網絡世界歷險, 12生肖全家福的神奇世界, 23号牛乃糖, 26个秘密, 阿笨猫

### Cluster 2: Specialized Archetype (Drama Focus)
- **Cluster Size**: 47 titles (2.4% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 78.55 / 100
- **Mean Popularity**: 83,570 members
- **Favorites-to-Popularity Ratio**: 0.0338
- **Dominant Genres**: Drama, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Historical, Tragedy
- **Representative Exemplar Titles**: Your lie in April, Blue Exorcist, The Apothecary Diaries, The Rising of the Shield Hero Season 2, Dragon Ball

### Cluster 3: Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]
- **Cluster Size**: 453 titles (22.7% of catalog)
- **Median Release Year**: 2019
- **Mean Average Score**: 63.60 / 100
- **Mean Popularity**: 1,000 members
- **Favorites-to-Popularity Ratio**: 0.0500
- **Dominant Genres**: Fantasy, Action, Drama
- **Key Thematic Tags**: chinese animation, shorts, fantasy
- **Representative Exemplar Titles**: I=Fantasy, (Mi)Liu, (OO), 12월, 15-fun de Wakaru: Kami no Tou

### Cluster 4: Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 4)
- **Cluster Size**: 220 titles (11.0% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 61.83 / 100
- **Mean Popularity**: 1,004 members
- **Favorites-to-Popularity Ratio**: 0.0499
- **Dominant Genres**: Adventure, Fantasy, Action
- **Key Thematic Tags**: chinese animation, kids, adventure
- **Representative Exemplar Titles**: Thunderbolt Fantasy - Bewitching Melody of the West, 81号农场之保卫麦咭, 81 Hao Nongchang: Fengkuang De Mai Ji, '84 Taekwon V, A Tang Qiyu

### Cluster 5: Specialized Archetype (Fantasy Focus)
- **Cluster Size**: 101 titles (5.1% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 70.24 / 100
- **Mean Popularity**: 3,751 members
- **Favorites-to-Popularity Ratio**: 0.0232
- **Dominant Genres**: Fantasy, Action, Adventure
- **Key Thematic Tags**: Full CGI, Cultivation, Male Protagonist
- **Representative Exemplar Titles**: The Silver Guardian, TO BE HERO, To Be Heroine, Dragon Ball: Mystical Adventure, Noblesse: The Beginning of Destruction

### Cluster 6: Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Broad Reach]
- **Cluster Size**: 348 titles (17.4% of catalog)
- **Median Release Year**: 2019
- **Mean Average Score**: 66.67 / 100
- **Mean Popularity**: 1,044 members
- **Favorites-to-Popularity Ratio**: 0.0501
- **Dominant Genres**: Comedy, Fantasy, Action
- **Key Thematic Tags**: chinese animation, short episodes, comedy
- **Representative Exemplar Titles**: Swallowed Star, Soul Land 2: The Peerless Tang Clan, Tunshi Xingkong 2, Dou Po Cangqiong: San Nian Zhi Yue, Jade Dynasty

---

## 4. Latent Space Visualizations & Manifold Projections
High-dimensional representations projected via PCA (2D & 3D) and t-SNE (2D):

### Elbow Silhouette
![Elbow Silhouette](figures_non_jp/elbow_silhouette.png)

### Pca 2D
![Pca 2D](figures_non_jp/pca_2d.png)

### Pca 3D
![Pca 3D](figures_non_jp/pca_3d.png)

### Tsne 2D
![Tsne 2D](figures_non_jp/tsne_2d.png)

### Cluster Heatmap
![Cluster Heatmap](figures_non_jp/cluster_heatmap.png)

---

## 5. Incremental Database Architecture & Fallback Strategy
1. **SQLite Persistent Database (`data/anime_catalog.db`)**: Deduplicates incoming anime by canonical ID (`anilist:{id}`, `kitsu:{id}`), tracking pagination state across runs.
2. **Rate Limit Throttling**: Implements configurable polite delays (`--rate-delay`) to prevent API rate limits or IP bans during large catalog harvests.
3. **Multi-Source Failover**: Queries AniList GraphQL endpoint by default. If AniList is rate-limited, unreachable, or returns insufficient records, queries Kitsu JSON:API, normalizing attributes into the standard schema.
4. **Offline Portability**: The database automatically exports full state to `data/raw_anime_data.json` for offline demonstration.

---
*Report auto-generated by the Antigravity Data Science Pipeline.*