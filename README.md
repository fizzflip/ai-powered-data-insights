# AI-Powered Anime Data Insights: Multi-Source Unsupervised Clustering & Empirical Archetype Discovery

An end-to-end Machine Learning and Data Science project that uses unsupervised clustering to categorize anime titles based on their structural, chronological, popularity, and thematic characteristics.

Powered by **AniList GraphQL**, **Kitsu REST API**, **SQLite Incremental Storage**, **Scikit-Learn**, **Pandas**, **Seaborn**, and **Matplotlib**.

---

## 📌 Project Overview

Traditional anime exploration relies heavily on simple genre filters (e.g., "Action", "Romance") or superficial popularity rankings. This project employs unsupervised machine learning to uncover organic behavioral groupings, mapping anime into empirical, data-driven archetypes without artificial 1-to-1 label constraints.

### 🌟 Key Enhancements in Iteration 2
1. **Dual Storage Incremental Local Database**: Persistent storage in SQLite (`data/anime_catalog.db`) with automatic export synchronization to `data/raw_anime_data.json` for seamless offline demonstration.
2. **Multi-Source Ingestion & Fallback**:
   - **Primary**: AniList GraphQL API (rich tags, studios, score, popularity).
   - **Secondary Fallback**: Kitsu JSON:API (`https://kitsu.io/api/edge/anime`), normalized to canonical schema.
   - **Offline Fallback**: SQLite database + 55-item curated mock dataset.
3. **API Ban Prevention & Polite Rate-Limiting**: Configurable inter-request throttling (`--rate-delay 0.6`) and incremental pagination tracking to gradually build up a large offline catalog without risking rate limits or bans.
4. **Strict Empirical Archetype Engine**: Dropped rigid 1-to-1 Hungarian matching. Archetypes are now derived dynamically from true centroid coordinates across Recency, Acclaim, Reach, Cult Loyalty, and Thematic Focus.

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

### Available CLI Options
| Flag | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `--samples` | `int` | `500` | Target number of anime records to retrieve/analyze |
| `--k` | `int` | `5` | Force specific number of K-Means clusters (set to `0` for auto-k) |
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
| **0** | **Classics (Historical Favorites)** | 14.8% | 2008 | 79.4 | 225,000 | 0.048 | Influential foundational series (*Cowboy Bebop*, *Trigun*, *Princess Mononoke*). |
| **1** | **Modern Hits (Contemporary Drama)** | 22.4% | 2020 | 81.2 | 310,000 | 0.038 | Modern character drama, comedy ensembles (*Dr. STONE*, *SPY x FAMILY*, *Oshi no Ko*). |
| **2** | **Specialized Archetype (Drama Focus)** | 10.6% | 2016 | 82.5 | 260,000 | 0.041 | Acclaimed theatrical films and emotional narrative arcs (*A Silent Voice*, *Your Name.*). |
| **3** | **Low-Profile (Commercial Mid-Tier & Long-Tail)** | 31.2% | 2017 | 69.5 | 195,000 | 0.017 | Commercial adaptations and sequels (*Tokyo Ghoul √A*, *High School DxD*). |
| **4** | **Modern Hits (Blockbuster Drama & Action)** | 21.0% | 2019 | 83.1 | 510,000 | 0.045 | Massive mainstream shounen and dark fantasy (*Demon Slayer*, *Jujutsu Kaisen*). |

---

## 🧪 Automated Testing

Run the full pytest suite:
```bash
uv run pytest -v
```

13 automated tests across 6 modules validate:
- **`test_database.py`**: SQLite initialization, upsert deduplication, and bidirectional JSON export/import.
- **`test_data_fetcher.py`**: Multi-source querying, rate-limit backoff, offline mock fallback.
- **`test_preprocessor.py`**: Imputation, StandardScaler, `Recency` calculation, and non-empty TF-IDF matrices.
- **`test_clustering.py`**: K-Means clustering, DBSCAN on PCA space, and empirical archetype labeling.
- **`test_visualizer.py`**: Headless rendering of PCA 2D/3D, t-SNE, Elbow/Silhouette curves, and heatmaps.
- **`test_pipeline.py`**: End-to-end multi-source pipeline execution and artifact generation.
