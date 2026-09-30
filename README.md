# AI-Powered Anime Data Insights: Multi-Source Unsupervised Clustering & Empirical Archetype Discovery

An end-to-end Machine Learning and Data Science project that uses unsupervised clustering to categorize anime titles based on their structural, chronological, popularity, and thematic characteristics.

Powered by **AniList GraphQL**, **Kitsu REST API**, **SQLite Incremental Storage**, **Scikit-Learn**, **Pandas**, **Seaborn**, and **Matplotlib**.

---

## 📌 Project Overview

Traditional anime exploration relies heavily on simple genre filters (e.g., "Action", "Romance") or superficial popularity rankings. This project employs unsupervised machine learning to uncover organic behavioral groupings, mapping anime into empirical, data-driven archetypes without artificial 1-to-1 label constraints.

### 🌟 Key Enhancements in Iteration 3
1. **Dynamic Cluster Scaling ($k$) with Database Volume**:
   - The candidate search window $[k_{\min}(N), k_{\max}(N)]$ and optimal cluster count dynamically adapt to database size $N$ using a sub-linear power-law heuristic:
     $$k_{\text{target}}(N) = \text{clip}\left(\left\lfloor 1.15 \cdot N^{0.26} \right\rfloor, 3, 10\right), \quad k_{\min} = \max(2, k_{\text{target}} - 1), \quad k_{\max} = \min(N-1, 12, k_{\text{target}} + 1)$$
   - Prevents over-fragmenting small datasets and coarse over-merging on large catalogs.
2. **Multi-Step Incremental Database Ingestion & Verification Harness**:
   - Dedicated benchmark runner (`scripts/demonstrate_scaling.py` / `python main.py --run-scaling-steps`) that validates scaling across 3 incremental database states:
     - **Step 1 ($N_1 = 150$)**: Optimal $k = 3$ (Macro-archetypes)
     - **Step 2 ($N_2 = 600$)**: Database incrementally expanded by 450 titles $\to$ Optimal $k = 5$
     - **Step 3 ($N_3 = 1,998$)**: Database incrementally expanded to full catalog $\to$ Optimal $k = 7$
   - Verifies monotonic growth ($k_1 \le k_2 \le k_3$) with zero duplicate archetype label collisions.
3. **100% Collision-Free Archetype Disambiguation**:
   - Hierarchical naming and secondary trait discriminators guarantee unique persona labels regardless of $k$.
4. **Dual Storage Incremental Local Database**: Persistent storage in SQLite (`data/anime_catalog.db`, 1,998 titles) with automatic export synchronization to `data/raw_anime_data.json` for offline demonstration.
5. **Multi-Source Ingestion & Fallback**: AniList GraphQL API with Kitsu JSON:API fallback and rate-delay throttling.

---

## 🚀 Architecture & Pipeline Flow

