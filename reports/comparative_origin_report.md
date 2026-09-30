# Comparative Cross-Market Anime Analysis: Japanese Domestic (JP) vs Overseas (Non-JP)

## Executive Summary
- **Total Catalog Volume Analyzed**: 4,000 titles (SQLite Persistent Database: 40,654 titles)
- **Japanese Domestic Cohort (JP)**: 2,000 titles (50.0% of catalog)
- **International / Overseas Cohort (Non-JP)**: 2,000 titles (50.0% of catalog)
  - **Chinese Animation (Donghua, `CN`)**: 1,436 titles (71.8% of Non-JP)
  - **Korean Animation (Aeni, `KR`)**: 544 titles (27.2% of Non-JP)
  - **Western / Global Animation (`WESTERN`)**: 20 titles (1.0% of Non-JP)
  - **Other Foreign Productions (`OTHER`)**: 0 titles (0.0% of Non-JP)
- **Optimal Unsupervised Archetype Resolution**: $k_{jp} = 7$ clusters vs $k_{non\_jp} = 7$ clusters

> [!IMPORTANT]
> **Core Analytical Finding**: Independent cohort clustering reveals that Chinese Donghua and Korean Aeni > form distinct structural ecosystems from Japanese broadcast anime. In joint pooling, Non-JP works are frequently > compressed into a single low-popularity outlier cluster. Cohort separation surfaces authentic market archetypes, > including high-frequency web-novel cultivation sagas, 3D CGI action epics, and highly devoted manhwa adaptations.

---

## 1. Catalog Composition & Regional Origin Breakdown

| Cohort / Region | Sub-Tag | Title Count | Catalog Share (%) | Non-JP Share (%) |
|:----------------|:-------:|:-----------:|:-----------------:|:----------------:|
| **Japanese Domestic** | `JP` | 2,000 | 50.0% | N/A |
| **Chinese Donghua** | `CN` | 1,436 | 35.9% | 71.8% |
| **Korean Aeni** | `KR` | 544 | 13.6% | 27.2% |
| **Western / Global** | `WESTERN` | 20 | 0.5% | 1.0% |
| **Other Overseas** | `OTHER` | 0 | 0.0% | 0.0% |
| **Total Combined** | -- | **4,000** | **100.0%** | **100.0%** |

### Market Breakdown Visualization
![Origin Distribution](figures_compare/origin_distribution.png)

---

## 2. Quantitative Metric Divergence Matrix
Key performance indicators, viewer devotion, and distribution format differences across cohorts:

| Metric Dimension | Japanese Domestic (JP) | Overseas (Non-JP) | Divergence / Structural Difference |
|:-----------------|:----------------------:|:-----------------:|:-----------------------------------|
| **Mean Average Score** | 73.37 / 100 | 64.54 / 100 | -8.83 pts |
| **Median Average Score** | 74.0 / 100 | 65.0 / 100 | -9.0 pts |
| **Mean Popularity** | 124,908 members | 3,087 members | -97.5% |
| **Median Popularity** | 79,080 members | 1,000 members | Strong Western platform discovery gap |
| **Mean Favourites** | 3,619 | 131 | Core viewer concentration |
| **Devotion Ratio** (`fav / pop`) | 0.0216 | 0.0482 | Higher niche core devotion |
| **Mean Episode Count** | 15.4 eps | 22.3 eps | Web release serialized pacing |
| **Median Episode Duration** | 24 mins | 13 mins | TV broadcast cour (24m) vs Web/ONA (15-20m) |

### Distribution Comparative Figures
![Score & Popularity Comparison](figures_compare/score_popularity_comparison.png)

![Format & Duration Comparison](figures_compare/format_comparison.png)

---

## 3. Thematic & Genre Affinity Divergence
Relative prevalence of dominant genres within each market cohort (% of titles featuring genre):

| Genre Name | JP Domestic Prevalence (%) | Non-JP Prevalence (%) | Cohort Divergence (% pts) | Affinity Bias |
|:-----------|:---------------------------:|:---------------------:|:--------------------------:|:--------------|
| **Action** | 45.9% | 25.1% | -20.8% | JP Biased |
| **Comedy** | 46.4% | 22.9% | -23.5% | JP Biased |
| **Fantasy** | 36.3% | 31.9% | -4.4% | JP Biased |
| **Drama** | 37.0% | 12.2% | -24.8% | JP Biased |
| **Adventure** | 25.9% | 20.8% | -5.1% | JP Biased |
| **Romance** | 34.2% | 6.7% | -27.5% | JP Biased |
| **Slice of Life** | 26.1% | 3.9% | -22.2% | JP Biased |
| **Supernatural** | 23.4% | 5.0% | -18.4% | JP Biased |
| **Sci-Fi** | 16.5% | 9.4% | -7.1% | JP Biased |
| **Mystery** | 13.3% | 2.5% | -10.9% | JP Biased |

### Top Genre Divergence Visualization
![Genre Divergence](figures_compare/genre_divergence.png)

---

## 4. Cross-Market Unsupervised Archetype Contrast

