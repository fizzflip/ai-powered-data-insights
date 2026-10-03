#import "../theme.typ": *

// ============================================================================
// CHAPTER 05: COMPARATIVE ORIGIN & GEO-CULTURAL TAXONOMY
// ============================================================================

#grid(
  columns: (1fr, auto),
  align: (horizon + left, horizon + right),
  [
    #telemetry-pill("COHORT DIVERGENCE", "JP DOMESTIC vs NON-JP OVERSEAS", color: nebula-cyan)
    #h(6pt)
    #telemetry-pill("TAXONOMY", "GEO-CULTURAL ARCHETYPES", color: star-gold)
  ],
  [
    #text(font: font-display, size: 7.5pt, fill: text-muted)[
      SECTION \/\/ 05.00
    ]
  ],
)

= Comparative Origin

Traditional anime scholarship and algorithmic recommender systems have historically treated the global animation catalog as a monolithic distribution dominated by Japanese broadcast television conventions. In contemporary multi-source databases containing tens of thousands of records, however, non-Japanese productions—most notably Chinese animation (*Donghua*, 动画), Korean animation (*Aeni*, 애니), and Western animated serials—represent rapidly expanding, structurally distinct production ecosystems.

Without cohort-aware partitioning, standard unsupervised dimensionality reduction and clustering models invariably collapse foreign productions into marginal outlier clusters characterized merely by low Western tracking volume. This chapter formalizes a rigorous comparative origin framework, isolating Japanese domestic titles (`jp`) from international works (`non-jp`) across catalog representation, format morphology, thematic genre divergence, and audience devotion dynamics.

== Regional Cohort Breakdown

The analytical catalog comprises 40,654 total records indexed in the persistent SQLite database, with 24,122 titles possessing verified geo-cultural origin attribution. Within this cohort-tagged corpus, Japanese domestic titles constitute 20,000 works (82.91%), while international productions encompass 4,122 titles (17.09%).

