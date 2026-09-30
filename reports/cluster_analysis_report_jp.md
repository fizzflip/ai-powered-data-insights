# Anime Unsupervised Clustering & Empirical Archetype Report

## Executive Summary
- **Dataset Analyzed**: 20,000 anime entries (Current SQLite Local Database: 40,654 titles)
- **Data Architecture**: Dual-storage engine (SQLite `data/anime_catalog.db` with auto-sync to `data/raw_anime_data.json`)
- **Multi-Source Support**: Primary AniList GraphQL API + Secondary Kitsu JSON:API fallback with polite rate-limiting
- **Feature Dimensionality**: 80 engineered features (Continuous standard, categorical one-hot, multi-label genres, and TF-IDF tags)
- **K-Means Cluster Count ($k$)**: 10
- **DBSCAN Density Structure**: 2 dense core clusters, 76 structural noise/outlier points

---

## 1. Optimal Number of Clusters & Silhouette Diagnostics
Cluster cohesion and separation were evaluated across candidate cluster counts $k \in [10, 12]$:

| $k$ (Clusters) | Inertia ($WCSS$) | Silhouette Score | Archetype Alignment Status |
|:--------------:|:----------------:|:----------------:|:--------------------------:|
| 10 | 116171.72 | 0.1109 | Selected |
| 11 | 113234.18 | 0.1132 |  |
| 12 | 111017.72 | 0.1147 | Global Maximum |

> [!NOTE]
> **Adaptive Cluster Scaling & Parsimony Tradeoff**: The candidate search window scales dynamically with catalog volume. Penalized silhouette scoring prevents premature saturation at coarse $k$ while rewarding relative inertia reduction, allowing subtle sub-genres and era distinctions to surface as the database grows.

---

## 2. Cluster Profiles Summary Table
Quantitative feature means and dominant categorical traits across each discovered cluster archetype:

|   cluster_id | archetype                                                                        |   size |   score |   mean_score |   popularity |   mean_popularity |   year |   median_year |   favorites_ratio |   mean_favorites_ratio | top_genres                   | top_tags                                           |
|--------------|----------------------------------------------------------------------------------|--------|---------|--------------|--------------|-------------------|--------|---------------|-------------------|------------------------|------------------------------|----------------------------------------------------|
|            0 | Specialized Archetype (Comedy Focus) [Female Protagonist • Broad Reach]          |   2211 |   58.32 |        58.32 |      2955.00 |           2955.00 |   2003 |       2003.00 |              0.01 |                   0.01 | Comedy, Action, Sci-Fi       | Female Protagonist, Male Protagonist, School       |
|            1 | Low-Profile (Commercial Mid-Tier & Long-Tail) [music • Core Reach]               |   2653 |   63.23 |        63.23 |      1000.00 |           1000.00 |   2020 |       2020.00 |              0.05 |                   0.05 | Music, Special, Fantasy      | music, vocaloid, idol                              |
|            2 | Modern Hits (Blockbuster Comedy)                                                 |   1332 |   76.74 |        76.74 |    155779.00 |         155779.03 |   2018 |       2018.00 |              0.03 |                   0.03 | Comedy, Drama, Action        | Male Protagonist, Female Protagonist, Heterosexual |
|            3 | Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]             |   3551 |   65.22 |        65.22 |      1129.50 |           1129.53 |   2016 |       2016.00 |              0.05 |                   0.05 | Comedy, Fantasy, Action      | comedy, fantasy, action                            |
|            4 | Specialized Archetype (Action Focus)                                             |   1399 |   69.53 |        69.53 |     13611.90 |          13611.89 |   2013 |       2013.00 |              0.02 |                   0.02 | Action, Drama, Adventure     | Male Protagonist, Female Protagonist, Shounen      |
|            5 | Specialized Archetype (Comedy Focus) [Male Protagonist • Broad Reach]            |   1922 |   67.97 |        67.97 |      5938.10 |           5938.10 |   2015 |       2015.00 |              0.01 |                   0.01 | Comedy, Action, Fantasy      | Female Protagonist, Male Protagonist, School       |
|            6 | Specialized Archetype (Comedy Focus) [School • High Reach]                       |   2668 |   67.18 |        67.18 |     26396.50 |          26396.46 |   2016 |       2016.00 |              0.01 |                   0.01 | Comedy, Action, Fantasy      | Male Protagonist, Female Protagonist, School       |
|            7 | Low-Profile (Commercial Mid-Tier & Long-Tail) [shorts • Core Reach]              |   1600 |   48.68 |        48.68 |      1083.30 |           1083.29 |   2013 |       2013.00 |              0.05 |                   0.05 | Comedy, Slice of Life, Music | comedy, japanese production, shorts                |
|            8 | Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • Core Reach]                |   1539 |   65.28 |        65.28 |      1108.70 |           1108.69 |   2015 |       2015.00 |              0.05 |                   0.05 | Comedy, Fantasy, Tv          | kids, comedy, fantasy                              |
|            9 | Low-Profile (Commercial Mid-Tier & Long-Tail) [japanese production • Core Reach] |   1125 |   57.98 |        57.98 |      1026.10 |           1026.13 |   1986 |       1986.00 |              0.05 |                   0.05 | Comedy, Fantasy, Adventure   | japanese production, kids, comedy                  |

