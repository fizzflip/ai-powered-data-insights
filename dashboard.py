import marimo

__generated_with = "0.25.0"
app = marimo.App(width="full", app_title="AI Anime Archetype Intelligence Hub")


@app.cell
def setup_and_imports():
    import os
    import sys
    from pathlib import Path
    import marimo as mo
    import numpy as np
    import pandas as pd
    import matplotlib

    # Force headless backend before any visualizer or pyplot import
    matplotlib.use("Agg")
    os.environ["MPLBACKEND"] = "Agg"

    # Ensure repository root is on sys.path regardless of launch directory
    _current = Path(__file__).resolve()
    repo_root = _current.parent.parent if _current.parent.name == "notebooks" else _current.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from src.database import AnimeCatalogDB
    from src.preprocessor import DataPreprocessor
    from src.clustering import AnimeClusterer
    from src.visualizer import ClusterVisualizer
    from src.comparative_visualizer import ComparativeVisualizer
    from src.pipeline import PipelineConfig, InsightsPipeline, run_comparative_pipeline

    def render_fig(fig):
        _html = mo.as_html(fig)
        matplotlib.pyplot.close(fig)
        return _html

    return (
        AnimeCatalogDB,
        AnimeClusterer,
        ClusterVisualizer,
        ComparativeVisualizer,
        DataPreprocessor,
        InsightsPipeline,
        PipelineConfig,
        mo,
        np,
        os,
        pd,
        render_fig,
        repo_root,
        run_comparative_pipeline,
    )


@app.cell
def catalog_database_connection(AnimeCatalogDB, pd, repo_root):
    _db_path = str(repo_root / "data" / "anime_catalog.db")
    db = AnimeCatalogDB(db_path=_db_path)
    total_catalog_count = db.count_records()

    jp_count = db.count_records(origin="jp")
    non_jp_count = db.count_records(origin="non-jp")

    df_catalog_summary = pd.DataFrame([
        {"Metric": "Total Catalog Records", "Value": f"{total_catalog_count:,}"},
        {"Metric": "Japanese Domestic (JP)", "Value": f"{jp_count:,}"},
        {"Metric": "Overseas / Non-JP (Donghua/Aeni)", "Value": f"{non_jp_count:,}"},
    ])
    return db, df_catalog_summary, jp_count, non_jp_count, total_catalog_count


@app.cell
def hyperparameter_form_ui(mo, total_catalog_count):
    _max_samples = max(100, min(5000, total_catalog_count)) if total_catalog_count > 0 else 500
    _default_samples = min(600, _max_samples)

    controls_form = (
        mo.md(
            """
            ### ⚙️ Pipeline Configuration & Model Hyperparameters
            {cohort}
            {samples}
            {k}
            {adaptive_k}
            {dbscan_eps}
            {dbscan_min_samples}
            """
        )
        .batch(
            cohort=mo.ui.dropdown(
                options={
                    "All Productions (Global)": "all",
                    "Japanese Domestic (JP)": "jp",
                    "Overseas (Non-JP: Donghua/Aeni)": "non-jp",
                    "Comparative Cross-Market (JP vs Non-JP)": "compare",
                },
                value="All Productions (Global)",
                label="Origin Cohort",
            ),
            samples=mo.ui.slider(
                start=100,
                stop=_max_samples,
                step=50,
                value=_default_samples,
                label="Catalog Sample Limit",
            ),
            k=mo.ui.slider(
                start=2,
                stop=12,
                step=1,
                value=5,
                label="Target Clusters (k)",
            ),
            adaptive_k=mo.ui.checkbox(
                value=False,
                label="Enable Adaptive Cluster Scaling (Power-Law k(N))",
            ),
            dbscan_eps=mo.ui.slider(
                start=0.5,
                stop=3.0,
                step=0.1,
                value=1.2,
                label="DBSCAN Neighborhood (eps)",
            ),
            dbscan_min_samples=mo.ui.slider(
                start=2,
                stop=10,
                step=1,
                value=4,
                label="DBSCAN Min Samples",
            ),
        )
        .form(submit_button_label="🚀 Run / Re-Cluster Pipeline", bordered=True)
    )
    return controls_form,


