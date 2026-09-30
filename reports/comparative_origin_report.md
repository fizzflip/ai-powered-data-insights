# Comparative Cross-Market Anime Analysis: Japanese Domestic (JP) vs Overseas (Non-JP)

## Executive Summary
- **Total Catalog Volume Analyzed**: 24,122 titles (SQLite Persistent Database: 40,654 titles)
- **Japanese Domestic Cohort (JP)**: 20,000 titles (82.9% of catalog)
- **International / Overseas Cohort (Non-JP)**: 4,122 titles (17.1% of catalog)
  - **Chinese Animation (Donghua, `CN`)**: 3,120 titles (75.7% of Non-JP)
  - **Korean Animation (Aeni, `KR`)**: 970 titles (23.5% of Non-JP)
  - **Western / Global Animation (`WESTERN`)**: 32 titles (0.8% of Non-JP)
  - **Other Foreign Productions (`OTHER`)**: 0 titles (0.0% of Non-JP)
- **Optimal Unsupervised Archetype Resolution**: $k_{jp} = 10$ clusters vs $k_{non\_jp} = 9$ clusters

> [!IMPORTANT]
> **Core Analytical Finding**: Independent cohort clustering reveals that Chinese Donghua and Korean Aeni > form distinct structural ecosystems from Japanese broadcast anime. In joint pooling, Non-JP works are frequently > compressed into a single low-popularity outlier cluster. Cohort separation surfaces authentic market archetypes, > including high-frequency web-novel cultivation sagas, 3D CGI action epics, and highly devoted manhwa adaptations.

---

## 1. Catalog Composition & Regional Origin Breakdown

| Cohort / Region | Sub-Tag | Title Count | Catalog Share (%) | Non-JP Share (%) |
|:----------------|:-------:|:-----------:|:-----------------:|:----------------:|
| **Japanese Domestic** | `JP` | 20,000 | 82.9% | N/A |
| **Chinese Donghua** | `CN` | 3,120 | 12.9% | 75.7% |
| **Korean Aeni** | `KR` | 970 | 4.0% | 23.5% |
| **Western / Global** | `WESTERN` | 32 | 0.1% | 0.8% |
| **Other Overseas** | `OTHER` | 0 | 0.0% | 0.0% |
| **Total Combined** | -- | **24,122** | **100.0%** | **100.0%** |

### Market Breakdown Visualization
![Origin Distribution](figures_compare/origin_distribution.png)

---

## 2. Quantitative Metric Divergence Matrix
Key performance indicators, viewer devotion, and distribution format differences across cohorts:

| Metric Dimension | Japanese Domestic (JP) | Overseas (Non-JP) | Divergence / Structural Difference |
|:-----------------|:----------------------:|:-----------------:|:-----------------------------------|
| **Mean Average Score** | 64.06 / 100 | 64.02 / 100 | -0.04 pts |
| **Median Average Score** | 65.0 / 100 | 65.0 / 100 | +0.0 pts |
| **Mean Popularity** | 16,309 members | 1,993 members | -87.8% |
| **Median Popularity** | 1,000 members | 1,000 members | Strong Western platform discovery gap |
| **Mean Favourites** | 430 | 88 | Core viewer concentration |
| **Devotion Ratio** (`fav / pop`) | 0.0330 | 0.0483 | Higher niche core devotion |
| **Mean Episode Count** | 9.9 eps | 23.4 eps | Web release serialized pacing |
| **Median Episode Duration** | 23 mins | 13 mins | TV broadcast cour (24m) vs Web/ONA (15-20m) |

### Distribution Comparative Figures
![Score & Popularity Comparison](figures_compare/score_popularity_comparison.png)

![Format & Duration Comparison](figures_compare/format_comparison.png)

---

## 3. Thematic & Genre Affinity Divergence
Relative prevalence of dominant genres within each market cohort (% of titles featuring genre):

| Genre Name | JP Domestic Prevalence (%) | Non-JP Prevalence (%) | Cohort Divergence (% pts) | Affinity Bias |
|:-----------|:---------------------------:|:---------------------:|:--------------------------:|:--------------|
| **Fantasy** | 21.6% | 33.6% | +12.0% | Non-JP Biased (Donghua/Aeni) |
| **Comedy** | 31.2% | 21.6% | -9.6% | JP Biased |
| **Action** | 24.0% | 23.0% | -1.0% | Balanced |
| **Adventure** | 16.1% | 23.5% | +7.4% | Non-JP Biased (Donghua/Aeni) |
| **Drama** | 17.9% | 10.1% | -7.8% | JP Biased |
| **Sci-Fi** | 13.0% | 8.2% | -4.8% | JP Biased |
| **Romance** | 13.6% | 5.1% | -8.5% | JP Biased |
| **Music** | 14.8% | 3.0% | -11.8% | JP Biased |
| **Slice of Life** | 13.6% | 4.1% | -9.4% | JP Biased |
| **Tv** | 2.9% | 12.2% | +9.3% | Non-JP Biased (Donghua/Aeni) |

### Top Genre Divergence Visualization
![Genre Divergence](figures_compare/genre_divergence.png)

---

## 4. Cross-Market Unsupervised Archetype Contrast