---

## 3. Detailed Empirical Archetype Findings
### Cluster 0: Specialized Archetype (Comedy Focus) [Female Protagonist • Broad Reach]
- **Cluster Size**: 2211 titles (11.1% of catalog)
- **Median Release Year**: 2003
- **Mean Average Score**: 58.32 / 100
- **Mean Popularity**: 2,955 members
- **Favorites-to-Popularity Ratio**: 0.0089
- **Dominant Genres**: Comedy, Action, Sci-Fi
- **Key Thematic Tags**: Female Protagonist, Male Protagonist, School
- **Representative Exemplar Titles**: Pupa, Dragon Ball Z: Bio-Broly, Chika Gentou Gekiga: Shoujo Tsubaki, GIBIATE, Dragon Ball: Curse of the Blood Rubies

### Cluster 1: Low-Profile (Commercial Mid-Tier & Long-Tail) [music • Core Reach]
- **Cluster Size**: 2653 titles (13.3% of catalog)
- **Median Release Year**: 2020
- **Mean Average Score**: 63.23 / 100
- **Mean Popularity**: 1,000 members
- **Favorites-to-Popularity Ratio**: 0.0500
- **Dominant Genres**: Music, Special, Fantasy
- **Key Thematic Tags**: music, vocaloid, idol
- **Representative Exemplar Titles**: !nvade Show!, "Anata o Hitokoto de Arawashite Kudasai" no Shitsumon ga Nigate da., "働く"の100年史, "Hitori de Ikirare Sō" tte Sore tte Nee, Homete Iru no?, "IDOLIC's Magic"

### Cluster 2: Modern Hits (Blockbuster Comedy)
- **Cluster Size**: 1332 titles (6.7% of catalog)
- **Median Release Year**: 2018
- **Mean Average Score**: 76.74 / 100
- **Mean Popularity**: 155,779 members
- **Favorites-to-Popularity Ratio**: 0.0277
- **Dominant Genres**: Comedy, Drama, Action
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Heterosexual
- **Representative Exemplar Titles**: Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN, Death Note, My Hero Academia

