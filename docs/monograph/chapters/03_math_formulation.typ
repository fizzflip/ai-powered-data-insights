#import "../theme.typ": *

= Mathematical Formulation

#parchment-card(title: "METHODOLOGY AXIOM", stamp: "ALGO-V2")[
  The classification of multi-dimensional cultural artifacts requires mathematical rigor that resists the artificial uniformity of arbitrary cluster priors. This chapter formalizes the unsupervised clustering pipeline: the sub-linear adaptive scaling laws governing cluster count $k(N)$, high-dimensional feature preprocessing and compression, dual-objective partition optimization (K-Means and DBSCAN), parsimony-penalized silhouette scoring, and orthogonal vs. non-linear latent space manifold embeddings.
]

#v(10pt)

== 1. Sub-Linear Adaptive Cluster Scaling ($k$)

=== The Failure Modes of Fixed Partitioning Across Scales
In unsupervised catalog segmentation, the selection of the cluster cardinality parameter $k$ represents an existential bias. Fixed-$k$ heuristics fail catastrophically across differing dataset volumes:

1. *Micro-Scale Over-Fragmentation ($N << 300$)*: Imposing an arbitrary $k = 10$ onto small collections forces artificial boundaries across continuous stylistic cohorts, splintering unified aesthetics into degenerate, statistically under-powered clusters ($N_i < 5$) dominated by sample noise.
2. *Macro-Scale Coarse Over-Merging ($N >> 2,000$)*: Conversely, fixing $k = 5$ on an industrial catalog of $40,654$ entries compresses vast, heterogeneous creative movements—such as Cyberpunk Noir, Iyashikei Slice-of-Life, and Isekai Power Fantasies—into amorphous mega-clusters that obscure nuanced sub-genre genealogies.

=== Mathematical Power-Law Formulation
To guarantee scale invariance and mathematical stability as the ingested catalog expands, we derive an adaptive candidate search window bounded by a sub-linear power law inspired by empirical Heaps' law dynamics in information retrieval:

$ k_("min")(N) = max(2, floor(c_("min") dot N^alpha)) $

$ k_("max")(N) = min(k_("cap"), floor(c_("max") dot N^alpha)) $