```
   ┌─────────────────────────────────────────────────────────────┐
   │                  Multi-Source Ingestion                     │
   │  AniList GraphQL ──(fallback)──> Kitsu API ──> Polite Delay │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Dual-Storage Local Database Engine              │
   │  - SQLite Persistent Catalog: data/anime_catalog.db         │
   │  - Deduplication & Incremental Pagination Resumption        │
   │  - Auto-Export Sync: data/raw_anime_data.json (Portable)    │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │          Data Preprocessing & Feature Engineering           │
   │  - StandardScaler on Continuous Features (score, pop, etc.) │
   │  - Engineered 'Recency' & 'Favorites-to-Popularity' Ratio   │
   │  - Multi-label Binarization for Genres                      │
   │  - TF-IDF Vectorization for Anime Tags                      │
   │  - One-Hot Categorical Encoding for Source & Season         │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │         Unsupervised ML & Empirical Archetype Engine        │
   │  - Elbow Inertia & Silhouette Diagnostics (k in [2, 10])    │
   │  - K-Means Clustering                                       │
   │  - DBSCAN on PCA-reduced space (Density & Outlier Flagging) │
   │  - Dynamic Centroid Coordinate Archetype Profiler           │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │              Visualization & Findings Reporting             │
   │  - PCA 2D & 3D Projections with Exemplar Annotations        │
   │  - t-SNE 2D Manifold Embedding                              │
   │  - Diagnostic Elbow & Silhouette Curves                     │
   │  - Normalized Centroid Feature Heatmap                      │
   │  - Comprehensive Markdown Report: cluster_analysis_report.md│
   └─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
ai-powered-data-insights/
├── data/
│   ├── anime_catalog.db              # SQLite persistent incremental database
│   └── raw_anime_data.json           # Synchronized portable JSON cache
├── reports/
│   ├── figures/                      # High-resolution visual artifacts (300 DPI)
│   │   ├── elbow_silhouette.png      # Elbow & Silhouette diagnostic curves
│   │   ├── pca_2d.png                # 2D PCA projection with exemplar titles
│   │   ├── pca_3d.png                # 3D PCA projection
│   │   ├── tsne_2d.png               # 2D t-SNE non-linear projection
│   │   └── cluster_heatmap.png       # Normalized feature means heatmap
│   └── cluster_analysis_report.md    # Detailed empirical findings report
├── src/
│   ├── __init__.py
│   ├── database.py                   # SQLite storage, deduplication & sync engine
│   ├── data_fetcher.py               # MultiSourceFetcher (AniList + Kitsu + Mock)
│   ├── preprocessor.py               # Cleaning, imputation, scaling, TF-IDF
│   ├── clustering.py                 # KMeans, DBSCAN, elbow/silhouette, empirical archetypes
│   ├── visualizer.py                 # Matplotlib (headless) & Seaborn visualizers
│   └── pipeline.py                   # End-to-end orchestration controller
├── tests/
│   ├── test_database.py              # SQLite database & export/import unit tests
│   ├── test_data_fetcher.py          # Data fetcher & cache unit tests
│   ├── test_preprocessor.py          # Preprocessor & transformation unit tests
│   ├── test_clustering.py            # Clustering algorithms & archetype tests
│   ├── test_visualizer.py            # Visualization & figure generation tests
│   └── test_pipeline.py              # End-to-end integration tests
├── main.py                           # CLI entrypoint
├── pyproject.toml                    # Project configuration & dependencies
├── requirements.txt                  # Pinned dependencies lockfile
└── README.md
```

---

## 🛠️ Installation & Setup

Ensure Python `>= 3.12` is installed.

### Using `uv` (Recommended)
```bash
# Clone the repository and enter directory
cd /home/mrbot/.temp/ai-powered-data-insights

# Install all dependencies into virtual environment
uv sync
```

### Using standard `pip`
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 💻 Usage & CLI Options

### Run Default Pipeline (Auto source, 500 records)
```bash
python main.py
```

### Fetch Incrementally from Kitsu REST API
```bash
python main.py --source kitsu --samples 100
```

### Run Completely Offline (Using Local SQLite Database)
```bash
python main.py --offline
```

### Slow / Polite Crawling (Avoiding API Bans)
```bash
python main.py --samples 1000 --rate-delay 1.2
```

### Force Fresh Fetch from APIs (Bypassing Local Cache)
```bash
python main.py --force-fetch --samples 500
```

### Run Multi-Step Incremental Database Scaling Benchmark
```bash
python main.py --run-scaling-steps
```

### Run Adaptive Clustering (Auto-scaling k with dataset size)
```bash
python main.py --offline --adaptive-k
```

