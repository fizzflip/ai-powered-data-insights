# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 10,048 anime entries (Current SQLite Local Database: 10,048 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 77 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 10
- **DBSCAN Density Structure**: 6 dense core clusters, 119 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [10, 12]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 10 | 64065.18 | 0.1116 | Selected |
| 11 | 62802.63 | 0.1057 |  |
| 12 | 61675.41 | 0.1085 |  |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                                                      |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                 | top_tags                                           |
|--------------|--------------------------------------------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|----------------------------|----------------------------------------------------|
|            0 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Broad Reach] |   1186 |   70.08 |        70.08 |     13943.90 |          13943.90 |   2014 |       2014.50 |              0.01 |                   0.01 | Comedy, Action, Fantasy    | Male Protagonist, Female Protagonist, School       |
|            1 | Low-Profile (Commercial Mid-Tier & Long-Tail) [ONA • Core Reach]               |    588 |   66.75 |        66.75 |      3215.20 |           3215.17 |   2012 |       2012.00 |              0.00 |                   0.00 | Animation, Tv, Ona         | TV, ONA, special                                   |
|            2 | Low-Profile (Commercial Mid-Tier & Long-Tail) [ONA • Core Reach] (Cluster 2)   |   1023 |   69.02 |        69.02 |      3344.50 |           3344.53 |   2012 |       2012.00 |              0.00 |                   0.00 | Animation, Special, Ova    | special, OVA, ONA                                  |
|            3 | Modern Hits (Blockbuster Drama)                                                |    432 |   81.95 |        81.95 |    234334.10 |         234334.08 |   2017 |       2017.00 |              0.05 |                   0.05 | Drama, Action, Comedy      | Male Protagonist, Tragedy, Female Protagonist      |
|            4 | Specialized Archetype (Action Focus)                                           |   1068 |   72.60 |        72.60 |     25377.40 |          25377.40 |   2014 |       2013.50 |              0.01 |                   0.01 | Action, Drama, Adventure   | Male Protagonist, Female Protagonist, Tragedy      |
|            5 | Specialized Archetype (Comedy Focus) [Male Protagonist • Broad Reach]          |   1640 |   61.79 |        61.79 |     21389.30 |          21389.35 |   2016 |       2016.00 |              0.01 |                   0.01 | Comedy, Action, Fantasy    | Male Protagonist, Female Protagonist, School       |
|            6 | Specialized Archetype (Comedy Focus) [Female Protagonist • High Reach]         |   1651 |   73.22 |        73.22 |     76869.80 |          76869.82 |   2019 |       2019.00 |              0.02 |                   0.02 | Comedy, Action, Fantasy    | Male Protagonist, Female Protagonist, Heterosexual |
|            7 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach]  |    725 |   70.13 |        70.13 |     12829.10 |          12829.15 |   1999 |       1999.00 |              0.02 |                   0.02 | Comedy, Action, Adventure  | Male Protagonist, Female Protagonist, Shounen      |
|            8 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Nakadashi • Core Reach]         |    735 |   67.48 |        67.48 |      2388.00 |           2387.97 |   2015 |       2015.00 |              0.04 |                   0.04 | Hentai, Fantasy, Action    | Nakadashi, Fellatio, Large Breasts                 |
|            9 | Low-Profile (Commercial Mid-Tier & Long-Tail) [Full CGI • Core Reach]          |   1000 |   67.77 |        67.77 |       630.80 |            630.79 |   2015 |       2015.00 |              0.01 |                   0.01 | Fantasy, Action, Adventure | Full CGI, Female Protagonist, Male Protagonist     |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Broad Reach]
- **Cluster Size**: 1186 titles (11.8% of catalog)
- **Median Release Year**: 2014
- **Mean Average Score**: 70.08 / 100
- **Mean Popularity**: 13,944 members
- **Favorites-to-Popularity Ratio**: 0.0090
- **Dominant Genres**: Comedy, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, School
- **Representative Exemplar Titles**: Attack on Titan: No Regrets, Steins;Gate: Egoistic Poriomania, the Garden of sinners Chapter 1: Thanatos. (Overlooking View), Little Witch Academia, One-Punch Man: Road to Hero

### Cluster 1: Low-Profile (Commercial Mid-Tier & Long-Tail) [ONA • Core Reach]
- **Cluster Size**: 588 titles (5.9% of catalog)
- **Median Release Year**: 2012
- **Mean Average Score**: 66.75 / 100
- **Mean Popularity**: 3,215 members
- **Favorites-to-Popularity Ratio**: 0.0033
- **Dominant Genres**: Animation, Tv, Ona
- **Key Thematic Tags**: TV, ONA, special
- **Representative Exemplar Titles**: Kiss x Sis (TV), Aldnoah.Zero 2nd Season, The Asterisk War: The Academy City on the Water, Air, Special A (S.A)