#v(8pt)
#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  grid(
    // size: 90%,
    // rows: (.5fr, .5fr),
    [#metric-card("JP Domestic", "20,000", subtitle: "82.9% of tagged catalog", delta: "Baseline")],
    [ \ ],
    [#metric-card("Chinese Donghua", "3,120", subtitle: "75.69% of Non-JP cohort", delta: "Dominant")],
  ),
  grid(
    // rows: (.5fr, .5fr),
    [#metric-card("Korean Aeni", "970", subtitle: "23.53% of Non-JP cohort", delta: "Rapid Growth")],
    [ \ ],
    [#metric-card("Western / Global", "32", subtitle: "0.78% of Non-JP cohort", delta: "Selective")],
  ),
)
#v(8pt)

In detailed controlled sampling ($N=100$, partitioned equally into 50 Japanese Domestic titles and 50 Overseas titles comprising 46 Donghua and 4 Aeni productions), cross-cohort metrics demonstrate that score parity coexists with dramatic popularity divergence:
#pagebreak()
#v(6pt)
#styled-table(
  columns: (1.5fr, 1.1fr, 1.1fr, 1.8fr),
  table.header(
    [#text(fill: star-gold, weight: "bold")[Metric Dimension]],
    [#text(fill: star-gold, weight: "bold")[JP Domestic (`jp`)]],
    [#text(fill: star-gold, weight: "bold")[Non-JP Overseas]],
    [#text(fill: star-gold, weight: "bold")[Empirical Structural Gap]],
  ),
  [Catalog Title Count ($N$)],
  [20,000 titles (82.9%)],
  [4,122 titles (17.1%)],
  [Domestic production primacy],
  [Mean Global Score],
  [64.12 / 100],
  [64.04 / 100],
  [Score parity across base catalog],
  [High-Tier Score Mean],
  [81.98 / 100],
  [77.04 / 100],
  [-4.94 pt gap in top-quartile cohorts],
  [Median Popularity (Log10)],
  [3.00 ($approx 10^3$ members)],
  [3.00 ($approx 10^3$ members)],
  [Comparable long-tail median],
  [Mean Popularity (Sample)],
  [653,743 members],
  [80,353 members],
  [-87.71% Western tracking visibility],
  [Devotion Ratio (`fav / pop`)],
  [0.0481 (4.81%)],
  [0.0289 (2.89%)],
  [Denser core conversion in JP hits],
)
#v(6pt)

#align(center)[
  #image("../assets/origin_distribution.png", width: 85%)
]

As depicted above, Chinese Donghua commands over three-quarters of the non-Japanese catalog, underpinned by rapid industrialization across domestic platforms such as Bilibili, Tencent Video, and iQIYI. Korean Aeni represents roughly one-quarter of international titles, propelled by high-value webtoon (*Manhwa*) intellectual property pipelines. Western animation cataloged on anime-specific platforms remains a boutique slice ($0.78\%$), restricted largely to high-profile anime-adjacent collaborations (*Cyberpunk: Edgerunners*, *Castlevania*, *The Legend of Korra*).

== Media Format & Distribution Mechanics

The architectural divergence between Japanese and international anime is fundamentally mechanical: it is rooted in distribution pipelines, episodic broadcast scheduling, and licensing contracts.

Traditional Japanese television animation operates within the rigorous constraints of the *Production Committee System* (*Seisaku Iinkai*), wherein terrestrial and satellite broadcast slots dictate strict 12-episode or 24-episode seasonal *cours*. Each broadcast episode must strictly occupy a 24-minute programming block (including commercial breaks, opening, and ending sequences). In contrast, Chinese Donghua is overwhelmingly released as *Original Net Animation (ONA)* directly onto streaming platforms, unencumbered by linear television schedules.

#align(center)[
  #image("../assets/format_comparison.png", width: 85%)
]

#spec-callout(title: "DISTRIBUTION PIPELINE TAXONOMY")[
  + *Japanese Broadcast Cour System*: Standardized into quarterly seasons (Winter, Spring, Summer, Fall). Episodic runtimes tightly adhere to $24.0 plus.minus 0.5$ minutes. Theatrical movies and Direct-to-Video Original Video Animations (OVAs) serve as supplementary monetization vectors for proven intellectual properties.
  + *Chinese Web-Streaming (ONA) Paradigm*: Unconstrained by terrestrial broadcast limits, Donghua episodes fluctuate between 15 and 20 minutes. Continuous weekly release models (*continuous multi-year serialization*) replace quarterly cours, enabling series like *Soul Land* (斗罗大陆) and *A Will Eternal* (一念永恒) to run continuously for over 100 to 250 consecutive episodes.
  + *Korean Digital Webtoon Cadence*: Primarily formatted as high-frequency web animations or compact prestige seasons (8 to 12 episodes) co-produced with Japanese animation studios (e.g., Studio Mir, Telecom Animation Film, MAPPA) or directly financed by digital publishing conglomerates (Naver, Kakao).
]

This format polarity explains the episodic distribution illustrated in the boxplots above: while the Japanese domestic median episode count remains pegged at standard cour units (12 or 24 episodes), the Non-JP cohort exhibits an expansive interquartile spread, with a lower median episode runtime ($approx 13$ minutes in web shorts) contrasting against monumental episodic runs exceeding 60 to 100 episodes in cultivation serials.

== Thematic & Genre Divergence

Geo-cultural divergence manifests with striking mathematical clarity in genre prevalence matrices. Rather than replicating the thematic profile of Japanese anime, international animation centers on narrative traditions unique to its cultural origins.

#align(center)[
  #image("../assets/genre_divergence.png", width: 85%)
]

#v(6pt)
#styled-table(
  columns: (1.5fr, 1.2fr, 1.2fr, 1.1fr, 1.5fr),
  table.header(
    [#text(fill: star-gold, weight: "bold")[Genre Name]],
    [#text(fill: star-gold, weight: "bold")[JP Prevalence (%)]],
    [#text(fill: star-gold, weight: "bold")[Non-JP Prevalence (%)]],
    [#text(fill: star-gold, weight: "bold")[Net Delta (% pts)]],
    [#text(fill: star-gold, weight: "bold")[Affinity Bias]],
  ),
  [*Fantasy*],
  [9.8% (42.0% top-tier)],
  [19.1% (42.0% top-tier)],
  [+9.3%],
  [Strong Non-JP Biased],
  [*Adventure*],
  [7.3% (44.0% top-tier)],
  [13.4% (32.0% top-tier)],
  [+6.1%],
  [Strong Non-JP Biased],
  [*Action*],
  [10.9% (64.0% top-tier)],
  [13.1% (56.0% top-tier)],
  [+2.2%],
  [Non-JP Leaning],
  [*Supernatural*],
  [36.0% (sample)],
  [42.0% (sample)],
  [+6.0%],
  [Non-JP Biased (Aeni / Donghua)],
  [*Comedy*],
  [14.1% (44.0% top-tier)],
  [12.3% (26.0% top-tier)],
  [-1.8%],
  [JP Leaning],
  [*Drama*],
  [8.1% (60.0% top-tier)],
  [5.7% (62.0% top-tier)],
  [-2.4%],
  [JP Leaning],
  [*Romance*],
  [6.1% (16.0% top-tier)],
  [2.9% (24.0% top-tier)],
  [-3.2%],
  [JP Leaning (Indexed MAL)],
  [*Slice of Life*],
  [6.1%],
  [2.4%],
  [-3.7%],
  [Strong JP Biased],
  [*Music*],
  [6.7%],
  [1.7%],
  [-5.0%],
  [Strong JP Biased],
  [*Psychological*],
  [20.0% (sample)],
  [2.0% (sample)],
  [-18.0%],
  [Overwhelming JP Biased],
)
#v(6pt)

=== Cultural Narrative Trademarks
- *Chinese Donghua (3D CGI Cultivation & Wuxia)*: The overwhelming dominance of Fantasy (19.1%) and Adventure (13.4%) in Donghua is driven by indigenous literary genres: *Xianxia* (仙侠, immortal heroes), *Wuxia* (武侠, martial heroes), and *Xuanhuan* (玄幻, eastern fantasy). Unlike Japanese 2D cel animation, Chinese studios (such as Sparkly Key Animation and Foch Film) heavily prioritize full 3D CGI pipelines using motion capture, high-polygon character assets, and GPU-accelerated rendering engines (Unreal Engine 5). Signature titles such as *Soul Land* (斗罗大陆), *Battle Through the Heavens* (斗破苍穹), and *Record of a Mortal's Journey to Immortality* (凡人修仙传) embody this hyper-kinetic, serialized progression formula.
- *Korean Aeni (Webtoon Transmedia & Urban Fantasy)*: Propelled by the global surge of webtoons, Korean animation focuses intensely on high-concept urban fantasy, "System" level-up tropes, and psychological power hierarchies (*Solo Leveling*, *Tower of God*, *Lookism*, *The God of High School*). Additionally, Korean independent animation preserves a rich tradition of nuanced romantic melodrama and social critique.
- *Western Global Animation (Adult Satire & Video Game Adaptations)*: Western titles represented in anime indices lean heavily toward high-budget prestige adaptations of gaming intellectual properties (*Castlevania*, *Arcane*, *Blood of Zeus*) and adult speculative fiction, characterized by orchestral cinematic scoring, 8-episode arcs, and graphic novel aesthetics.
- *Japanese Domestic (Broad-Spectrum Diversity)*: The Japanese catalog retains unmatched breadth across introspective genres that remain almost entirely unrepresented in international cohorts: *Slice of Life* (6.1% vs 2.4%), *Music / Idol* (6.7% vs 1.7%), and *Psychological Thrillers* (20.0% vs 2.0% in sampled cohorts), exemplified by *Steins;Gate*, *Neon Genesis Evangelion*, and *Monster*.

== Audience Devotion vs. Mainstream Popularity

Evaluating anime titles solely through Western tracking platforms (AniList, MyAnimeList, Kitsu) introduces systematic discovery distortions. Because Western communities disproportionately track Japanese television broadcasts, international anime suffers from an artificial popularity deficit that obscures genuine user devotion.

#align(center)[
  #image("../assets/score_popularity_comparison.png", width: 85%)
]

To evaluate true community commitment independent of raw exposure, we define the dimensionless *Audience Devotion Index* $D(x)$ for any given title $x$:

$ D(x) = frac(text("Favourites")(x), text("Popularity")(x) + epsilon) $

where $epsilon = 10$ acts as a smoothing regularization constant against small-sample denominator spikes.

In Japanese blockbuster releases (*Demon Slayer: Kimetsu no Yaiba*, *Jujutsu Kaisen*, *Attack on Titan*), mean popularity reaches 653,743 members with a devotion index of $D = 0.0481$ (4.81% of logged viewers favorite the title). For international titles, the mean popularity in the same tracking ecosystems plunges by 87.7% to 80,353 members (with a median of just 27,041). Despite this severe exposure filter, top-tier Donghua titles (*Grandmaster of Demonic Cultivation / Mo Dao Zu Shi*, *Heaven Official's Blessing / Tian Guan Ci Fu*, *Link Click / Shiguang Dailiren*) achieve devotion ratios exceeding $D = 0.055$, demonstrating core audience loyalty that surpasses many mainstream Japanese television broadcasts.

#parchment-card(title: "PRESCRIPTION NOTE // RECOMMENDER NORMALIZATION", stamp: "VERIFIED")[
  *Core Algorithmic Finding*: When pooling multi-origin catalogs into a single feature matrix without cohort normalization, $k$-means and Gaussian Mixture Models erroneously fuse high-prestige Chinese cultivation masterpieces with low-budget Japanese direct-to-video filler simply because both occupy the same low-popularity coordinate range on Western tracking platforms.

  *Architectural Remedy*: Recommender pipelines must compute *cohort-normalized popularity percentiles*:
  $ P_("norm")(x) = frac("Rank"(x mid c_x), abs(C_(c_x))) $
  where $c_x in {"JP", "CN", "KR", "WESTERN"}$. Normalizing within origin cohorts protects foreign cinematic masterworks from algorithmic marginalization and preserves diverse latent archetype resolution.
]