@app.cell
def execution_guard(controls_form, jp_count, mo, non_jp_count, total_catalog_count):
    mo.stop(
        total_catalog_count == 0,
        mo.callout("⚠️ SQLite database is empty. Please ingest anime records or offline database first.", kind="warn"),
    )

    if controls_form.value is not None:
        _cfg = controls_form.value
        _cohort = _cfg["cohort"]
        _samples = int(_cfg["samples"])
        _k = int(_cfg["k"])

        if _cohort in ("non-jp", "compare") and non_jp_count < 2:
            mo.stop(
                True,
                mo.callout(
                    f"⚠️ Selected cohort '{_cohort}' has insufficient records in database ({non_jp_count} available). Please ingest offline data or choose 'all' / 'jp'.",
                    kind="warn",
                ),
            )

        # Ensure sample count is at least k to avoid KMeans n_samples < k
        _samples = max(_samples, _k)

        active_params = {
            "cohort": _cohort,
            "samples": _samples,
            "k": _k,
            "adaptive_k": bool(_cfg["adaptive_k"]),
            "dbscan_eps": float(_cfg["dbscan_eps"]),
            "dbscan_min_samples": int(_cfg["dbscan_min_samples"]),
        }
    else:
        active_params = {
            "cohort": "all",
            "samples": min(500, max(50, total_catalog_count)),
            "k": 5,
            "adaptive_k": False,
            "dbscan_eps": 1.2,
            "dbscan_min_samples": 4,
        }

    return active_params,


@app.cell
def execute_clustering_pipeline(InsightsPipeline, PipelineConfig, active_params, repo_root):
    _p_config = PipelineConfig(
        num_samples=active_params["samples"],
        k=None if active_params["adaptive_k"] else active_params["k"],
        adaptive_k=active_params["adaptive_k"],
        dbscan_eps=active_params["dbscan_eps"],
        dbscan_min_samples=active_params["dbscan_min_samples"],
        origin=active_params["cohort"],
        db_path=str(repo_root / "data" / "anime_catalog.db"),
        output_dir=str(repo_root / "reports"),
        offline_mode=True,
        generate_plots=False,
    )

    _pipeline = InsightsPipeline(_p_config)
    pipeline_results = _pipeline.run()

    if pipeline_results.get("origin") == "compare":
        df_clustered = pipeline_results["df_all"].copy()
    else:
        df_clustered = pipeline_results["df"].copy()
        if "clustering" in pipeline_results and "cluster_id" not in df_clustered.columns:
            df_clustered["cluster_id"] = pipeline_results["clustering"].kmeans_labels
            df_clustered["archetype"] = df_clustered["cluster_id"].map(
                pipeline_results["clustering"].archetype_labels
            )

    return df_clustered, pipeline_results


@app.cell
def render_kpi_metrics(mo, pipeline_results, total_catalog_count):
    if pipeline_results.get("origin") == "compare":
        kpi_strip = mo.hstack([
            mo.stat(
                value=f"{pipeline_results['num_samples']:,}",
                label="Total Analyzed",
                caption=f"Out of {total_catalog_count:,} stored",
                bordered=True,
            ),
            mo.stat(
                value=f"{pipeline_results['k_optimal']['jp']}",
                label="JP Optimal Archetypes",
                caption="Japanese Domestic",
                bordered=True,
            ),
            mo.stat(
                value=f"{pipeline_results['k_optimal']['non_jp']}",
                label="Non-JP Optimal Archetypes",
                caption="Donghua & Aeni",
                bordered=True,
            ),
            mo.stat(
                value=f"{pipeline_results['num_jp']} : {pipeline_results['num_non_jp']}",
                label="JP / Non-JP Cohort Split",
                caption="Balance ratio",
                bordered=True,
            ),
        ], justify="start", gap=1.0)
    else:
        _sil = 0.0
        if "clustering" in pipeline_results and pipeline_results["clustering"].silhouette_scores:
            _k_opt = pipeline_results["k_optimal"]
            _sil = pipeline_results["clustering"].silhouette_scores.get(_k_opt, 0.0)

        kpi_strip = mo.hstack([
            mo.stat(
                value=f"{pipeline_results['num_samples']:,}",
                label="Analyzed Titles",
                caption=f"Out of {total_catalog_count:,} catalog",
                bordered=True,
            ),
            mo.stat(
                value=f"{pipeline_results['k_optimal']}",
                label="Discovered Archetypes (k)",
                caption="Silhouette peak",
                bordered=True,
            ),
            mo.stat(
                value=f"{_sil:.3f}",
                label="Silhouette Cohesion",
                caption="Cluster separation quality",
                bordered=True,
            ),
            mo.stat(
                value=f"{pipeline_results.get('dbscan_noise', 0)} ({pipeline_results.get('dbscan_noise', 0) / max(1, pipeline_results['num_samples']) * 100:.1f}%)",
                label="DBSCAN Outlier Noise",
                caption=f"{pipeline_results.get('dbscan_clusters', 0)} dense cores",
                bordered=True,
            ),
        ], justify="start", gap=1.0)

    return kpi_strip,