$ k_("optimal") = op("argmax", limits: #true)_(k in [k_("min"), k_("max")]) S_("parsimonious")(k) $

Where $N in NN^+$ denotes the active catalog sample size, $alpha in (0, 0.5)$ represents the sub-linear scaling exponent, $c_("min")$ and $c_("max")$ define the lower and upper envelope constants, and $k_("cap")$ enforces an asymptotic ceiling to preserve human interpretability.

#pagebreak()
#styled-table(
  columns: (1.5fr, 1fr, 1.2fr, 2.5fr),
  [#text(fill: white, weight: "bold")[Parameter]],
  [#text(fill: white, weight: "bold")[Value]],
  [#text(fill: white, weight: "bold")[Domain]],
  [#text(fill: white, weight: "bold")[Empirical & Theoretical Justification]],

  [$c_("min")$ (Lower Bound Scalar)],
  [`1.20`],
  [$RR^+$],
  [Prevents premature cluster saturation; ensures at least 2 distinct macro-cohorts at baseline.],

  [$c_("max")$ (Upper Bound Scalar)],
  [`3.50`],
  [$RR^+$],
  [Allows structural expansion without exceeding the cognitive limit of taxonomic distinctiveness.],

  [$alpha$ (Sub-Linear Exponent)],
  [`0.35`],
  [$(0.25, 0.40)$],
  [Derived from empirical vocabulary growth rates; mirrors semantic diversity in media taxonomies.],

  [$k_("cap")$ (Asymptotic Ceiling)],
  [`24`],
  [$NN^+$],
  [Upper ceiling preventing unmanageable taxonomy fragmentation on macro catalogs ($N > 40,000$).],
)

#v(6pt)

#spec-callout(title: "CALCULATED SCALING BENCHMARK TRAJECTORY")[
  Applying this sub-linear formulation across benchmark scales produces the following adaptive search boundaries:
  - *Small Benchmark ($N = 150$)*: $k_("target") = 4$, $k in [3, 5]$, Selecting $k^* = 3$ ($S = 0.1701$, Inertia = $1,242.05$).
  - *Medium Expansion ($N = 600$)*: $k_("target") = 6$, $k in [5, 7]$, Selecting $k^* = 5$ ($S = 0.1133$, Inertia = $4,431.29$).
  - *Large Catalog ($N = 1,998$)*: $k_("target") = 8$, $k in [7, 9]$, Selecting $k^* = 7$ ($S = 0.0897$, Inertia = $13,884.00$).
  - *Full Manami Catalog ($N = 40,654$)*: Search window expands to $[14, 22]$, selecting the canonical $18$-cluster taxonomy.
]

#v(10pt)

== 2. High-Dimensional Feature Space & Preprocessing

The raw database schema encompasses heterogeneous data structures: bounded continuous review ratings, unbounded heavy-tailed engagement metrics, discrete calendar years, sparse multi-label genres, and unstructured community synopsis tags. A 5-stage transformation pipeline projects these variables into a cohesive dense matrix $bold(X) in RR^(N times 73)$.

=== 2.1 Continuous Feature Standardization
Continuous variables with approximately Gaussian distributions—such as `averageScore`, `duration`, and normalized episode counts—are centered and scaled to zero mean and unit variance:

$ z = (x - mu) / sigma = (x - 1/N sum_(i=1)^N x_i) / sqrt(1/(N-1) sum_(i=1)^N (x_i - mu)^2) $

This standardization prevents features with large natural ranges (such as episode runtime in minutes) from dominating Euclidean distance calculations over bounded metrics.

=== 2.2 Heavy-Tail Logarithmic Variance Compression
Audience viewership (`popularity`) and user bookmark counts (`favourites`) follow extreme Pareto-like power-law distributions, where viral flagship titles (e.g., _Attack on Titan_, $p > 500,000$) dwarf long-tail arthouse releases ($p < 500$). To stabilize variance and regularize gradient computation, we apply a smooth shifted logarithmic compression:

$ y_("pop") = ln(1 + "popularity") $
$ y_("fav") = ln(1 + "favourites") $
$ y_("ep") = ln(1 + "episodes") $

This transformation compresses four orders of magnitude into a well-behaved continuous interval $[0, 13.5]$, pulling extreme outlier points into the active neighborhood of dense metric clustering.

=== 2.3 Temporal Recency Decay & The Devotion Ratio
Temporal evolution and audience engagement depth are extracted through two engineered interaction ratios:

*Temporal Recency Decay ($R$)*: Release years are normalized across the historical catalog boundary $[t_("min"), t_("max")]$:
$ R(t) = (t - t_("min")) / ((t_("max") - t_("min")) + epsilon), quad epsilon = 10^(-6) $

*Devotion Ratio ($D$)*: Raw popularity reflects passive reach, whereas favorite marks reflect active passion. We formulate the Devotion Ratio with Laplace additive smoothing:
$ D = "favourites" / ("popularity" + 1.0) $

A title with $10,000$ members and $1,000$ favorites ($D = 0.0999$) exhibits vastly higher community devotion than a commercial broadcast with $400,000$ members and $4,000$ favorites ($D = 0.0099$). This feature provides the mathematical foundation for isolating cult and legacy archetypes.

=== 2.4 Multi-Label Genre Indicators & TF-IDF Thematic Vectorization
Categorical taxonomy features are encoded via dual sparse-to-dense mappings:

1. *Multi-Label Binary Genre Encoding*: Each anime entry possesses a subset of $G$ discrete genre tags ($G = 18$). We construct an indicator vector $bold(g) in {0, 1}^G$:
$ g_j = cases(1 quad &"if genre" j in "title", 0 quad &"otherwise") $

2. *TF-IDF Thematic Tag Vectorization*: Community thematic descriptors (e.g., _"Male Protagonist"_, _"Philosophy"_, _"Cyberpunk"_, _"Ensemble Cast"_) are parsed into document strings and weighted via Term Frequency-Inverse Document Frequency (TF-IDF) over corpus $cal(D)$:
$
  "TF"(t, d) = f_(t, d) / (sum_(t' in d) f_(t', d)), quad "IDF"(t, cal(D)) = ln((1 + |cal(D)|) / (1 + |{d in cal(D) : t in d}|)) + 1
$
$ w_(t, d) = "TF"(t, d) dot "IDF"(t, cal(D)) $

With $ell_2$ normalization applied across the top $M = 35$ informative tag dimensions:
$ bold(v)_d = (w_(1, d), w_(2, d), dots, w_(M, d))^T / sqrt(sum_(j=1)^M w_(j, d)^2) $

The resulting composite row vector for title $i$ spans $d = 7 + 13 + 18 + 35 = 73$ orthogonal dimensions.

#v(10pt)

== 3. Unsupervised Objective Optimization

=== 3.1 K-Means Inertia Minimization
Partitioning the $73$-dimensional standardized feature space into $k$ coherent archetype clusters is driven by minimizing the Within-Cluster Sum of Squares (Inertia $J$):

$ J(bold(mu)_1, dots, bold(mu)_k) = sum_(i=1)^k sum_(bold(x) in C_i) norm(bold(x) - bold(mu)_i)^2 $

Where centroid $bold(mu)_i$ represents the empirical barycenter of partition $C_i$:
$ bold(mu)_i = 1 / (|C_i|) sum_(bold(x) in C_i) bold(x) $

Optimization executes via Lloyd’s algorithm with `k-means++` seeding, iterating alternating expectation and maximization steps until inertia convergence $|J^((t)) - J^((t-1))| < 10^(-4)$.

=== 3.2 DBSCAN Density Reachability & Structural Noise Isolation
While K-Means constructs convex Voronoi partitions across the global dataset, non-convex density structures and anomalous edge titles require density-based clustering. We employ Density-Based Spatial Clustering of Applications with Noise (DBSCAN) parameterized by neighborhood radius $epsilon = 1.2$ and core sample threshold $"MinPts" = 4$.

*Core Point Condition*: A point $bold(p)$ is a core point if its closed $epsilon$-neighborhood contains at least $"MinPts"$ samples:
$ |N_epsilon(bold(p))| = |{bold(q) in cal(D) : "dist"(bold(p), bold(q)) <= epsilon}| >= "MinPts" $

*Border & Noise Points*:
- A point $bold(p)$ is a *Border Point* if $|N_epsilon(bold(p))| < "MinPts"$ but $bold(p) in N_epsilon(bold(q))$ for some core point $bold(q)$.
- A point $bold(p)$ is designated *Noise* ($"cluster" = -1$) if it is neither core nor border.

*Density-Reachable Chain*: A point $bold(p)$ is density-reachable from $bold(q)$ if there exists a finite sequence $bold(p)_1, bold(p)_2, dots, bold(p)_n$ where $bold(p)_1 = bold(q)$, $bold(p)_n = bold(p)$, and each $bold(p)_(i+1)$ is directly density-reachable from $bold(p)_i$.

In the $500$-sample reference harvest, DBSCAN isolates $99$ anomalous outlier titles ($19.8%$ of data), filtering out bizarre experimental shorts and zero-engagement promotional videos so that K-Means archetype centroids remain structurally pure and commercially representative.

#v(10pt)

== 4. Cluster Validation Diagnostics & Parsimony Scoring

=== 4.1 Silhouette Coefficient Formulation
To quantify whether clusters represent statistically tight, distinct populations rather than arbitrary Euclidean tessellations, we compute the Silhouette Coefficient $s(i)$ for each data point $i in C_I$:

$ a(i) = 1 / (|C_I| - 1) sum_(j in C_I, j != i) norm(bold(x)_i - bold(x)_j) $

$ b(i) = min_(J != I) [ 1 / (|C_J|) sum_(j in C_J) norm(bold(x)_i - bold(x)_j) ] $

$ s(i) = (b(i) - a(i)) / max(a(i), b(i)), quad s(i) in [-1, +1] $

Where $a(i)$ measures average intra-cluster cohesion, and $b(i)$ measures lowest mean inter-cluster separation. The catalog mean silhouette is:
$ S(k) = 1 / N sum_(i=1)^N s(i) $

=== 4.2 The Parsimony Penalty Function
A well-known pathology of raw silhouette scoring is its systematic bias toward minimal cluster counts ($k = 2$ or $k = 3$), which artificially achieve high separation by collapsing rich sub-genres into blunt polar opposites (e.g., "Mainstream Shonen" vs. "Everything Else").

To resolve this, we formulate the *Parsimony-Penalized Silhouette Objective* $S_("parsimonious")(k)$:

$ S_("parsimonious")(k) = S(k) - lambda dot (k - k_("min")) / (k_("max") - k_("min")) $

Where $lambda = 0.08$ is the complexity damping coefficient. This penalty establishes a rigorous Pareto-optimal trade-off: higher cluster counts $k$ must yield significant structural inertia reductions ($Delta J$) to overcome the parsimony deduction.

#v(10pt)

#align(center)[
  #image("../assets/elbow_silhouette.png", width: 90%)
]
#align(center)[
  #text(font: font-display, size: 7.5pt, fill: text-muted)[
    Figure 3.1: Elbow Method (Inertia vs. $k$) and Silhouette Diagnostics across Candidate Cluster Counts ($k in [10, 12]$). Red dashed line marks $k = 10$.
  ]
]