### Cluster 3: Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]
- **Cluster Size**: 3551 titles (17.8% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 65.22 / 100
- **Mean Popularity**: 1,130 members
- **Favorites-to-Popularity Ratio**: 0.0495
- **Dominant Genres**: Comedy, Fantasy, Action
- **Key Thematic Tags**: comedy, fantasy, action
- **Representative Exemplar Titles**: Ane wa Yanmama Junyuu-chuu, Shoujo Ramune, Chiikawa, Uchi no Otouto Maji de Dekain dakedo Mi ni Konai?, Imaizumi's house seems to be a gathering place for gals

### Cluster 4: Specialized Archetype (Action Focus)
- **Cluster Size**: 1399 titles (7.0% of catalog)
- **Median Release Year**: 2013
- **Mean Average Score**: 69.53 / 100
- **Mean Popularity**: 13,612 members
- **Favorites-to-Popularity Ratio**: 0.0228
- **Dominant Genres**: Action, Drama, Adventure
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, Shounen
- **Representative Exemplar Titles**: A Silent Voice, Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, Demon Slayer: Kimetsu no Yaiba Infinity Castle, Sword Art Online the Movie: Ordinal Scale, The Disappearance of Haruhi Suzumiya

### Cluster 5: Specialized Archetype (Comedy Focus) [Male Protagonist • Broad Reach]
- **Cluster Size**: 1922 titles (9.6% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 67.97 / 100
- **Mean Popularity**: 5,938 members
- **Favorites-to-Popularity Ratio**: 0.0097
- **Dominant Genres**: Comedy, Action, Fantasy
- **Key Thematic Tags**: Female Protagonist, Male Protagonist, School
- **Representative Exemplar Titles**: Peace Sign, Avatar: The Legend So Far, Fate/stay night: Unlimited Blade Works - Prologue, Yuuri!!! on ICE The Movie: ICE ADOLESCENCE, Corpse Party: Missing Footage

### Cluster 6: Specialized Archetype (Comedy Focus) [School • High Reach]
- **Cluster Size**: 2668 titles (13.3% of catalog)
- **Median Release Year**: 2016
- **Mean Average Score**: 67.18 / 100
- **Mean Popularity**: 26,396 members
- **Favorites-to-Popularity Ratio**: 0.0130
- **Dominant Genres**: Comedy, Action, Fantasy
- **Key Thematic Tags**: Male Protagonist, Female Protagonist, School
- **Representative Exemplar Titles**: One-Punch Man Season 3, My First Girlfriend is a Gal, And you thought there is never a girl online?, Infinite Stratos, Oreshura

### Cluster 7: Low-Profile (Commercial Mid-Tier & Long-Tail) [shorts • Core Reach]
- **Cluster Size**: 1600 titles (8.0% of catalog)
- **Median Release Year**: 2013
- **Mean Average Score**: 48.68 / 100
- **Mean Popularity**: 1,083 members
- **Favorites-to-Popularity Ratio**: 0.0494
- **Dominant Genres**: Comedy, Slice of Life, Music
- **Key Thematic Tags**: comedy, japanese production, shorts
- **Representative Exemplar Titles**: Boku no Pico, EX-ARM, Mars of Destruction, Tenkuu Danzai Skelter Heaven, Shitcom

### Cluster 8: Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • Core Reach]
- **Cluster Size**: 1539 titles (7.7% of catalog)
- **Median Release Year**: 2015
- **Mean Average Score**: 65.28 / 100
- **Mean Popularity**: 1,109 members
- **Favorites-to-Popularity Ratio**: 0.0486
- **Dominant Genres**: Comedy, Fantasy, Tv
- **Key Thematic Tags**: kids, comedy, fantasy
- **Representative Exemplar Titles**: Moomin, Nobody's Boy Remi, Renegade Immortal, Ojamajo Doremi Dokkaan!, Wonderful Precure!

### Cluster 9: Low-Profile (Commercial Mid-Tier & Long-Tail) [japanese production • Core Reach]
- **Cluster Size**: 1125 titles (5.6% of catalog)
- **Median Release Year**: 1986
- **Mean Average Score**: 57.98 / 100
- **Mean Popularity**: 1,026 members
- **Favorites-to-Popularity Ratio**: 0.0489
- **Dominant Genres**: Comedy, Fantasy, Adventure
- **Key Thematic Tags**: japanese production, kids, comedy
- **Representative Exemplar Titles**: Ringing Bell, DAICON IV Opening Animation, The Little Norse Prince, Natsu e no Tobira, Gamba's Adventure

---

## 4. Latent Space Visualizations & Manifold Projections
High-dimensional representations projected via PCA (2D & 3D) and t-SNE (2D):

### Elbow Silhouette
![Elbow Silhouette](figures_jp/elbow_silhouette.png)

### Pca 2D
![Pca 2D](figures_jp/pca_2d.png)

### Pca 3D
![Pca 3D](figures_jp/pca_3d.png)

### Tsne 2D
![Tsne 2D](figures_jp/tsne_2d.png)

### Cluster Heatmap
![Cluster Heatmap](figures_jp/cluster_heatmap.png)

---

## 5. Incremental Database Architecture & Fallback Strategy
1. **SQLite Persistent Database (`data/anime_catalog.db`)**: Deduplicates incoming anime by canonical ID (`anilist:{id}`, `kitsu:{id}`), tracking pagination state across runs.
2. **Rate Limit Throttling**: Implements configurable polite delays (`--rate-delay`) to prevent API rate limits or IP bans during large catalog harvests.
3. **Multi-Source Failover**: Queries AniList GraphQL endpoint by default. If AniList is rate-limited, unreachable, or returns insufficient records, queries Kitsu JSON:API, normalizing attributes into the standard schema.
4. **Offline Portability**: The database automatically exports full state to `data/raw_anime_data.json` for offline demonstration.

---
*Report auto-generated by the Antigravity Data Science Pipeline.*