@app.cell
def render_tab_archetypes(ClusterVisualizer, mo, pipeline_results):
    if pipeline_results.get("origin") == "compare":
        _jp_profiles = pipeline_results.get("cluster_profiles", {}).get("jp", None)
        _njp_profiles = pipeline_results.get("cluster_profiles", {}).get("non_jp", None)
        _viz = ClusterVisualizer()
        _jp_table = _viz.format_summary_table(_jp_profiles) if _jp_profiles is not None and not _jp_profiles.empty else "No profiles."
        _njp_table = _viz.format_summary_table(_njp_profiles) if _njp_profiles is not None and not _njp_profiles.empty else "No profiles."

        tab_archetypes = mo.vstack([
            mo.callout(
                "Comparative cross-market mode active: Japanese and Overseas cohorts are partitioned to prevent representation bias.",
                kind="info",
                title="Dual-Cohort Archetype Contrast",
            ),
            mo.md(f"### 🇯🇵 Japanese Domestic Discovered Archetypes\n{_jp_table}"),
            mo.md(f"### 🌏 Overseas (Non-JP: Donghua / Aeni) Discovered Archetypes\n{_njp_table}"),
        ])
    else:
        _clustering = pipeline_results["clustering"]
        _viz = ClusterVisualizer()
        _summary_table = _viz.format_summary_table(_clustering.cluster_profiles)

        tab_archetypes = mo.vstack([
            mo.callout(
                f"Successfully partitioned {pipeline_results['num_samples']} titles into {pipeline_results['k_optimal']} distinct empirical archetypes.",
                kind="success",
                title="Empirical Archetype Resolution Complete",
            ),
            mo.md(f"### Discovered Archetype Profile Breakdown\n{_summary_table}"),
        ])

    return tab_archetypes,


@app.cell
def render_tab_projections(ClusterVisualizer, mo, pipeline_results, render_fig):
    _viz = ClusterVisualizer(dpi=100)
    if pipeline_results.get("origin") == "compare":
        _jp_res = pipeline_results["jp_results"]
        _fig_jp_pca = _viz.plot_pca_2d(
            X=_jp_res["preprocessed"].X,
            labels=_jp_res["clustering"].kmeans_labels,
            archetype_map=_jp_res["clustering"].archetype_labels,
            titles=_jp_res["preprocessed"].df["title"],
        )
        _njp_res = pipeline_results["non_jp_results"]
        _fig_njp_pca = _viz.plot_pca_2d(
            X=_njp_res["preprocessed"].X,
            labels=_njp_res["clustering"].kmeans_labels,
            archetype_map=_njp_res["clustering"].archetype_labels,
            titles=_njp_res["preprocessed"].df["title"],
        )
        tab_projections = mo.vstack([
            mo.md("### 🌌 Dual Latent Space Projections (JP vs Non-JP)"),
            mo.hstack([render_fig(_fig_jp_pca), render_fig(_fig_njp_pca)], justify="center", gap=1.0),
        ])
    else:
        _prep = pipeline_results["preprocessed"]
        _clust = pipeline_results["clustering"]
        _fig_pca2d = _viz.plot_pca_2d(
            X=_prep.X,
            labels=_clust.kmeans_labels,
            archetype_map=_clust.archetype_labels,
            titles=_prep.df["title"],
        )
        _fig_pca3d = _viz.plot_pca_3d(
            X=_prep.X,
            labels=_clust.kmeans_labels,
            archetype_map=_clust.archetype_labels,
        )
        _fig_tsne = _viz.plot_tsne_2d(
            X=_prep.X,
            labels=_clust.kmeans_labels,
            archetype_map=_clust.archetype_labels,
        )
        tab_projections = mo.vstack([
            mo.md("### 🌌 Manifold Projections & Latent Archetype Space"),
            mo.hstack([render_fig(_fig_pca2d), render_fig(_fig_tsne)], justify="center", gap=1.0),
            mo.md("### 🧊 3D Latent Spatial Structure"),
            render_fig(_fig_pca3d),
        ])

    return tab_projections,


@app.cell
def render_tab_diagnostics(ClusterVisualizer, mo, pipeline_results, render_fig):
    _viz = ClusterVisualizer(dpi=100)
    if pipeline_results.get("origin") == "compare":
        _jp_clust = pipeline_results["jp_results"]["clustering"]
        _njp_clust = pipeline_results["non_jp_results"]["clustering"]
        _fig_jp_diag = _viz.plot_elbow_and_silhouette(
            elbow_inertias=_jp_clust.elbow_inertias,
            silhouette_scores=_jp_clust.silhouette_scores,
            k_optimal=_jp_clust.k_optimal,
        )
        _fig_njp_diag = _viz.plot_elbow_and_silhouette(
            elbow_inertias=_njp_clust.elbow_inertias,
            silhouette_scores=_njp_clust.silhouette_scores,
            k_optimal=_njp_clust.k_optimal,
        )
        tab_diagnostics = mo.vstack([
            mo.md("### 📈 Cluster Quality Optimization: Japanese Domestic (Left) vs Overseas (Right)"),
            mo.hstack([render_fig(_fig_jp_diag), render_fig(_fig_njp_diag)], justify="center", gap=1.0),
        ])
    else:
        _clust = pipeline_results["clustering"]
        _fig_diag = _viz.plot_elbow_and_silhouette(
            elbow_inertias=_clust.elbow_inertias,
            silhouette_scores=_clust.silhouette_scores,
            k_optimal=_clust.k_optimal,
        )
        _fig_heat = _viz.plot_cluster_heatmap(_clust.cluster_profiles)
        tab_diagnostics = mo.vstack([
            mo.md("### 📈 Silhouette & Elbow Knee Diagnostics"),
            render_fig(_fig_diag),
            mo.md("### 🌡️ Standardized Centroid Feature Loadings Heatmap"),
            render_fig(_fig_heat),
        ])

    return tab_diagnostics,