### A. Japanese Domestic Archetypes ($k=7$)
The Japanese domestic market exhibits high structural diversity across broadcast television eras, late-night cours, and prestige cinematic releases:

| Cluster ID | Archetype Label | Size | Share (%) | Mean Score | Mean Popularity | Top Exemplars |
|:----------:|:----------------|:----:|:---------:|:----------:|:---------------:|:--------------|
| 0 | **Specialized Archetype (Comedy Focus)** | 362 | 18.1% | 75.9 | 69,700 | Haikyu!! 3rd Season, My Hero Academia Season 5, Uzaki-chan Wants to Hang Out! |
| 1 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [Male Protagonist • Core Reach]** | 427 | 21.3% | 67.2 | 60,815 | Haganai, BTOOOM!, My First Girlfriend is a Gal |
| 2 | **Specialized Archetype (Drama Focus) [Male Protagonist • High Reach]** | 154 | 7.7% | 83.2 | 382,182 | Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN |
| 3 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [Magic • Core Reach]** | 330 | 16.5% | 66.3 | 80,775 | The Promised Neverland Season 2, Boruto: Naruto Next Generations, How NOT to Summon a Demon Lord |
| 4 | **Specialized Archetype (Drama Focus) [Female Protagonist • Broad Reach]** | 221 | 11.1% | 77.3 | 100,688 | Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, Spirited Away, JUJUTSU KAISEN 0 |
| 5 | **Modern Hits (Blockbuster Action)** | 349 | 17.4% | 76.8 | 223,646 | Sword Art Online, My Hero Academia Season 2, Attack on Titan |
| 6 | **Classics (Historical Favorites)** | 157 | 7.8% | 76.6 | 81,528 | Fullmetal Alchemist, A Certain Magical Index, Fate/stay night |

#### Japanese Domestic Visualizations
![JP Latent Space PCA 2D](figures_jp/pca_2d.png)

![JP Cluster Heatmap](figures_jp/cluster_heatmap.png)

### B. Overseas / Non-JP Archetypes ($k=7$)
The overseas market (heavily propelled by Chinese streaming platforms such as Bilibili and Tencent, alongside Korean webtoon studios) converges into distinct production paradigms:

| Cluster ID | Archetype Label | Size | Share (%) | Mean Score | Mean Popularity | Top Exemplars |
|:----------:|:----------------|:----:|:---------:|:----------:|:---------------:|:--------------|
| 0 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach]** | 202 | 10.1% | 60.1 | 1,000 | 15 Children Space Adventure, 77 Danui Bimil, A Long He Lili |
| 1 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 1)** | 629 | 31.4% | 64.4 | 1,000 | 12生肖全家福網絡世界歷險, 12生肖全家福的神奇世界, 23号牛乃糖 |
| 2 | **Specialized Archetype (Drama Focus)** | 47 | 2.4% | 78.5 | 83,570 | Your lie in April, Blue Exorcist, The Apothecary Diaries |
| 3 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]** | 453 | 22.7% | 63.6 | 1,000 | I=Fantasy, (Mi)Liu, (OO) |
| 4 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 4)** | 220 | 11.0% | 61.8 | 1,004 | Thunderbolt Fantasy - Bewitching Melody of the West, 81号农场之保卫麦咭, 81 Hao Nongchang: Fengkuang De Mai Ji |
| 5 | **Specialized Archetype (Fantasy Focus)** | 101 | 5.1% | 70.2 | 3,751 | The Silver Guardian, TO BE HERO, To Be Heroine |
| 6 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Broad Reach]** | 348 | 17.4% | 66.7 | 1,044 | Swallowed Star, Soul Land 2: The Peerless Tang Clan, Tunshi Xingkong 2 |

#### Overseas (Non-JP) Visualizations
![Non-JP Latent Space PCA 2D](figures_non_jp/pca_2d.png)

![Non-JP Cluster Heatmap](figures_non_jp/cluster_heatmap.png)

---

## 5. Architectural & Algorithmic Implications
1. **Mitigation of Representation Bias**: In global databases (AniList, MyAnimeList, Kitsu), Western community engagement with Non-JP anime is lower by orders of magnitude compared to mainstream Japanese seasonal anime. When clustering without origin cohorting, standard clustering algorithms inadvertently clump high-budget Chinese cultivation epics (e.g. *Soul Land*, *A Will Eternal*, *Mo Dao Zu Shi*) with obscure Japanese OVAs simply due to lower raw member counts.
2. **Production Cadence & Format Divergence**: Chinese Donghua predominantly adopts ONA web serialization with episodes ranging between 15 and 20 minutes, operating under multi-year continuous release models rather than Japanese 12-to-24-episode seasonal television broadcast cours.
3. **Recommendation Engine Optimization**: Recommender architectures must apply cohort-aware scoring or feature normalization. Calculating normalized relative popularity within cohort preserves the prestige and discovery of top-tier foreign masterpieces.

---
*Report auto-generated by the Antigravity Comparative Origin Analysis Engine.*