// ============================================================================
// ACADEMIC RESEARCH MONOGRAPH
// AI-Powered Anime Data Insights: Multi-Source Unsupervised Clustering,
// Latent Space Projections & Empirical Archetype Discovery
// Accession: № 14777 // Academic Research Edition
// ============================================================================

#import "theme.typ": *

#show: monograph-template.with(
  title: "AI-Powered Anime Data Insights",
  subtitle: "Multi-Source Unsupervised Clustering, Latent Space Projections & Empirical Archetype Discovery",
  accession: "№ 14777",
  edition: "ACADEMIC RESEARCH EDITION // 2026.10",
  authors: ("DeepMind Cognitive Systems", "AI Insights Autonomous Engineering Team"),
)

// ----------------------------------------------------------------------------
// 1. FRONT COVER
// ----------------------------------------------------------------------------
#cover-page(
  title: "AI-POWERED ANIME DATA INSIGHTS",
  subtitle: "Multi-Source Unsupervised Clustering and Empirical Archetype Discovery",
  kanji-title: "RESEARCH MONOGRAPH",
  accession: "ACCESSION № 14777",
  authors: ("Sandeep Prasad", "240905050085"),
  date: "OCTOBER 2026",
  // abstract: [
  //   // This academic research monograph presents an end-to-end unsupervised machine learning architecture that discovers empirical, data-driven archetypes across animated media using high-dimensional manifold projections, topological density estimation, and sub-linear adaptive clustering. Departing from commercial, publisher-assigned genre categories, the system unifies continuous metadata, Laplace-smoothed devotion metrics, TF-IDF thematic vectors, and a 5-level deterministic origin cascade across 40,654 consolidated titles. The methodology exposes 18 distinct latent archetypes with 100% collision-free taxonomic discrimination, uncovers structural format and genre divergence between Japanese domestic and international productions (Chinese Donghua and Korean Aeni), and benchmarks an ultra-compact 1.14 MB serverless WebAssembly edge deployment on Netlify Edge.
  // ]
)

#pagebreak()

// ----------------------------------------------------------------------------
// 2. PREFATORY NOTE & TABLE OF CONTENTS
// ----------------------------------------------------------------------------

#v(10pt)
#grid(
  columns: (1fr, auto),
  align: (left + horizon, right + horizon),
  text(font: font-display, size: 16pt, weight: "bold", fill: abyss, tracking: 0.05em)[TABLE OF CONTENTS],
  text(font: font-display, size: 8pt, fill: wisteria, tracking: 0.12em)[ACADEMIC COMPENDIUM INDEX • 18 CLUSTERS],
)
#v(4pt)
#line(length: 100%, stroke: 1.5pt + wisteria)
#v(16pt)

#outline(
  title: none,
  indent: 1.5em,
  depth: 2,
)

#v(1.5cm)

#parchment-card(title: "RESEARCH STATEMENT & METHODOLOGICAL RIGOR", stamp: "CANONICAL")[
  *Academic & Empirical Integrity*: This monograph is engineered as a definitive reference report for unsupervised machine learning in computational media studies. All mathematical formulas, algorithmic loss functions, and statistical telemetry are typeset in `Space Mono` with fixed-width tabular numerals. Qualitative observations and domain taxonomy are corroborated by quantitative centroid coordinates. All latent space projections (PCA, t-SNE), feature heatmaps, and system architecture diagrams are preserved with native vector fidelity.
]

#pagebreak()

// ----------------------------------------------------------------------------
// 3. RESEARCH SECTIONS
// ----------------------------------------------------------------------------

#include "chapters/00_executive_summary.typ"

#pagebreak()

#include "chapters/02_system_architecture.typ"

#pagebreak()

#include "chapters/03_math_formulation.typ"

#pagebreak()

#include "chapters/04_cluster_archetypes.typ"

#pagebreak()

#include "chapters/05_origin_divergence.typ"

#pagebreak()

// #include "chapters/06_benchmarks_and_edge.typ"

// #pagebreak()

#include "chapters/07_discussion_and_references.typ"

// #pagebreak()

// ----------------------------------------------------------------------------
// 4. COLOPHON & VERIFICATION SIGN-OFF
// ----------------------------------------------------------------------------
//
// = Colophon & Academic Verification Sign-Off
//
// #v(1cm)
//
// #spec-callout(title: "SYSTEM VERIFICATION & REPRODUCIBILITY CERTIFICATE")[
//   - *Document Composition*: Typst 0.15.1 Native Vector Typography Engine
//   - *Typographic Hierarchy*: Space Mono (Display & Formulas) \/\/ Inter (Latin Body) \/\/ Zen Kaku Gothic New (CJK Glyphs)
//   - *Color Palette Architecture*: Minimalist Academic Palette (Wisteria Violet `#6E58A3`, Midnight Abyss `#140C37`, Lilac Quartz `#D5B9F3`, Star Gold `#FCE277`, Nebula Cyan `#4DF0D2`)
//   - *Scientific Figures*: High-resolution vector diagrams and statistical plots (`elbow_silhouette.png`, `pca_2d.png`, `tsne_2d.png`, `cluster_heatmap.png`, `origin_distribution.png`, `format_comparison.png`, `genre_divergence.png`, `score_popularity_comparison.png`, `system_pipeline.svg`, `origin_cascade.svg`, `database_scaling.svg`, `wasm_architecture.svg`)
//   - *Ingestion Scale*: 40,654 unique de-duplicated titles across AniList GraphQL, Kitsu JSON:API, and Manami Offline Database
//   - *Algorithmic Resolution*: 18 canonical empirical clusters discovered via Parsimonious Silhouette optimization ($k=18$) with zero label collision rate
//   - *Origin Provenance*: 5-level deterministic origin cascade resolving 24,122 cohort-tagged titles across JP, Donghua, Aeni, and Western animation
//   - *Client-Side Edge Payload*: 1.14 MB compressed gzip columnar payload executing on Netlify Edge via Pyodide WebAssembly
//   - *Deterministic Random Seed*: `SEED = 42` for all pseudo-random initializations
//   - *Verification Status*: 100% Academic Acceptance & Reproducibility Invariants Verified
// ]
//
// #v(1.5cm)
//
// #align(center)[
//   #box(
//     fill: card-bg,
//     inset: (x: 20pt, y: 12pt),
//     radius: 4pt,
//     stroke: 1pt + stroke-light,
//     [
//       #text(font: font-jp, size: 10pt, fill: sumi-ink)[
//         星間幾何学と機械学習による次元分類体系\
//         *Empirical Archetype Discovery & High-Dimensional Latent Projections*
//       ]\
//       #v(4pt)
//       #text(font: font-display, size: 7.5pt, fill: text-muted, tracking: 0.15em)[
//         ● ACCESSION № 14777 ● OCTOBER 2026 ● END OF MONOGRAPH ●
//       ]
//     ]
//   )
// ]
