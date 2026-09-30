# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 1,998 anime entries (Current SQLite Local Database: 1,998 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 73 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 7
- **DBSCAN Density Structure**: 14 dense core clusters, 116 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [7, 9]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 7 | 13604.50 | 0.0961 | Selected |
| 8 | 13245.62 | 0.0903 |  |
| 9 | 12927.95 | 0.0857 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                     |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                     | top_tags                                            |
|--------------|-----------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|--------------------------------|-----------------------------------------------------|
|            0 | Low-Profile (Commercial Mid-Tier & Long-Tail) |    511 |   66.16 |        66.16 |    101275.80 |         101275.83 |   2018 |       2018.00 |              0.01 |                   0.01 | Action, Fantasy, Comedy        | Male Protagonist, Female Harem, Magic               |
|            1 | Specialized Archetype (Comedy Focus)          |    498 |   75.99 |        75.99 |    114959.40 |         114959.36 |   2018 |       2018.00 |              0.02 |                   0.02 | Comedy, Slice of Life, Romance | Male Protagonist, Female Protagonist, School        |
|            2 | Modern Hits (Blockbuster Drama)               |    165 |   84.75 |        84.75 |    417592.70 |         417592.72 |   2018 |       2018.00 |              0.06 |                   0.06 | Drama, Action, Comedy          | Male Protagonist, Tragedy, Ensemble Cast            |
|            3 | Specialized Archetype (Drama Focus)           |    175 |   78.33 |        78.33 |    124951.00 |         124951.01 |   2017 |       2017.00 |              0.02 |                   0.02 | Drama, Action, Fantasy         | Male Protagonist, Female Protagonist, Tragedy       |
|            4 | Classics (Historical Favorites)               |    143 |   78.57 |        78.57 |    185361.30 |         185361.29 |   2005 |       2005.00 |              0.04 |                   0.04 | Action, Comedy, Drama          | Male Protagonist, Female Protagonist, Ensemble Cast |
|            5 | Modern Hits (Blockbuster Action)              |    458 |   78.19 |        78.19 |    293278.40 |         293278.44 |   2018 |       2018.00 |              0.03 |                   0.03 | Action, Drama, Comedy          | Male Protagonist, Tragedy, Heterosexual             |
|            6 | Classics (Legacy Masterworks - High Devotion) |     48 |   82.79 |        82.79 |    266864.40 |         266864.35 |   2001 |       2001.00 |              0.05 |                   0.05 | Drama, Fantasy, Adventure      | Female Protagonist, Male Protagonist, Tragedy       |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Low-Profile (Commercial Mid-Tier & Long-Tail)
- **Cluster Size**: 511 titles (25.6% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 66.16 / 100
- **Mean Popularity**: 101,276 members
- **Favorites-to-Popularity Ratio**: 0.0138
- **Dominant Genres**: Action, Fantasy, Comedy
- **Key Thematic Tags**: Male Protagonist, Female Harem, Magic
- **Representative Exemplar Titles**: The Promised Neverland Season 2, Tokyo Ghoul:re, Date A Live, The Rising of the Shield Hero Season 2, Is It Wrong to Try to Pick Up Girls in a Dungeon? II

### Cluster 1: Specialized Archetype (Comedy Focus)
- **Cluster Size**: 498 titles (24.9% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 75.99 / 100
- **Mean Popularity**: 114,959 members
- **Favorites-to-Popularity Ratio**: 0.0202
- **Dominant Genres**: Comedy, Slice of Life, Romance
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, School
- **Representative Exemplar Titles**: Attack on Titan Season 2, Attack on Titan Season 3, Attack on Titan Season 3 Part 2, DON'T TOY WITH ME, MISS NAGATORO, Assassination Classroom Second Season

### Cluster 2: Modern Hits (Blockbuster Drama)
- **Cluster Size**: 165 titles (8.3% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 84.75 / 100
- **Mean Popularity**: 417,593 members
- **Favorites-to-Popularity Ratio**: 0.0627
- **Dominant Genres**: Drama, Action, Comedy
- **Key Thematic Tags**: Male Protagonist, Tragedy, Ensemble Cast
- **Representative Exemplar Titles**: Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, Death Note, Hunter x Hunter (2011)

### Cluster 3: Specialized Archetype (Drama Focus)
- **Cluster Size**: 175 titles (8.8% of catalog)
- **Median Release Year**: 2017
- **Mean Average Score**: 78.33 / 100
- **Mean Popularity**: 124,951 members
- **Favorites-to-Popularity Ratio**: 0.0228
- **Dominant Genres**: Drama, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Tragedy
- **Representative Exemplar Titles**: Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, JUJUTSU KAISEN 0, Your Name., A Silent Voice, Rascal Does Not Dream of a Dreaming Girl

### Cluster 4: Classics (Historical Favorites)
- **Cluster Size**: 143 titles (7.2% of catalog)
- **Median Release Year**: 2005
- **Mean Average Score**: 78.57 / 100
- **Mean Popularity**: 185,361 members
- **Favorites-to-Popularity Ratio**: 0.0372
- **Dominant Genres**: Action, Comedy, Drama
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Ensemble Cast
- **Representative Exemplar Titles**: Naruto, Bleach, Death Note, Fullmetal Alchemist: Brotherhood, Hunter x Hunter (2011)

### Cluster 5: Modern Hits (Blockbuster Action)
- **Cluster Size**: 458 titles (22.9% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 78.19 / 100
- **Mean Popularity**: 293,278 members
- **Favorites-to-Popularity Ratio**: 0.0299
- **Dominant Genres**: Action, Drama, Comedy
- **Key Thematic Tags**: Male Protagonist, Tragedy, Heterosexual
- **Representative Exemplar Titles**: My Hero Academia, Tokyo Ghoul, Attack on Titan Season 2, Sword Art Online, Attack on Titan Season 3

### Cluster 6: Classics (Legacy Masterworks - High Devotion)
- **Cluster Size**: 48 titles (2.4% of catalog)
- **Median Release Year**: 2001
- **Mean Average Score**: 82.79 / 100
- **Mean Popularity**: 266,864 members
- **Favorites-to-Popularity Ratio**: 0.0476
- **Dominant Genres**: Drama, Fantasy, Adventure
- **Key Thematic Tags**: Female Protagonist, Male Protagonist, Tragedy
- **Representative Exemplar Titles**: A Silent Voice, Your Name., Spirited Away, I Want to Eat Your Pancreas, Howl‘s Moving Castle

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