# Generative UI Stitch Prompts: Cosmic Lofi Apothecary Monograph

This guide provides high-fidelity prompts designed for modern generative UI systems (Google Stitch, v0, Galileo AI, Midjourney UI mode, and WebComponent generators) to produce visual mockups and interactive components adhering strictly to the **Cosmic Lofi Apothecary** design system.

---

## 1. Global Aesthetic Tokens & Atmosphere

When feeding prompts into AI generation pipelines, prepend these design system tokens to ensure coherent styling:

```text
[AESTHETIC STYLE]: Cosmic Lofi Apothecary / Retro-Futuristic Anime Packaging / Beveled Glass Terrarium.
[COLOR PALETTE]: 
- Canvas Ground: Wisteria Violet (#6E58A3 / oklch(58.2% 0.162 295.4))
- Deep Void: Cosmic Abyss (#140C37 / oklch(14.8% 0.078 278.2))
- Liquid Midtone: Deep Indigo (#251C58 / oklch(22.1% 0.092 274.5))
- Specular Glass Highlight: Lilac Quartz (#D5B9F3 / oklch(88.4% 0.052 294.0))
- Tactile Label Ground: Peach Cream (#FAC4A7 / oklch(89.2% 0.074 78.5))
- Sumi Brown Ink: (#2C211B / oklch(21.4% 0.055 280.0))
- Celestial Gold: Star Gold (#FCE277 / oklch(89.4% 0.142 86.2))
- Reactive Accent: Nebula Cyan (#4DF0D2 / oklch(82.5% 0.135 178.0))
- Stopper Metal: Lathe-Knurled Brass (#C89E48 / #5A4214 / #FCE59F)
[TYPOGRAPHY]: Monospaced telemetry ('Space Mono', 'Courier Prime') paired with Japanese Gothic ('Zen Kaku Gothic New') and Classical Mincho ('Shippori Mincho').
[SURFACE PHYSICS]: Glassmorphism 2.0 with physical beveled glass borders, multi-pass inset highlights, and tactile risograph stipple grain.
```

---

## 2. Desktop Dashboard Mockup Stitch Prompt

```text
DESIGN PROMPT:
A sleek, ultra-detailed desktop browser application mockup (1000x640 aspect ratio) for an anime archetype discovery engine titled "insights.anime.ai/marimo-dag". 

WINDOW FRAME & CONTAINER:
- Dark titanium macOS window frame with close, minimize, expand buttons (#FF5F56, #FFBD2E, #27C93F) on the top left.
- Centered address pill containing a cyan security beacon and URL text: "https://insights.anime.ai/marimo-dag" in Space Mono font.
- Canvas background in deep cosmic abyss (#140C37) with subtle starry grain and purple ambient glow.

LEFT SIDEBAR (260px width):
- Titled "MARIMO REACTIVE DAG" in peach parchment typography (#FAC4A7) with a glowing cyan status dot.
- Segmented toggle pill: "JP ANIME" (active, illuminated wisteria violet #6E58A3) vs "GLOBAL / ONA" (inactive, dark purple #251C58).
- Slider control 1: "ARCHETYPE CLUSTERS (k)" with a gold thumb at k=18 (#FCE277) and a glowing gold halo.
- Slider control 2: "MIN MAL SCORE" with cyan slider track set at ≥ 7.50 (#4DF0D2).
- Interactive popularity rank brush showing mini histogram bars in peach cream (#FAC4A7) with dashed bounding box.
- Reactive DAG execution telemetry box displaying sub-millisecond cell benchmark times: Cell 01 (cached), Cell 04 (1.2ms), Cell 09 (6.4ms), Cell 14 (11.8ms).

CENTER TOP PANEL (Visualization Canvas):
- 2D PCA and Barnes-Hut t-SNE dimensionality reduction scatter plot.
- Coordinate axes labeled "t-SNE DIM 1" and "t-SNE DIM 2" with dashed lilac grid lines (#251C58).
- Multiple distinct scatter clusters: Cluster #03 (Nebula Cyan points), Cluster #07 (Star Gold points), Cluster #11 (Lilac Quartz points), Cluster #14 (Terracotta Rose points).
- Cluster centroids marked with glowing diamond astroids.
- Selected node highlighting "Cowboy Bebop" with double pulsating rings and an interactive apothecary tooltip card:
  "COWBOY BEBOP (1998) // Cluster #03: Space Western // Score: 8.75 | Devotion: 94.2%".

CENTER BOTTOM PANEL (Data Inspector Table):
- Polars reactive dataframe table showing 4 selected titles:
  Row 1: "Cowboy Bebop" | Cluster #03 Space Western | Score: ★ 8.75 | Devotion Bar: 94.2% | [JP] Sunrise
  Row 2: "Steins;Gate" | Cluster #07 Time Dilation | Score: ★ 9.08 | Devotion Bar: 96.5% | [JP] White Fox
  Row 3: "Ghost in the Shell: SAC" | Cluster #11 Cyberpunk | Score: ★ 8.68 | Devotion Bar: 89.4% | [JP] Prod. I.G
  Row 4: "The King's Avatar" | Cluster #15 Esports Strat | Score: ★ 8.21 | Devotion Bar: 78.1% | [CN] B.CMAY
- Crisp monospaced tabular numerals, pill badges, and glassmorphic card edges.
```