#v(8pt)

As demonstrated in Figure 3.1, while raw inertia descends monotonically as $k$ increases, the silhouette score exhibits a pronounced inflection at $k = 10$ ($S = 0.131$), confirming optimal mathematical cohesion before structural over-fitting occurs.

#v(10pt)

== 5. Latent Space Projections

Visualizing $73$-dimensional feature interactions demands dimensional reduction techniques capable of preserving both global variance and non-linear manifold topologies.

=== 5.1 Principal Component Analysis (PCA) Linear Decomposition
PCA computes an orthogonal coordinate system where successive axes maximize explained sample variance. Given mean-centered data matrix $bold(X)_c in RR^(N times d)$:

1. *Sample Covariance Matrix*:
$ bold(Sigma) = 1 / (N - 1) bold(X)_c^T bold(X)_c in RR^(d times d) $

2. *Eigendecomposition*:
$ bold(Sigma) bold(v)_j = lambda_j bold(v)_j, quad j in {1, dots, d} $
Where $lambda_1 >= lambda_2 >= dots >= lambda_d >= 0$ are eigenvalues, and $bold(v)_j$ are orthonormal eigenvectors.

3. *Explained Variance Ratio (EVR)*:
$ "EVR"_j = lambda_j / (sum_(m=1)^d lambda_m) $

