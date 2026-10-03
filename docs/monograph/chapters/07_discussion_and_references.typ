// ============================================================================
// CHAPTER 07: DISCUSSION, THREATS TO VALIDITY & SCHOLARLY REFERENCES
// AI-Powered Anime Data Insights: Empirical Clustering & Latent Projections
// ============================================================================

#import "../theme.typ": *

= Discussions and Limitations

== Threats to Validity & Limitations

While the empirical pipeline successfully ingested 40,654 records and surfaced 18 distinct latent archetypes, several methodological threats to validity must be formally acknowledged in an academic evaluation.

=== 1. Construct Validity & Metadata Noise
The foundational data sources (AniList, Kitsu, Manami) rely partially on crowdsourced community contributions. Consequently:
- *Tagging Drift & Semantic Ambiguity*: Thematic tags such as _"Philosophy"_, _"Tragedy"_, or _"Cyberpunk"_ are applied with varying subjective criteria across platform user bases. While TF-IDF vectorization with $ell_2$ normalization suppresses sporadic outlier keywords, subtle platform-specific tagging drift cannot be completely eliminated.
- *Synchronic Scarcity in Pre-Digital Media*: Media produced prior to the 1980s cel-animation era frequently suffer from sparse synopsis fields and missing broadcast metadata, leading to lower dimensionality in their semantic representation vectors.

=== 2. Internal Validity & Hyperparameter Sensitivity
- *Sub-Linear Exponent Selection ($alpha = 0.35$)*: The power-law envelope $k(N) = floor(c dot N^alpha)$ was derived from empirical Heaps' law observations on media taxonomies. While $alpha = 0.35$ demonstrated optimal inertia stabilization across benchmark increments ($N in [150, 600, 1998, 40654]$), higher values of $alpha$ ($alpha > 0.45$) would accelerate cluster splintering, whereas lower values ($alpha < 0.25$) risk prematurely merging distinct sub-genres into monolithic clusters.
- *Parsimony Damping Parameter ($lambda = 0.08$)*: The complexity penalty prevents raw silhouette scoring from degenerating into trivial binary partitions ($k = 2$). The selected coefficient $lambda = 0.08$ represents a calibrated trade-off between statistical silhouette separation and granular genre interpretability.

=== 3. External Validity & Platform Tracking Bias
- *Western Demographic Skew*: The underlying platforms cater predominantly to English-speaking international audiences. As established in Chapter 5, Chinese Donghua and Korean Aeni exhibit severe Western tracking deflation (-87.7% in recorded member volume) despite comparable baseline scores (64.04 vs 64.12). Replicating this study using native Chinese platforms (Bilibili, Tencent Video) or Korean platforms (Naver Series) would yield denser engagement metrics for overseas productions.

#v(8pt)

== Ethical Considerations & Algorithmic Stewardship

Automated recommender systems and unsupervised clustering algorithms play a profound role in shaping cultural discovery:
+ *Mitigating Popularity Amplification Loops*: Standard collaborative filtering algorithms systematically over-amplify commercial blockbuster franchises (Cluster 0) while suppressing boutique arthouse works (Cluster 6) and international productions (Cluster 17). By projecting media onto continuous latent manifold coordinates independent of raw viewership volume, our pipeline enables equitable pedagogical discovery based on intrinsic aesthetic affinity.
+ *Cultural Autonomy in Taxonomy*: Prior commercial databases frequently labeled Chinese Donghua and Korean Aeni as mere "Japanese anime sub-types". Our 5-level deterministic cascade establishes cultural and geographic autonomy, honoring distinct national production pipelines (such as Donghua's Xianxia/Wuxia traditions and Aeni's webtoon serialization models).

#v(8pt)

== Reproducibility & Open Science Invariants

To guarantee rigorous empirical reproducibility in accordance with open science benchmarks:
- *Deterministic Pseudo-Random Initialization*: All stochastic dimensionality reduction operations (UMAP, t-SNE) and cluster initializations (`k-means++`) are strictly pinned to `SEED = 42`.
- *Hermetic Containerization*: Complete dependency trees are locked via modern lockfiles (`uv.lock`) and container specifications (`Containerfile` / Docker).
- *Automated Test Verification*: The repository includes comprehensive automated test suites (`tests/test_scaling.py`, `tests/test_clustering.py`, `tests/test_origin_cascade.py`) verifying invariant cluster label uniqueness and zero deduplication collisions across the entire 40,654-title warehouse.

#v(10pt)

== Scholarly References

#set text(size: 8.5pt)
#set par(leading: 0.65em)

+ *Lloyd, S. P.* (1982). "Least squares quantization in PCM." _IEEE Transactions on Information Theory_, 28(2), 129–137.
+ *Ester, M., Kriegel, H.-P., Sander, J., & Xu, X.* (1996). "A density-based algorithm for discovering clusters in large spatial databases with noise." In _Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining (KDD-96)_, pp. 226–231.
+ *Rousseeuw, P. J.* (1987). "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis." _Journal of Computational and Applied Mathematics_, 20, 53–65.
+ *van der Maaten, L., & Hinton, G.* (2008). "Visualizing data using t-SNE." _Journal of Machine Learning Research_, 9(Nov), 2579–2605.
+ *Salton, G., & Buckley, C.* (1988). "Term-weighting approaches in automatic text retrieval." _Information Processing & Management_, 24(5), 513–523.
+ *Heaps, H. S.* (1978). _Information Retrieval: Computational and Theoretical Aspects_. Academic Press, New York.
+ *Jaro, M. A.* (1989). "Advances in record-linkage methodology as applied to matching the 1985 census of Tampa, Florida." _Journal of the American Statistical Association_, 84(406), 414–420.
+ *Winkler, W. E.* (1990). "String Comparator Metrics and Enhanced Decision Rules in the Fellegi-Sunter Model of Record Linkage." In _Proceedings of the Section on Survey Research Methods_, American Statistical Association, pp. 354–359.
+ *Napier, S. J.* (2005). _Anime from Akira to Howl's Moving Castle: Experiencing Contemporary Japanese Animation_. Palgrave Macmillan, New York.
+ *Clements, J., & McCarthy, H.* (2015). _The Anime Encyclopedia: A Century of Japanese Animation_ (3rd Edition). Stone Bridge Press, Berkeley.
+ *Lamarre, T.* (2009). _The Anime Machine: A Media Theory of Animation_. University of Minnesota Press, Minneapolis.
+ *Abadi, M., et al.* (2016). "TensorFlow: A system for large-scale machine learning." In _12th USENIX Symposium on Operating Systems Design and Implementation (OSDI '16)_, pp. 265–283.
+ *Pedregosa, F., et al.* (2011). "Scikit-learn: Machine learning in Python." _Journal of Machine Learning Research_, 12, 2825–2830.
