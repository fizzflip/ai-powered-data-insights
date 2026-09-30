# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 1,998 anime entries (Current SQLite Local Database: 1,998 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 73 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 5
- **DBSCAN Density Structure**: 14 dense core clusters, 116 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [2, 10]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 2 | 18836.54 | 0.1737 |  |
| 3 | 16072.76 | 0.1928 | Global Maximum |
| 4 | 15062.15 | 0.1190 |  |
| 5 | 14484.68 | 0.1060 | Selected |
| 6 | 13990.26 | 0.0963 |  |
| 7 | 13604.50 | 0.0961 |  |
| 8 | 13245.62 | 0.0903 |  |
| 9 | 12927.95 | 0.0857 |  |
| 10 | 12617.16 | 0.0825 |  |

> [!NOTE]
> **Empirical vs. Global Silhouette Tradeoff**: While mathematical silhouette score peaks at lower $k$ (e.g. $k=3$), evaluating $k=5$ yields balanced domain granularities separating Historical Classics, Modern Shounen Blockbusters, Contemporary Ensemble Hits, Cult Acclaim, and Low-Profile productions without over-merging.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                     |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres               | top_tags                                           |
|--------------|-----------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|--------------------------|----------------------------------------------------|
|            0 | Low-Profile (Commercial Mid-Tier & Long-Tail) |    639 |   67.65 |        67.65 |     91904.80 |          91904.83 |   2018 |       2018.00 |              0.01 |                   0.01 | Comedy, Action, Fantasy  | Male Protagonist, Heterosexual, School             |
|            1 | Modern Hits (Contemporary Comedy)             |    626 |   76.49 |        76.49 |    160458.10 |         160458.08 |   2018 |       2018.00 |              0.02 |                   0.02 | Comedy, Action, Drama    | Male Protagonist, Heterosexual, Female Protagonist |
|            2 | Modern Hits (Blockbuster Drama)               |    414 |   81.08 |        81.08 |    349494.10 |         349494.13 |   2019 |       2019.00 |              0.04 |                   0.04 | Drama, Action, Comedy    | Male Protagonist, Tragedy, Ensemble Cast           |
|            3 | Specialized Archetype (Drama Focus)           |    216 |   79.54 |        79.54 |    158347.90 |         158347.94 |   2016 |       2016.00 |              0.03 |                   0.03 | Drama, Action, Fantasy   | Male Protagonist, Female Protagonist, Tragedy      |
|            4 | Classics (Legacy Masterworks - High Devotion) |    103 |   82.60 |        82.60 |    343116.00 |         343115.99 |   2004 |       2004.00 |              0.06 |                   0.06 | Action, Drama, Adventure | Male Protagonist, Tragedy, Philosophy              |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Low-Profile (Commercial Mid-Tier & Long-Tail)
- **Cluster Size**: 639 titles (32.0% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 67.65 / 100
- **Mean Popularity**: 91,905 members
- **Favorites-to-Popularity Ratio**: 0.0142
- **Dominant Genres**: Comedy, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Heterosexual, School
- **Representative Exemplar Titles**: The Promised Neverland Season 2, The Rising of the Shield Hero Season 2, Tokyo Ghoul:re 2, Boruto: Naruto Next Generations, How NOT to Summon a Demon Lord

### Cluster 1: Modern Hits (Contemporary Comedy)
- **Cluster Size**: 626 titles (31.3% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 76.49 / 100
- **Mean Popularity**: 160,458 members
- **Favorites-to-Popularity Ratio**: 0.0230
- **Dominant Genres**: Comedy, Action, Drama
- **Key Thematic Tags**: Male Protagonist, Heterosexual, Female Protagonist
- **Representative Exemplar Titles**: My Hero Academia Season 2, One Punch Man, My Hero Academia Season 3, Sword Art Online II, Tokyo Ghoul √A

### Cluster 2: Modern Hits (Blockbuster Drama)
- **Cluster Size**: 414 titles (20.7% of catalog)
- **Median Release Year**: 2019
- **Mean Average Score**: 81.08 / 100
- **Mean Popularity**: 349,494 members
- **Favorites-to-Popularity Ratio**: 0.0406
- **Dominant Genres**: Drama, Action, Comedy
- **Key Thematic Tags**: Male Protagonist, Tragedy, Ensemble Cast
- **Representative Exemplar Titles**: Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, My Hero Academia, One-Punch Man, Tokyo Ghoul

### Cluster 3: Specialized Archetype (Drama Focus)
- **Cluster Size**: 216 titles (10.8% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 79.54 / 100
- **Mean Popularity**: 158,348 members
- **Favorites-to-Popularity Ratio**: 0.0288
- **Dominant Genres**: Drama, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Tragedy
- **Representative Exemplar Titles**: A Silent Voice, Your Name., Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, Spirited Away, JUJUTSU KAISEN 0

### Cluster 4: Classics (Legacy Masterworks - High Devotion)
- **Cluster Size**: 103 titles (5.2% of catalog)
- **Median Release Year**: 2004
- **Mean Average Score**: 82.60 / 100
- **Mean Popularity**: 343,116 members
- **Favorites-to-Popularity Ratio**: 0.0608
- **Dominant Genres**: Action, Drama, Adventure
- **Key Thematic Tags**: Male Protagonist, Tragedy, Philosophy
- **Representative Exemplar Titles**: Attack on Titan, Death Note, Hunter x Hunter (2011), ONE PIECE, Fullmetal Alchemist: Brotherhood

---

## 4. Latent Space Visualizations & Manifold Projections
High-dimensional representations projected via PCA (2D & 3D) and t-SNE (2D):

### Elbow Silhouette
![Elbow Silhouette](figures/elbow_silhouette.png)

### Pca 2D
![Pca 2D](figures/pca_2d.png)

### Pca 3D
![Pca 3D](figures/pca_3d.png)

### Tsne 2D
![Tsne 2D](figures/tsne_2d.png)

### Cluster Heatmap
![Cluster Heatmap](figures/cluster_heatmap.png)

---

## 5. Incremental Database Architecture & Fallback Strategy
1. **SQLite Persistent Database (`data/anime_catalog.db`)**: Deduplicates incoming anime by canonical ID (`anilist:{id}`, `kitsu:{id}`), tracking pagination state across runs.
2. **Rate Limit Throttling**: Implements configurable polite delays (`--rate-delay`) to prevent API rate limits or IP bans during large catalog harvests.
3. **Multi-Source Failover**: Queries AniList GraphQL endpoint by default. If AniList is rate-limited, unreachable, or returns insufficient records, queries Kitsu JSON:API, normalizing attributes into the standard schema.
4. **Offline Portability**: The database automatically exports full state to `data/raw_anime_data.json` for offline demonstration.

---
*Report auto-generated by the Antigravity Data Science Pipeline.*