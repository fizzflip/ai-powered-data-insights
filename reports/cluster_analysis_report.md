# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 3,148 anime entries (Current SQLite Local Database: 3,148 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 74 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 8
- **DBSCAN Density Structure**: 11 dense core clusters, 122 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [8, 10]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 8 | 20942.00 | 0.0872 | Selected |
| 9 | 20427.20 | 0.0863 |  |
| 10 | 20013.78 | 0.0859 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                                                     |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                   | top_tags                                           |
|--------------|-------------------------------------------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|------------------------------|----------------------------------------------------|
|            0 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach] |    575 |   65.43 |        65.43 |     43101.70 |          43101.67 |   2014 |       2014.00 |              0.01 |                   0.01 | Comedy, Action, Romance      | Male Protagonist, School, Female Protagonist       |
|            1 | Modern Hits (Blockbuster Drama) [Male Protagonist • High Reach]               |    339 |   82.72 |        82.72 |    374613.00 |         374612.96 |   2017 |       2017.00 |              0.05 |                   0.05 | Drama, Action, Comedy        | Male Protagonist, Tragedy, Ensemble Cast           |
|            2 | Specialized Archetype (Comedy Focus)                                          |    563 |   74.76 |        74.76 |     53100.40 |          53100.38 |   2021 |       2021.00 |              0.02 |                   0.02 | Comedy, Slice of Life, Drama | Male Protagonist, Female Protagonist, Heterosexual |
|            3 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Super Power • Core Reach]      |    218 |   73.44 |        73.44 |     44390.90 |          44390.92 |   2013 |       2013.00 |              0.01 |                   0.01 | Action, Drama, Adventure     | Male Protagonist, Super Power, Female Protagonist  |
|            4 | Modern Hits (Blockbuster Comedy)                                              |    659 |   76.50 |        76.50 |    212368.80 |         212368.83 |   2018 |       2018.00 |              0.02 |                   0.02 | Comedy, Action, Drama        | Male Protagonist, Heterosexual, Female Protagonist |
|            5 | Modern Hits (Blockbuster Drama) [Female Protagonist • High Reach]             |    164 |   81.52 |        81.52 |    186509.60 |         186509.60 |   2017 |       2017.00 |              0.03 |                   0.03 | Drama, Action, Fantasy       | Male Protagonist, Female Protagonist, Tragedy      |
|            6 | Classics (Historical Favorites)                                               |    207 |   75.24 |        75.24 |     69412.00 |          69412.02 |   2004 |       2004.00 |              0.02 |                   0.02 | Action, Comedy, Drama        | Male Protagonist, Female Protagonist, Tragedy      |
|            7 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Female Harem • Broad Reach]    |    423 |   65.63 |        65.63 |     90172.20 |          90172.22 |   2022 |       2022.00 |              0.02 |                   0.02 | Fantasy, Action, Adventure   | Male Protagonist, Magic, Female Harem              |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach]
- **Cluster Size**: 575 titles (18.3% of catalog)
- **Median Release Year**: 2014
- **Mean Average Score**: 65.43 / 100
- **Mean Popularity**: 43,102 members
- **Favorites-to-Popularity Ratio**: 0.0093
- **Dominant Genres**: Comedy, Action, Romance
- **Key Thematic Tags**: Male Protagonist, School, Female Protagonist
- **Representative Exemplar Titles**: School Days (TV), Rosario + Vampire, Dagashi Kashi, Keijo!!!!!!!!, kiss×sis (TV)

### Cluster 1: Modern Hits (Blockbuster Drama) [Male Protagonist • High Reach]
- **Cluster Size**: 339 titles (10.8% of catalog)
- **Median Release Year**: 2017
- **Mean Average Score**: 82.72 / 100
- **Mean Popularity**: 374,613 members
- **Favorites-to-Popularity Ratio**: 0.0523
- **Dominant Genres**: Drama, Action, Comedy
- **Key Thematic Tags**: Male Protagonist, Tragedy, Ensemble Cast
- **Representative Exemplar Titles**: Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, Death Note, My Hero Academia

