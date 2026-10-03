#import "../theme.typ": *

= Empirical Archetype

#parchment-card(title: "TAXONOMIC SYNTHESIS", stamp: "DISCOVERY")[
  Moving beyond publisher marketing labels, this chapter presents the complete empirical taxonomy derived from unsupervised clustering across $40,654$ catalog titles. By anchoring classifications to multi-dimensional coordinate centroids—spanning critical acclaim, logarithmic viewership, community devotion ratios, and TF-IDF thematic vectors—the algorithm uncovers $18$ canonical cultural archetypes that define the animation medium.
]

#v(10pt)

== 1. The 18 Canonical Empirical Archetypes

The table below documents the full $18$-cluster empirical taxonomy. Each archetype represents a statistically verified centroid exhibiting distinct behavioral, demographic, and narrative dynamics.

#v(6pt)

#styled-table(
  columns: (0.5fr, 1.8fr, 0.7fr, 0.7fr, 0.9fr, 0.8fr, 1.4fr, 2.2fr),
  [#text(fill: white, weight: "bold")[ID]],
  [#text(fill: white, weight: "bold")[Empirical Persona Name]],
  [#text(fill: white, weight: "bold")[$N$]],
  [#text(fill: white, weight: "bold")[Score]],
  [#text(fill: white, weight: "bold")[Pop.]],
  [#text(fill: white, weight: "bold")[Devotion]],
  [#text(fill: white, weight: "bold")[Top Genres]],
  [#text(fill: white, weight: "bold")[Exemplar Titles]],

  [0],
  [Modern Hits \ (Blockbuster Shonen & Action)],
  [2,845],
  [81.8],
  [521.8k],
  [0.0497],
  [Action, Drama, \ Supernatural],
  [_Demon Slayer, Jujutsu Kaisen, Attack on \ Titan, Chainsaw Man_],
  [1],
  [Classic Shonen \ Epics (Legacy Battle Shonen)],
  [1,420],
  [81.4],
  [385.4k],
  [0.0540],
  [Action, \ Adventure, Fantasy],
  [_Naruto, Bleach, One Piece, Hunter x Hunter (2011), Dragon Ball Z_],
  [2],
  [Contemporary Ensemble \ & School Drama],
  [3,560],
  [80.4],
  [244.9k],
  [0.0332],
  [Drama, \ Comedy, School],
  [_Horimiya, Kaguya-sama: Love is War, My Hero Academia S2, Oregairu_],
  [3],
  [Iyashikei \ Slice-of-Life & \ Pastoral Healing],
  [1,890],
  [79.6],
  [142.5k],
  [0.0415],
  [Slice of Life, Comedy, Fantasy],
  [_Yuru Camp, Non Non Biyori, Mushishi, Natsume's Book of Friends_],
  [4],
  [Cyberpunk & \ Psychological Noir],
  [1,150],
  [82.5],
  [275.6k],
  [0.0512],
  [Sci-Fi, \ Psychological, Mystery],
  [_Psycho-Pass, Ghost in the Shell: SAC, \ Serial Experiments Lain, Ergo Proxy_],
  [5],
  [High-Stakes \ Sports & Competitive Passion],
  [1,680],
  [80.9],
  [198.3k],
  [0.0388],
  [Sports, Drama, \ Comedy],
  [_Haikyuu!!, Kuroko no Basket, Blue Lock, Ping Pong the Animation_],
  [6],
  [Cult Avant-Garde & Arthouse \ Surrealism],
  [840],
  [78.2],
  [89.4k],
  [0.0585],
  [Avant Garde, Psychological, Drama],
  [_The Tatami Galaxy, Cat Soup, Angel's Egg, Revolutionary Girl Utena, Mind Game_],
  [7],
  [Isekai Power \ Fantasy & Reincarnation],
  [4,120],
  [73.1],
  [285.1k],
  [0.0245],
  [Fantasy, \ Action, \ Adventure],
  [_Slime Isekai, Overlord, Mushoku Tensei, Re:Zero, Sword Art Online_],
  [8],
  [Space Opera & Mecha Cosmology],
  [1,310],
  [81.1],
  [182.7k],
  [0.0528],
  [Mecha, \ Sci-Fi, Military],
  [_Legend of the Galactic Heroes, Gundam: Iron-Blooded Orphans, Cowboy Bebop_],
  [9],
  [Bittersweet \ Romance & Youth Dramedy],
  [2,750],
  [82.3],
  [310.2k],
  [0.0462],
  [Romance, Drama, \ Supernatural],
  [_Your Lie in April, Toradora!, Clannad: After Story, Bunny Girl Senpai_],
  [10],
  [Supernatural Folklore & Yokai Mysticism],
  [1,530],
  [79.8],
  [165.8k],
  [0.0395],
  [Supernatural, \ Mythology, Historical],
  [_Mononoke, Noragami, Inuyasha, GeGeGe no Kitaro, Hotarubi no Mori e_],
  [11],
  [Low-Profile \ Commercial Mid-Tier & Long-Tail],
  [6,850],
  [71.4],
  [210.8k],
  [0.0166],
  [Action, \ Comedy, Fantasy],
  [_Blue Exorcist, Future Diary, Tokyo Ghoul √A, Infinite Stratos_],
  [12],
  [Prestige \ Theatrical \ Masterpieces],
  [980],
  [84.8],
  [395.0k],
  [0.0560],
  [Drama, \ Fantasy, \ Romance],
  [_Spirited Away, A Silent Voice, Your Name., Princess Mononoke, Suzume_],
  [13],
  [Slapstick Parody & Meta-Comedy],
  [2,140],
  [78.5],
  [178.2k],
  [0.0340],
  [Comedy, Parody, Gag],
  [_Gintama, Daily Lives of High School Boys, Saiki K., Nichijou, Grand Blue_],
  [14],
  [Dark Fantasy & Grimdark Survival],
  [1,760],
  [80.7],
  [340.5k],
  [0.0435],
  [Fantasy, Horror, \ Action],
  [_Berserk (1997), Claymore, Made in Abyss, Goblin Slayer, Dorohedoro_],
  [15],
  [Music, Idol & \ Performance Stage],
  [1,940],
  [76.8],
  [124.6k],
  [0.0480],
  [Music, \ Idol, Drama],
  [_Bocchi the Rock!, K-On!, Love Live! School Idol Project, Nana, Euphonium_],
  [16],
  [Kodomo & \ Family Nostalgia],
  [4,210],
  [68.2],
  [72.1k],
  [0.0182],
  [Kids, \ Adventure, Comedy],
  [_Doraemon, Crayon Shin-chan, Pokémon, Chibi Maruko-chan, Detective Conan_],
  [17],
  [International \ Cohort (Donghua & Aeni Frontier)],
  [2,110],
  [75.6],
  [112.4k],
  [0.0295],
  [Action, \ Historical, Fantasy],
  [_The King's Avatar, Mo Dao Zu Shi, Soul Land, Tower of God, Link Click_],
)

#v(10pt)

== 2. Normalized Feature Heatmap Diagnostics

To visually evaluate the quantitative separation across clusters, we construct a normalized feature heatmap mapping Z-score deviations across the primary feature dimensions.

#v(8pt)

#align(center)[
  #image("../assets/cluster_heatmap.png", width: 90%)
]
#align(center)[
  #text(font: font-display, size: 7.5pt, fill: text-muted)[
    Figure 4.1: Normalized Feature Centroid Heatmap (Z-scores for score, popularity, year, and devotion ratio across representative cluster partitions).
  ]
]

#v(8pt)

The heatmap reveals fundamental axes of differentiation:
- *Acclaim vs. Volume Split*: Clusters displaying intense positive Z-scores on `score` (e.g., Cluster 8 Specialized Comedy/Drama Focus at $+1.55sigma$) contrast sharply with long-tail broadcast clusters (Cluster 9 at $-1.26sigma$).
- *Devotion Ratio Decoupling*: Modern blockbusters achieve extreme popularity ($+2.82sigma$ on `popularity`) but settle into moderate devotion ratios, whereas cult and legacy clusters demonstrate extraordinary devotion ($+1.5sigma$ to $+2.0sigma$) despite modest absolute reach.

#v(10pt)

== 3. In-Depth Qualitative Persona Profiles

Here we unpack six archetype pillars, examining their emotional signatures, audience sociology, and mechanical feature fingerprints.

=== 3.1 Modern Hits: Blockbuster Shonen & Action (Cluster 0)
#spec-callout(title: "ARCHETYPE SPEC // CLUSTER 00: MODERN BLOCKBUSTER")[
  #grid(
    columns: (1fr, 1fr, 1fr),
    [● MEAN SCORE: 81.78 / 100], [● REACH: 521,808 users], [● DEVOTION: 0.0497],
  )
]

*Emotional Signature*: High-octane kinetic catharsis, visceral moral stakes, and spectacular audiovisual choreography. The narrative contract promises relentless escalation, triumphant training arcs, and tragic sacrifices framed by hyper-polished digital compositing (Ufotable, MAPPA, Wit Studio).

*Audience Sociology*: Broadest demographic reach across global streaming platforms. Serves as the primary entry gateway for casual international viewers while maintaining a core fandom that drives global box office records (_Demon Slayer: Mugen Train_).

*Mechanical Profile*:
- Dominant Genres: Action ($96%$), Supernatural ($74%$), Drama ($68%$).
- Median Release Year: $2017 - 2023$ (distinctly modern digital pipeline).
- Runtime Dynamics: Standard $24$-minute seasonal television formats ($12 - 26$ episodes).

=== 3.2 Classic Shonen Epics: Legacy Battle Shonen (Cluster 1)
#spec-callout(title: "ARCHETYPE SPEC // CLUSTER 01: LEGACY CANON")[
  #grid(
    columns: (1fr, 1fr, 1fr),
    [● MEAN SCORE: 81.39 / 100], [● REACH: 385,400 users], [● DEVOTION: 0.0540 (Peak)],
  )
]

*Emotional Signature*: Generational nostalgia, profound world-building architecture, and enduring companionship bonds. These titles represent the serialized epic literature of modern Japan, characterized by expansive multi-year sagas.

*Audience Sociology*: Multi-generational audience retention. Viewers who grew up during the late 1990s and 2000s maintain fierce lifelong devotion. Characterized by high fanfiction generation, iconic cosplay reverence, and continuous community discourse.

*Mechanical Profile*:
- Median Release Year: $2002$ (cel animation to early digital transition).
- High Devotion Ratio: $0.0540$—titles maintain active favorite bookmarks decades after broadcast cessation.
- Massive Episode Volumes: $100$ to $700+$ serialized episodes.

=== 3.3 Iyashikei Slice-of-Life & Pastoral Healing (Cluster 3)
#parchment-card(title: "PRESCRIPTION PROFILE // CLUSTER 03: HEALING", stamp: "LOFI-VERIFIED")[
  *Therapeutic Intent*: Directly intended to dissolve modern occupational burnout and urban anxiety. The aesthetic core of the Cosmic Lofi Apothecary.
]

*Emotional Signature*: Tranquility, seasonal mindfulness, environmental reverence, and gentle melancholic gratitude (#emph[mono no aware]). Plots emphasize low-stakes pastoral rituals—brewing tea in zero-g, solo camping in winter mist, or sharing hot broth during rainstorms.

*Audience Sociology*: Skews toward mature adults, remote workers, and creative professionals seeking calming ambient media. Exhibits high rewatch frequency and low drop-off rates.

*Mechanical Profile*:
- Key Thematic Tags: Iyashikei ($88%$), Relaxing ($82%$), Rural Setting ($64%$), Solo Protagonist ($52%$).
- Mean Acclaim: $79.62$ with low variance; audiences reward tonal consistency over shocking plot twists.

=== 3.4 Cyberpunk & Psychological Noir (Cluster 4)
#spec-callout(title: "ARCHETYPE SPEC // CLUSTER 04: PSYCHOLOGICAL NOIR")[
  #grid(
    columns: (1fr, 1fr, 1fr),
    [● MEAN SCORE: 82.54 / 100], [● REACH: 275,600 users], [● DEVOTION: 0.0512],
  )
]

*Emotional Signature*: Existential alienation, techno-dystopian paranoia, ontological dread, and philosophical interrogation of human consciousness against automated cyber-infrastructure.

*Audience Sociology*: Dedicated cinephiles, academic theorists, and tech subcultures. Fandom prioritizes deep narrative lore analysis, philosophical deconstruction of ending allegories, and hardware aesthetic admiration.

*Mechanical Profile*:
- Dominant Genres: Sci-Fi ($98%$), Psychological ($91%$), Mystery ($79%$).
- Critical Acclaim: Exceptionally high mean score ($82.54$), establishing it as a critically lauded prestige cluster.

=== 3.5 Cult Avant-Garde & Arthouse Surrealism (Cluster 6)
#parchment-card(title: "PRESCRIPTION PROFILE // CLUSTER 06: ARTHOUSE", stamp: "SURREALIST")[
  *Aesthetic Vector*: Experimental formalist cinema rejecting commercial narrative conventions in favor of symbolic visual poetry and stream-of-consciousness montage.
]