### Cluster 2: Low-Profile (Commercial Mid-Tier & Long-Tail) [ONA • Core Reach] (Cluster 2)
- **Cluster Size**: 1023 titles (10.2% of catalog)
- **Median Release Year**: 2012
- **Mean Average Score**: 69.02 / 100
- **Mean Popularity**: 3,344 members
- **Favorites-to-Popularity Ratio**: 0.0032
- **Dominant Genres**: Animation, Special, Ova
- **Key Thematic Tags**: special, OVA, ONA
- **Representative Exemplar Titles**: Attack on Titan Season 3 Specials, Hunter x Hunter: Greed Island, Hunter x Hunter: Greed Island Final, Avatar: The Legend So Far, Hunter x Hunter OVA

### Cluster 3: Modern Hits (Blockbuster Drama)
- **Cluster Size**: 432 titles (4.3% of catalog)
- **Median Release Year**: 2017
- **Mean Average Score**: 81.95 / 100
- **Mean Popularity**: 234,334 members
- **Favorites-to-Popularity Ratio**: 0.0457
- **Dominant Genres**: Drama, Action, Comedy
- **Key Thematic Tags**: Male Protagonist, Tragedy, Female Protagonist
- **Representative Exemplar Titles**: Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, Death Note, My Hero Academia

### Cluster 4: Specialized Archetype (Action Focus)
- **Cluster Size**: 1068 titles (10.6% of catalog)
- **Median Release Year**: 2014
- **Mean Average Score**: 72.60 / 100
- **Mean Popularity**: 25,377 members
- **Favorites-to-Popularity Ratio**: 0.0129
- **Dominant Genres**: Action, Drama, Adventure
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Tragedy
- **Representative Exemplar Titles**: Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, JUJUTSU KAISEN 0, Your Name., Weathering With You, A Silent Voice

### Cluster 5: Specialized Archetype (Comedy Focus) [Male Protagonist • Broad Reach]
- **Cluster Size**: 1640 titles (16.3% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 61.79 / 100
- **Mean Popularity**: 21,389 members
- **Favorites-to-Popularity Ratio**: 0.0097
- **Dominant Genres**: Comedy, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, School
- **Representative Exemplar Titles**: The Promised Neverland Season 2, Boruto: Naruto Next Generations, Eromanga Sensei, In Another World With My Smartphone, One-Punch Man Season 3

### Cluster 6: Specialized Archetype (Comedy Focus) [Female Protagonist • High Reach]
- **Cluster Size**: 1651 titles (16.4% of catalog)
- **Median Release Year**: 2019
- **Mean Average Score**: 73.22 / 100
- **Mean Popularity**: 76,870 members
- **Favorites-to-Popularity Ratio**: 0.0176
- **Dominant Genres**: Comedy, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Heterosexual
- **Representative Exemplar Titles**: My Hero Academia Season 2, Attack on Titan, My Hero Academia Season 3, My Hero Academia, My Hero Academia Season 4

### Cluster 7: Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach]
- **Cluster Size**: 725 titles (7.2% of catalog)
- **Median Release Year**: 1999
- **Mean Average Score**: 70.13 / 100
- **Mean Popularity**: 12,829 members
- **Favorites-to-Popularity Ratio**: 0.0178
- **Dominant Genres**: Comedy, Action, Adventure
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Shounen
- **Representative Exemplar Titles**: Dragon Ball, Pokémon, Dragon Ball GT, Full Metal Panic!, Chobits

### Cluster 8: Low-Profile (Commercial Mid-Tier & Long-Tail) [Nakadashi • Core Reach]
- **Cluster Size**: 735 titles (7.3% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 67.48 / 100
- **Mean Popularity**: 2,388 members
- **Favorites-to-Popularity Ratio**: 0.0398
- **Dominant Genres**: Hentai, Fantasy, Action
- **Key Thematic Tags**: Nakadashi, Fellatio, Large Breasts
- **Representative Exemplar Titles**: Manga Café Mishaps, Kawaki wo Ameku, Eroge! Sex and Gamedev, RWBY, Ane wa Yanmama Junyuu-chuu

### Cluster 9: Low-Profile (Commercial Mid-Tier & Long-Tail) [Full CGI • Core Reach]
- **Cluster Size**: 1000 titles (10.0% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 67.77 / 100
- **Mean Popularity**: 631 members
- **Favorites-to-Popularity Ratio**: 0.0128
- **Dominant Genres**: Fantasy, Action, Adventure
- **Key Thematic Tags**: Full CGI, Female Protagonist, Male Protagonist
- **Representative Exemplar Titles**: Inferno Cop 2, Girls' Work, Qing Jiao Wo Gui Chai Da Ren, BLADE & BASTARD, The Bugle Call: Song of War

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