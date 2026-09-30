# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 40,654 anime entries (Current SQLite Local Database: 40,654 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 80 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 10
- **DBSCAN Density Structure**: 4 dense core clusters, 109 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [10, 12]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 10 | 237923.24 | 0.1309 | Selected |
| 11 | 234756.32 | 0.1216 |  |
| 12 | 230572.15 | 0.1161 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                                                          |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                   | top_tags                                           |
|--------------|------------------------------------------------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|------------------------------|----------------------------------------------------|
|            0 | Low-Profile (Commercial Mid-Tier & Long-Tail) [music • Core Reach]                 |   6254 |   63.72 |        63.72 |       980.20 |            980.18 |   2019 |       2019.00 |              0.05 |                   0.05 | Music, Special, Comedy       | music, vocaloid, comedy                            |
|            1 | Specialized Archetype (Comedy Focus) [Female Protagonist • High Reach]             |   4018 |   65.81 |        65.81 |      9954.00 |           9953.97 |   2015 |       2015.00 |              0.01 |                   0.01 | Comedy, Action, Fantasy      | Female Protagonist, Male Protagonist, School       |
|            2 | Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]               |   7025 |   65.38 |        65.38 |      1058.10 |           1058.08 |   2016 |       2016.00 |              0.05 |                   0.05 | Comedy, Fantasy, Action      | comedy, fantasy, action                            |
|            3 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Animals • Core Reach]               |   3906 |   64.23 |        64.23 |       233.60 |            233.65 |   2015 |       2015.00 |              0.01 |                   0.01 | Comedy, Fantasy, Action      | Full CGI, Kids, Animals                            |
|            4 | Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • Core Reach]                  |   5166 |   65.26 |        65.26 |      1021.60 |           1021.58 |   2015 |       2015.00 |              0.05 |                   0.05 | Fantasy, Comedy, Tv          | kids, chinese animation, short episodes            |
|            5 | Specialized Archetype (Adventure Focus)                                            |   2545 |   66.30 |        66.30 |      6114.50 |           6114.54 |   2014 |       2014.00 |              0.03 |                   0.03 | Adventure, Action, Fantasy   | adventure, fantasy, Male Protagonist               |
|            6 | Low-Profile (Commercial Mid-Tier & Long-Tail) [comedy • Broad Reach]               |   3377 |   48.28 |        48.28 |      1072.70 |           1072.72 |   2014 |       2014.00 |              0.05 |                   0.05 | Comedy, Music, Slice of Life | comedy, japanese production, shorts                |
|            7 | Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • Core Reach] (Cluster 7)      |   2476 |   58.35 |        58.35 |      1031.70 |           1031.68 |   1984 |       1984.00 |              0.05 |                   0.05 | Movie, Comedy, Action        | kids, japanese production, shorts                  |
|            8 | Specialized Archetype (Comedy Focus) [Female Protagonist • High Reach] (Cluster 8) |   2579 |   73.64 |        73.64 |    101425.10 |         101425.06 |   2018 |       2018.00 |              0.02 |                   0.02 | Comedy, Action, Drama        | Male Protagonist, Female Protagonist, Heterosexual |
|            9 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Female Protagonist • Broad Reach]   |   3308 |   53.32 |        53.32 |      1064.10 |           1064.05 |   2001 |       2001.00 |              0.01 |                   0.01 | Comedy, Adventure, Action    | Female Protagonist, Male Protagonist, Kids         |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Low-Profile (Commercial Mid-Tier & Long-Tail) [music • Core Reach]
- **Cluster Size**: 6254 titles (15.4% of catalog)
- **Median Release Year**: 2019
- **Mean Average Score**: 63.72 / 100
- **Mean Popularity**: 980 members
- **Favorites-to-Popularity Ratio**: 0.0545
- **Dominant Genres**: Music, Special, Comedy
- **Key Thematic Tags**: music, vocaloid, comedy
- **Representative Exemplar Titles**: !nvade Show!, "Anata o Hitokoto de Arawashite Kudasai" no Shitsumon ga Nigate da., "働く"の100年史, I=Fantasy, "Hitori de Ikirare Sō" tte Sore tte Nee, Homete Iru no?