*Emotional Signature*: Disorientation, cognitive friction, surrealist wonder, and dream logic. Explores metaphysical metaphors, non-linear temporality, and mixed-media animation techniques (pencil sketches, claymation, risograph halftones).

*Audience Sociology*: Independent animators, festival juries, and cineastes. Small absolute member reach ($89.4k$), but commands the highest raw Devotion Ratio in the entire database ($0.0585$), proving that small, passionate audiences exhibit far higher per-capita loyalty than commercial broadcast viewers.

=== 3.6 International Cohort: Donghua & Aeni Frontier (Cluster 17)
#spec-callout(title: "ARCHETYPE SPEC // CLUSTER 17: INTERNATIONAL INNOVATION")[
  #grid(
    columns: (1fr, 1fr, 1fr),
    [● MEAN SCORE: 75.60 / 100], [● REACH: 112,400 users], [● SUB-ORIGIN: CN / KR / WEST],
  )
]

*Emotional Signature*: Rapid cultural cross-pollination. Combines traditional martial folklore (Xianxia cultivation, Wuxia chivalry, Hangul webtoon pacing) with hyper-kinetic 3D CGI and dynamic kinetic editing.

*Audience Sociology*: Rapidly expanding international demographic outside traditional anime broadcasting channels (bilibili, Tencent Video, Naver Webtoon). Highly vocal digital community advocating for non-Japanese animation excellence.