### Available CLI Options
| Flag | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `--samples` | `int` | `500` | Target number of anime records to retrieve/analyze |
| `--k` | `int` | `5` | Force specific number of K-Means clusters (set to `0` for auto-k) |
| `--adaptive-k` | `flag` | `False` | Dynamically scale candidate $[k_{\min}, k_{\max}]$ and optimal $k$ based on sample size $N$ |
| `--run-scaling-steps` | `flag` | `False` | Execute 3-step incremental DB scaling benchmark and generate progression report |
| `--step-samples` | `str` | `150,600,1998` | Comma-separated sample slices for incremental benchmark |
| `--source` | `str` | `auto` | Data source: `auto` (AniList -> Kitsu fallback), `anilist`, or `kitsu` |
| `--rate-delay` | `float` | `0.6` | Polite inter-request delay (seconds) to prevent API bans |
| `--db-path` | `path` | `data/anime_catalog.db` | Path to SQLite incremental database |
| `--min-k` | `int` | `2` | Minimum $k$ for Elbow and Silhouette evaluation |
| `--max-k` | `int` | `10` | Maximum $k$ for Elbow and Silhouette evaluation |
| `--dbscan-eps` | `float` | `1.2` | DBSCAN neighborhood radius ($\epsilon$) |
| `--dbscan-min-samples` | `int` | `4` | DBSCAN minimum core samples |
| `--force-fetch` | `flag` | `False` | Ignore local cache and fetch fresh data from APIs |
| `--offline` | `flag` | `False` | Run purely offline from SQLite database or mock |
| `--no-incremental` | `flag` | `False` | Do not resume pagination (restart from page 1) |
| `--output-dir` | `path` | `reports` | Target directory for report and figures |
| `--no-plots` | `flag` | `False` | Skip figure generation (fast text-only mode) |

---

## 📊 Summary of Discovered Empirical Archetypes

By avoiding rigid 1-to-1 Hungarian mapping, clusters are described by their true centroid coordinates:

| Cluster | Discovered Empirical Archetype | Catalog Share | Median Year | Mean Score | Mean Popularity | Favorites Ratio | Defining Traits & Exemplars |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | **Low-Profile (Commercial Mid-Tier & Long-Tail)** | 32.0% | 2018 | 67.7 | 91,905 | 0.014 | Long-tail sequels & adaptations (*The Promised Neverland S2*, *Shield Hero S2*). |
| **1** | **Modern Hits (Contemporary Comedy)** | 31.3% | 2018 | 76.5 | 160,458 | 0.023 | Modern character comedy & action ensembles (*My Hero Academia S2*, *One Punch Man*). |
| **2** | **Modern Hits (Blockbuster Drama)** | 20.7% | 2019 | 81.1 | 349,494 | 0.041 | Massive mainstream blockbusters (*Demon Slayer*, *JUJUTSU KAISEN*, *Tokyo Ghoul*). |
| **3** | **Specialized Archetype (Drama Focus)** | 10.8% | 2016 | 79.5 | 158,348 | 0.029 | Theatrical emotional masterpieces (*A Silent Voice*, *Your Name.*, *Mugen Train*). |
| **4** | **Classics (Legacy Masterworks - High Devotion)** | 5.2% | 2004 | 82.6 | 343,116 | 0.061 | High-devotion foundational masterworks (*Attack on Titan*, *Death Note*, *Hunter x Hunter*). |

---

## 🧪 Automated Testing

Run the full pytest suite:
```bash
uv run pytest -v
```

18 automated tests across 7 modules validate:
- **`test_scaling.py`**: Monotonic $k$ scaling bounds, variable-$k$ profiling safety, 100% archetype uniqueness, and 3-step incremental SQLite growth.
- **`test_database.py`**: SQLite initialization, upsert deduplication, and bidirectional JSON export/import.
- **`test_data_fetcher.py`**: Multi-source querying, rate-limit backoff, offline mock fallback.
- **`test_preprocessor.py`**: Imputation, StandardScaler, `Recency` calculation, and non-empty TF-IDF matrices.
- **`test_clustering.py`**: K-Means clustering, DBSCAN on PCA space, and empirical archetype labeling.
- **`test_visualizer.py`**: Headless rendering of PCA 2D/3D, t-SNE, Elbow/Silhouette curves, and heatmaps.
- **`test_pipeline.py`**: End-to-end multi-source pipeline execution and artifact generation.