### Cluster 1: Specialized Archetype (Comedy Focus) [Female Protagonist • High Reach]
- **Cluster Size**: 4018 titles (9.9% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 65.81 / 100
- **Mean Popularity**: 9,954 members
- **Favorites-to-Popularity Ratio**: 0.0104
- **Dominant Genres**: Comedy, Action, Fantasy
- **Key Thematic Tags**: Female Protagonist, Male Protagonist, School
- **Representative Exemplar Titles**: deleted, Diabolik Lovers, King's Game, Taboo Tattoo, WONDER EGG PRIORITY: My Priority

### Cluster 2: Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]
- **Cluster Size**: 7025 titles (17.3% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 65.38 / 100
- **Mean Popularity**: 1,058 members
- **Favorites-to-Popularity Ratio**: 0.0491
- **Dominant Genres**: Comedy, Fantasy, Action
- **Key Thematic Tags**: comedy, fantasy, action
- **Representative Exemplar Titles**: Shoujo Ramune, Imaizumi's house seems to be a gathering place for gals, Saimin Seishidou, Ecchi na Onee-chan ni Shiboraretai, Making A Cumback to Early Days!

### Cluster 3: Low-Profile (Commercial Mid-Tier & Long-Tail) [Animals • Core Reach]
- **Cluster Size**: 3906 titles (9.6% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 64.23 / 100
- **Mean Popularity**: 234 members
- **Favorites-to-Popularity Ratio**: 0.0083
- **Dominant Genres**: Comedy, Fantasy, Action
- **Key Thematic Tags**: Full CGI, Kids, Animals
- **Representative Exemplar Titles**: Kaikai Kitan, Steven Universe Season 2 Specials, One Piece: Straw Hat Theater, Fate/Zero Remix, Hellsing: Psalm of Darkness

### Cluster 4: Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • Core Reach]
- **Cluster Size**: 5166 titles (12.7% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 65.26 / 100
- **Mean Popularity**: 1,022 members
- **Favorites-to-Popularity Ratio**: 0.0483
- **Dominant Genres**: Fantasy, Comedy, Tv
- **Key Thematic Tags**: kids, chinese animation, short episodes
- **Representative Exemplar Titles**: Yo-kai Watch, Kirby: Right Back at Ya!, Shadowverse, Renegade Immortal, KochiKame

### Cluster 5: Specialized Archetype (Adventure Focus)
- **Cluster Size**: 2545 titles (6.3% of catalog)
- **Median Release Year**: 2014
- **Mean Average Score**: 66.30 / 100
- **Mean Popularity**: 6,114 members
- **Favorites-to-Popularity Ratio**: 0.0339
- **Dominant Genres**: Adventure, Action, Fantasy
- **Key Thematic Tags**: adventure, fantasy, Male Protagonist
- **Representative Exemplar Titles**: Demon Slayer: Kimetsu no Yaiba Infinity Castle, The Disappearance of Haruhi Suzumiya, Castle in the Sky, Evangelion: 3.0+1.0 Thrice Upon a Time, The Quintessential Quintuplets Movie

### Cluster 6: Low-Profile (Commercial Mid-Tier & Long-Tail) [comedy • Broad Reach]
- **Cluster Size**: 3377 titles (8.3% of catalog)
- **Median Release Year**: 2014
- **Mean Average Score**: 48.28 / 100
- **Mean Popularity**: 1,073 members
- **Favorites-to-Popularity Ratio**: 0.0492
- **Dominant Genres**: Comedy, Music, Slice of Life
- **Key Thematic Tags**: comedy, japanese production, shorts
- **Representative Exemplar Titles**: Pupa, Boku no Pico, EX-ARM, GIBIATE, Mars of Destruction

### Cluster 7: Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • Core Reach] (Cluster 7)
- **Cluster Size**: 2476 titles (6.1% of catalog)
- **Median Release Year**: 1984
- **Mean Average Score**: 58.35 / 100
- **Mean Popularity**: 1,032 members
- **Favorites-to-Popularity Ratio**: 0.0490
- **Dominant Genres**: Movie, Comedy, Action
- **Key Thematic Tags**: kids, japanese production, shorts
- **Representative Exemplar Titles**: Dororo, Cutie Honey, MD Geist - The Most Dangerous Ever, Gauche the Cellist, Ringing Bell

### Cluster 8: Specialized Archetype (Comedy Focus) [Female Protagonist • High Reach] (Cluster 8)
- **Cluster Size**: 2579 titles (6.3% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 73.64 / 100
- **Mean Popularity**: 101,425 members
- **Favorites-to-Popularity Ratio**: 0.0221
- **Dominant Genres**: Comedy, Action, Drama
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Heterosexual
- **Representative Exemplar Titles**: Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, Death Note, My Hero Academia

### Cluster 9: Low-Profile (Commercial Mid-Tier & Long-Tail) [Female Protagonist • Broad Reach]
- **Cluster Size**: 3308 titles (8.1% of catalog)
- **Median Release Year**: 2001
- **Mean Average Score**: 53.32 / 100
- **Mean Popularity**: 1,064 members
- **Favorites-to-Popularity Ratio**: 0.0084
- **Dominant Genres**: Comedy, Adventure, Action
- **Key Thematic Tags**: Female Protagonist, Male Protagonist, Kids
- **Representative Exemplar Titles**: makuranodanshi, KOWABON, On a Lustful Night Mingling with a Priest, The Reflection, Pastel Memories

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