---

## 3. Mobile App Mockup Stitch Prompt

```text
DESIGN PROMPT:
A mobile UI mockup for iOS/Android (420x840 aspect ratio) inside a smartphone chassis with dark titanium bezel (#251C58) and rounded corners.

STATUS BAR & DYNAMIC ISLAND:
- Centered black Dynamic Island pill featuring camera aperture and a glowing cyan audio/reactive indicator dot.
- Time readout "09:41" in bold Space Mono (#FAC4A7).
- Minimalist status icons: 5G signal bars, Wi-Fi arc, and green battery capsule (98%) in lilac quartz (#D5B9F3).

APP HEADER & SEARCH:
- Micro-pill banner: "COSMIC APOTHECARY // MOBILE" in neon cyan (#4DF0D2).
- Large header: "ANIME ARCHETYPES" in warm peach parchment (#FAC4A7) with subtitle "14,777 TITLES IN 18 LATENT CLUSTERS".
- Search input bar with magnifying glass icon and placeholder: "Search archetypes or anime...".
- Horizontal scroll chip row: "All (Active, wisteria violet with gold rim)", "JP Classic", "Donghua", "Cyberpunk".

STACKED ARCHETYPE CARDS:
- Card 1 (Cowboy Bebop):
  - Glassmorphic card chassis (#231952) with 1.5px wisteria border (#6E58A3).
  - Badge: "CLUSTER #03 // SPACE WESTERN".
  - Main Title: "Cowboy Bebop" with subtext "Spike Spiegel • Bebop Crew • Jazz Noir".
  - Gold star rating "★ 8.75" and member count "1.74M".
  - Horizontal devotion meter with filled cyan bar at 94.2%.
  - Origin badge: "[JP] Sunrise 1998".
- Card 2 (Steins;Gate):
  - Badge: "CLUSTER #07 // TIME DILATION" in bright star gold (#FCE277).
  - Main Title: "Steins;Gate" with subtext "Okabe Rintarou • Future Gadget • World Lines".
  - Rating: "★ 9.08" | Devotion: 96.5% gold meter.
- Card 3 (Ghost in the Shell: SAC):
  - Badge: "CLUSTER #11 // CYBORG MIND" in lilac quartz (#D5B9F3).
  - Main Title: "Ghost in the Shell: SAC" | Rating: "★ 8.68" | Devotion: 89.4%.

BOTTOM NAVIGATION DOCK:
- Floating glassmorphic dock with 4 icon buttons: "Catalog" (Active star gold), "Clusters", "Apothecary", "Profile".
- White home indicator pill at bottom center.
```

---

## 4. Cosmic Apothecary Decanter Vessel Stitch Prompt