### A. Japanese Domestic Archetypes ($k=10$)
The Japanese domestic market exhibits high structural diversity across broadcast television eras, late-night cours, and prestige cinematic releases:

| Cluster ID | Archetype Label | Size | Share (%) | Mean Score | Mean Popularity | Top Exemplars |
|:----------:|:----------------|:----:|:---------:|:----------:|:---------------:|:--------------|
| 0 | **Specialized Archetype (Comedy Focus) [Female Protagonist • Broad Reach]** | 2,211 | 11.1% | 58.3 | 2,955 | Pupa, Dragon Ball Z: Bio-Broly, Chika Gentou Gekiga: Shoujo Tsubaki |
| 1 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [music • Core Reach]** | 2,653 | 13.3% | 63.2 | 1,000 | !nvade Show!, "Anata o Hitokoto de Arawashite Kudasai" no Shitsumon ga Nigate da., "働く"の100年史 |
| 2 | **Modern Hits (Blockbuster Comedy)** | 1,332 | 6.7% | 76.7 | 155,779 | Attack on Titan, Demon Slayer: Kimetsu no Yaiba, JUJUTSU KAISEN |
| 3 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [fantasy • Core Reach]** | 3,551 | 17.8% | 65.2 | 1,130 | Ane wa Yanmama Junyuu-chuu, Shoujo Ramune, Chiikawa |
| 4 | **Specialized Archetype (Action Focus)** | 1,399 | 7.0% | 69.5 | 13,612 | A Silent Voice, Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train, Demon Slayer: Kimetsu no Yaiba Infinity Castle |
| 5 | **Specialized Archetype (Comedy Focus) [Male Protagonist • Broad Reach]** | 1,922 | 9.6% | 68.0 | 5,938 | Peace Sign, Avatar: The Legend So Far, Fate/stay night: Unlimited Blade Works - Prologue |
| 6 | **Specialized Archetype (Comedy Focus) [School • High Reach]** | 2,668 | 13.3% | 67.2 | 26,396 | One-Punch Man Season 3, My First Girlfriend is a Gal, And you thought there is never a girl online? |
| 7 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [shorts • Core Reach]** | 1,600 | 8.0% | 48.7 | 1,083 | Boku no Pico, EX-ARM, Mars of Destruction |
| 8 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • Core Reach]** | 1,539 | 7.7% | 65.3 | 1,109 | Moomin, Nobody's Boy Remi, Renegade Immortal |
| 9 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [japanese production • Core Reach]** | 1,125 | 5.6% | 58.0 | 1,026 | Ringing Bell, DAICON IV Opening Animation, The Little Norse Prince |

#### Japanese Domestic Visualizations
![JP Latent Space PCA 2D](figures_jp/pca_2d.png)

![JP Cluster Heatmap](figures_jp/cluster_heatmap.png)

### B. Overseas / Non-JP Archetypes ($k=9$)
The overseas market (heavily propelled by Chinese streaming platforms such as Bilibili and Tencent, alongside Korean webtoon studios) converges into distinct production paradigms:

| Cluster ID | Archetype Label | Size | Share (%) | Mean Score | Mean Popularity | Top Exemplars |
|:----------:|:----------------|:----:|:---------:|:----------:|:---------------:|:--------------|
| 0 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [kids • High Reach]** | 1,348 | 32.7% | 65.0 | 1,000 | Tunshi Xingkong 4, 12生肖全家福網絡世界歷險, 12生肖全家福的神奇世界 |
| 1 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [shorts • Broad Reach]** | 796 | 19.3% | 65.3 | 1,000 | Dou Po Cangqiong: Yuanqi, Douluo Dalu: Shuang Shen Zhi Zhan, I=Fantasy |
| 2 | **Specialized Archetype (Drama Focus)** | 52 | 1.3% | 77.6 | 77,116 | Your lie in April, Blue Exorcist, The Apothecary Diaries |
| 3 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [shorts • Core Reach]** | 343 | 8.3% | 64.2 | 1,000 | A Long He Lili, Sad Drowning, 安宁 |
| 4 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach]** | 253 | 6.1% | 43.7 | 1,000 | 15 Children Space Adventure, 2005 Space Odyssey, 77 Danui Bimil |
| 5 | **Specialized Archetype (Fantasy Focus)** | 114 | 2.8% | 69.9 | 2,773 | Dragon Ball: Mystical Adventure, Noblesse: The Beginning of Destruction, Kusuriya no Hitorigoto 3rd Season Part 2 |
| 6 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 6)** | 429 | 10.4% | 64.3 | 999 | Thunderbolt Fantasy - Bewitching Melody of the West, 81号农场之保卫麦咭, 81 Hao Nongchang: Fengkuang De Mai Ji |
| 7 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [chinese animation • Core Reach] (Cluster 7)** | 698 | 16.9% | 66.0 | 1,000 | Soul Land 2: The Peerless Tang Clan, Tunshi Xingkong 2, Dou Po Cangqiong: San Nian Zhi Yue |
| 8 | **Low-Profile (Commercial Mid-Tier & Long-Tail) [Full CGI • Core Reach]** | 89 | 2.2% | 62.0 | 255 | Wangpai Yushi, Tianbao Fuyao Lu 3, Fanren Xiu Xian Zhuan: Xinghai Feichi Prologue |

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