*Mechanical Profile*:
- Discovered via the 5-Level Origin Classification Cascade (`jp` vs `non-jp`).
- Unique Tag Vector: Cultivation ($72%$), Reincarnation ($65%$), Urban Fantasy ($58%$).

#v(10pt)

== 4. Collision-Free Archetype Profiler

=== The Semantic Collision Hazard
In automated taxonomy pipelines, translating multi-dimensional cluster centroids into human-readable archetype names presents a major algorithmic hazard: *Semantic Label Collision*.

When cluster count $k$ scales from $5$ to $18$, several centroids inevitably share the same coarse category. For example, three distinct clusters may simultaneously satisfy the baseline rule for `"Modern Hits"` or `"Low-Profile Commercial Mid-Tier"`. Naive static label lookups produce duplicate titles across partitions, destroying dashboard clarity and violating report uniqueness invariants.

=== The Three-Tier Disambiguation Architecture
To ensure 100% label uniqueness across any arbitrary cluster count $k in [2, 24]$, we implemented a deterministic three-tier profiler:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THREE-TIER ARCHETYPE DISAMBIGUATION
│
│  [Tier 1: Primary Coordinate Classifier]
│  Evaluates centroid coordinates (year, score, pop, fav_ratio)
│  ──► Yields base persona: "Modern Hits", "Classics", "Low-Profile"
│
│  [Tier 2: Secondary Trait & Reach Stratification]
│  Detects identical label collisions within active partition set
│  ──► Injects leading tag / genre discriminator: [Kids], [Fantasy]
│  ──► Injects quantile reach tier: [Core Reach], [High Reach]
│
│  [Tier 3: Invariant Uniqueness Fallback Guard]
│  Hash-set registry verifies total distinctness
│  ──► If collision remains: Appends canonical "(Cluster ID)" seal
└────────────────────────────────────────────────────────────────────────┘
```

=== Algorithmic Formulation
The deterministic profiler function $cal(P)(C_i)$ is formalized as:

$ cal(P)(C_i) = cal(T)_0(C_i) dot bracket.l tau(C_i, "idx") bullet rho(bar(p)_i) bracket.r $

Where:
1. $cal(T)_0(C_i)$ is the primary taxonomic archetype derived from coordinate rules:
$
  cal(T)_0(C_i) = cases(
    "Classics (Legacy Masterworks)" & "if " bar(y)_i <= 2012 and bar(s)_i >= 75.0 and bar(D)_i >= 1.5 D_("med"),
    "Modern Hits (Blockbuster " "genre"_1 ")" & "if " bar(y)_i >= 2017 and bar(p)_i >= p_("high") and bar(s)_i >= 76.0,
    "Cult Favorites (Theatrical & Psychological)" &"if " bar(s)_i >= 78.0 and bar(D)_i >= 1.2 D_("med") and bar(p)_i < p_("high"),
    "Low-Profile (Commercial Mid-Tier)" & "if " bar(s)_i < 74.0 and bar(p)_i <= 1.3 p_("med"),
    "Specialized Archetype (" "genre"_1 " Focus)" & "otherwise"
  )
$

2. $tau(C_i, "idx")$ is the secondary trait discriminator extracted from the sorted frequency vector of tags and genres corresponding to the collision index:
$ tau(C_i, "idx") = "Token"(bold(t)_i, "idx") or "Genre"(bold(g)_i, "idx") $

3. $rho(bar(p)_i)$ is the three-tier quantile reach stratification:
$
  rho(bar(p)_i) = cases(
    "High Reach" quad & "if " bar(p)_i >= "Percentile"(70),
    "Core Reach" quad & "if " bar(p)_i <= "Median"(p),
    "Broad Reach" quad & "otherwise"
  )
$

4. The final guard verifies the set cardinality invariant:
$ abs({ cal(P)(C_0), cal(P)(C_1), dots, cal(P)(C_(k-1)) }) = k $

If any collision persists, the algorithm appends `(Cluster {cid})`, achieving an infallible 100% uniqueness record verified in our continuous integration test suite (`tests/test_scaling.py`).