### Cluster 2: Specialized Archetype (Comedy Focus)
- **Cluster Size**: 563 titles (17.9% of catalog)
- **Median Release Year**: 2021
- **Mean Average Score**: 74.76 / 100
- **Mean Popularity**: 53,100 members
- **Favorites-to-Popularity Ratio**: 0.0193
- **Dominant Genres**: Comedy, Slice of Life, Drama
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Heterosexual
- **Representative Exemplar Titles**: Haikyu!! 3rd Season, My Hero Academia Season 5, Aharen-san wa Hakarenai, HAIKYU!! LAND VS. AIR, How Heavy Are the Dumbbells You Lift?

### Cluster 3: Low-Profile (Commercial Mid-Tier & Long-Tail) [Super Power • Core Reach]
- **Cluster Size**: 218 titles (6.9% of catalog)
- **Median Release Year**: 2013
- **Mean Average Score**: 73.44 / 100
- **Mean Popularity**: 44,391 members
- **Favorites-to-Popularity Ratio**: 0.0131
- **Dominant Genres**: Action, Drama, Adventure
- **Key Thematic Tags**: Male Protagonist, Super Power, Female Protagonist
- **Representative Exemplar Titles**: Dr. STONE Special Episode – RYUSUI, Re:ZERO -Starting Life in Another World- OVAs, the Garden of sinners Chapter 1: Thanatos. (Overlooking View), My Hero Academia: World Heroes' Mission, GOBLIN SLAYER -GOBLIN’S CROWN-

### Cluster 4: Modern Hits (Blockbuster Comedy)
- **Cluster Size**: 659 titles (20.9% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 76.50 / 100
- **Mean Popularity**: 212,369 members
- **Favorites-to-Popularity Ratio**: 0.0238
- **Dominant Genres**: Comedy, Action, Drama
- **Key Thematic Tags**: Male Protagonist, Heterosexual, Female Protagonist
- **Representative Exemplar Titles**: My Hero Academia Season 2, Attack on Titan, My Hero Academia Season 3, My Hero Academia, Akame ga Kill!

### Cluster 5: Modern Hits (Blockbuster Drama) [Female Protagonist • High Reach]
- **Cluster Size**: 164 titles (5.2% of catalog)
- **Median Release Year**: 2017
- **Mean Average Score**: 81.52 / 100
- **Mean Popularity**: 186,510 members
- **Favorites-to-Popularity Ratio**: 0.0346
- **Dominant Genres**: Drama, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Tragedy
- **Representative Exemplar Titles**: A Silent Voice, Your Name., Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, Spirited Away, JUJUTSU KAISEN 0

### Cluster 6: Classics (Historical Favorites)
- **Cluster Size**: 207 titles (6.6% of catalog)
- **Median Release Year**: 2004
- **Mean Average Score**: 75.24 / 100
- **Mean Popularity**: 69,412 members
- **Favorites-to-Popularity Ratio**: 0.0248
- **Dominant Genres**: Action, Comedy, Drama
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Tragedy
- **Representative Exemplar Titles**: Fullmetal Alchemist, Dragon Ball Z, Dragon Ball, Naruto: Shippuden, Darker than Black

### Cluster 7: Low-Profile (Commercial Mid-Tier & Long-Tail) [Female Harem • Broad Reach]
- **Cluster Size**: 423 titles (13.4% of catalog)
- **Median Release Year**: 2022
- **Mean Average Score**: 65.63 / 100
- **Mean Popularity**: 90,172 members
- **Favorites-to-Popularity Ratio**: 0.0152
- **Dominant Genres**: Fantasy, Action, Adventure
- **Key Thematic Tags**: Male Protagonist, Magic, Female Harem
- **Representative Exemplar Titles**: The Promised Neverland Season 2, The Rising of the Shield Hero Season 2, Is It Wrong to Try to Pick Up Girls in a Dungeon? II, Arifureta: From Commonplace to World's Strongest, Boruto: Naruto Next Generations

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