```text
DESIGN PROMPT:
An artisanal vector product illustration (500x700 aspect ratio) of the "Cosmic Lofi Apothecary Decanter Vessel" set against a tactile Wisteria Violet background (#6E58A3) with a subtle celestial coordinate grid and floating 4-point diamond sparkles.

STOPPER & COLLAR:
- Heavy lathe-knurled brass stopper cap (#C89E48) with mechanical micro-grooves (#5A4214 and #FCE59F), knurl pattern, and visible screw threads.
- Hermetic seal pill badge labeled: "SEAL: 0.024G HERMETIC" with a glowing cyan telemetry beacon.
- Thick cast glass collar with dual specular highlight ridges (#D5B9F3, #FFFFFF).

GLASS DECANTER BODY:
- Beveled spirits decanter silhouette with thick glass base slab and multi-pass glassmorphism highlights.
- Dual vertical white specular reflection streaks down the left shoulder.
- Interior filled with dark cosmic fluid (#140C37 graduating to #251C58).
- Liquid meniscus adhering upward at both side walls with an elliptical glowing surface meniscus line (#FFFFFF / #D5B9F3).

CELESTIAL MINIATURE ENCLOSURE:
- Floating zero-g astronaut wearing a lilac quartz space suit (#E7D2F3), deep purple life support backpack, and a reflective gold helmet visor (#FCE277), lounging peacefully while drifting.
- Ringed Saturnian gas giant in warm terracotta rose (#FAC4A7 / #CFA7AA) with an elliptical golden ring tilted at an authentic -24 degree astrodynamic angle.
- Twinkling 4-point diamond starbursts (✦) scattered through the cosmic fluid.

3D AXONOMETRIC APOTHECARY LABEL:
- Tilted rectangular parchment label in peach cream (#FAC4A7) projected with a perspective skew (rotateY: -11deg, rotateX: 5deg).
- Sumi brown ink typography (#2C211B):
  - Header: "SPACE JUICE FROM THE MILKY WAY"
  - Bilingual Japanese copy: "宇宙 にはたくさんの 銀河がある。"
  - Vermilion red square prescription seal: "純粋" (Pure)
  - Interstellar chemical formula: "WISTERIA: 420mg / QUARTZ: 18.5mg / INDIGO: 120μL"
  - Telemetry: "● H2O 500ml ● H·II·VII"
  - Authentic variable-pitch barcode strip with catalog accession serial: "№ 14777".
```

---

## 5. Telemetry & Analytics Card Prompts

```text
PROMPTS FOR ARCHITECTURAL DIAGRAMS:

1. PIPELINE FLOW (system_pipeline.svg):
"A horizontal 5-stage data engineering flowchart on a dark cosmic navy canvas (#140C37). Five rounded rectangular cards connected by glowing cyan arrows: Ingestion (01) -> Storage & Dedup (02) -> Hybrid Vectorizer (03) -> Clustering Engine (04) -> Latent Projection (05). Color coded with Wisteria Violet, Lilac Quartz, Peach Parchment, Star Gold, and Nebula Cyan. Bottom telemetry banner: Pipeline Batch Latency 2.84s, Client DAG Latency < 16ms."

2. ORIGIN CASCADE (origin_cascade.svg):
"A 5-level deterministic decision tree flowchart resolving anime geographic provenance. Five hierarchical cards labeled Level 01 (Country ISO 3166), Level 02 (Taxonomic Tags), Level 03 (Studio Gazetteer), Level 04 (Unicode Script Regex), Level 05 (Default Canonical Baseline). Each step outputs a green/cyan match pill with coverage metrics (92.4%, 4.8%, 1.6%, 0.9%, 0.3%) or drops down via a fallthrough arrow."

3. DATABASE SCALING (database_scaling.svg):
"A dual-axis performance analytics chart displaying ingestion throughput (gradient cyan/violet bars) and RAM consumption (glowing gold line graph) across 1K, 5K, 15K, and 40K anime records. 15K marked with a star callout at 2,980 rec/s and 46.8 MB memory."

4. WASM ARCHITECTURE (wasm_architecture.svg):
"A serverless zero-backend WebAssembly architecture schematic showing 5 sequential processing nodes: Netlify Edge CDN -> 1.14 MB Brotli Compressed Artifact -> Pyodide WASM Runtime (Python 3.11) -> Marimo Reactive DAG -> Hardware Accelerated DOM/Canvas 60 FPS Render. Connected by glowing cyan pipeline pipes."
```