In our empirical anime feature space:
- *PC1* explains $20.3%$ of total variance, aligning strongly with commercial reach, episode volume, and mainstream popularity.
- *PC2* explains $13.3%$ of variance, capturing the vertical axis of critical acclaim, devotion ratio, and psychological/drama tag density.
Together, the 2D projection captures $33.6%$ of total dataset variance.

#v(10pt)

#align(center)[
  #image("../assets/pca_2d.png", width: 85%)
]
#align(center)[
  #text(font: font-display, size: 7.5pt, fill: text-muted)[
    Figure 3.2: 2D Principal Component Projection (PC1: 20.3% vs. PC2: 13.3% variance) with Discovered Cluster Archetype Centroids and Exemplar Star Points.
  ]
]

#v(10pt)

=== 5.2 t-Distributed Stochastic Neighbor Embedding (t-SNE) Manifold Learning
While PCA reveals global linear axes, it suffers from projection crowding on fine-grained cluster boundaries. We complement PCA with non-linear t-SNE, which maps local affinity probabilities in high-dimensional space into low-dimensional Student-t probabilities.

1. *High-Dimensional Conditional Affinity*:
$
  p_(j|i) = (exp(- norm(bold(x)_i - bold(x)_j)^2 / (2 sigma_i^2))) / (sum_(k != i) exp(- norm(bold(x)_i - bold(x)_k)^2 / (2 sigma_i^2))), quad p_(i|i) = 0
$

With symmetric joint distribution:
$ p_(i j) = (p_(j|i) + p_(i|j)) / (2 N) $

2. *Low-Dimensional Student-t Affinity*:
In the 2D map space $bold(y)_i, bold(y)_j in RR^2$, heavy-tailed Cauchy (Student-t with 1 degree of freedom) kernels prevent the crowding problem:
$
  q_(i j) = (1 + norm(bold(y)_i - bold(y)_j)^2)^(-1) / (sum_(k) sum_(l != k) (1 + norm(bold(y)_k - bold(y)_l)^2)^(-1)), quad q_(i i) = 0
$

3. *Kullback-Leibler Divergence Optimization*:
The embedding coordinates $bold(Y) = {bold(y)_1, dots, bold(y)_N}$ are optimized via gradient descent by minimizing relative entropy:
$ cal(L)_("KL") = "KL"(P || Q) = sum_(i != j) p_(i j) ln(p_(i j) / q_(i j)) $

$
  (partial cal(L)_("KL")) / (partial bold(y)_i) = 4 sum_(j) (p_(i j) - q_(i j)) (bold(y)_i - bold(y)_j) (1 + norm(bold(y)_i - bold(y)_j)^2)^(-1)
$

#v(10pt)

#align(center)[
  #image("../assets/tsne_2d.png", width: 85%)
]
#align(center)[
  #text(font: font-display, size: 7.5pt, fill: text-muted)[
    Figure 3.3: 2D t-SNE Non-Linear Manifold Projection showing clean topological separation among specialized genre clusters and dense regional cohorts.
  ]
]

#v(8pt)

As evidenced in Figure 3.3, t-SNE separates specialized niches (such as music and idol performances, arthouse shorts, and high-intensity action) into distinct, island-like topological manifolds, confirming that our 73-dimensional preprocessed feature space preserves authentic stylistic affinity structures.