@app.cell
def render_tab_catalog(df_clustered, mo, pd):
    _display_cols = [
        c for c in [
            "title", "origin_cohort", "sub_origin", "averageScore",
            "popularity", "favourites", "seasonYear", "episodes",
            "duration", "archetype", "cluster_id"
        ] if c in df_clustered.columns
    ]
    _clean_df = df_clustered[_display_cols].copy()
    if "seasonYear" in _clean_df.columns:
        _clean_df["seasonYear"] = pd.to_numeric(_clean_df["seasonYear"], errors="coerce").fillna(0).astype(int)

    catalog_table = mo.ui.dataframe(
        _clean_df,
        page_size=12,
    )

    _csv_data = _clean_df.to_csv(index=False)
    download_btn = mo.download(
        data=_csv_data,
        filename="anime_cluster_catalog.csv",
        label="📥 Export Catalog CSV",
    )

    tab_catalog = mo.vstack([
        mo.hstack([
            mo.md("### 🔍 Interactive Anime Catalog Explorer\n*Filter columns, search titles, and sort features dynamically:*"),
            download_btn,
        ], justify="space-between", align="center"),
        catalog_table,
    ])

    return catalog_table, download_btn, tab_catalog


@app.cell
def render_tab_comparative(ComparativeVisualizer, mo, pipeline_results, render_fig):
    if pipeline_results.get("origin") == "compare":
        _comp_viz = ComparativeVisualizer(dpi=100)
        _df_all = pipeline_results["df_all"]
        _df_jp = pipeline_results["df_jp"]
        _df_non_jp = pipeline_results["df_non_jp"]

        _fig_dist = _comp_viz.plot_origin_distribution(_df_all)
        _fig_score = _comp_viz.plot_score_popularity_divergence(_df_jp, _df_non_jp)
        _fig_format = _comp_viz.plot_format_and_runtime_comparison(_df_jp, _df_non_jp)
        _fig_genre = _comp_viz.plot_genre_divergence(_df_jp, _df_non_jp)

        tab_comparative = mo.vstack([
            mo.md("### 🌏 Cross-Market Structural Contrast (JP vs Non-JP)"),
            mo.hstack([render_fig(_fig_dist), render_fig(_fig_score)], justify="center", gap=1.0),
            mo.hstack([render_fig(_fig_format), render_fig(_fig_genre)], justify="center", gap=1.0),
        ])
    else:
        tab_comparative = mo.callout(
            "Select 'Comparative Cross-Market (JP vs Non-JP)' in the configuration panel to unlock comparative distribution analyses.",
            kind="info",
            title="Cross-Market Mode Inactive",
        )

    return tab_comparative,


@app.cell
def assemble_master_dashboard(
    controls_form,
    df_catalog_summary,
    kpi_strip,
    mo,
    tab_archetypes,
    tab_catalog,
    tab_comparative,
    tab_diagnostics,
    tab_projections,
):
    tabs = mo.ui.tabs({
        "🌟 Discovered Archetypes": tab_archetypes,
        "🌌 Latent Projections": tab_projections,
        "📈 Model Diagnostics": tab_diagnostics,
        "🔍 Catalog Explorer": tab_catalog,
        "⚖️ Cross-Market Compare": tab_comparative,
    })

    dashboard_layout = mo.vstack([
        mo.md(
            """
            # 🎌 AI Anime Archetype Intelligence Hub
            *Interactive Unsupervised Clustering, Latent Space Analytics, and Cross-Market Discovery Engine*
            """
        ),
        kpi_strip,
        mo.accordion({
            "⚙️ Model & Cohort Configuration Panel": controls_form,
            "📊 Catalog Database Breakdown": mo.ui.table(df_catalog_summary),
        }, multiple=False),
        tabs,
    ], gap=1.2)

    dashboard_layout
    return dashboard_layout, tabs


if __name__ == "__main__":
    app.run()
