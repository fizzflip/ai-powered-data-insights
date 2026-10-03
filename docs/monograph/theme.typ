// ============================================================================
// COSMIC LOFI APOTHECARY TYPST THEME & DESIGN SYSTEM
// Based on docs/design.md (design-idea-2)
// Palette: Wisteria Violet, Midnight Abyss, Peach Parchment, Star Gold, Nebula Cyan
// ============================================================================

#let wisteria = rgb("#6E58A3")
#let abyss = rgb("#140C37")
#let midnight = rgb("#251C58")
#let glass-specular = rgb("#D5B9F3")
#let glass-reflection = rgb("#E7D2F3")
#let glass-caustic = rgb("#AB9ADC")
#let parchment = rgb("#FAC4A7")
#let parchment-light = rgb("#FFF4ED")
#let parchment-border = rgb("#D4BC94")
#let sumi-ink = rgb("#2C211B")
#let vermilion = rgb("#E07A5F")
#let star-gold = rgb("#FCE277")
#let star-gold-dark = rgb("#9E8019")
#let nebula-cyan = rgb("#4DF0D2")
#let terracotta = rgb("#CFA7AA")
#let brass = rgb("#C89E48")
#let brass-dark = rgb("#7D5E20")

// Neutrals & Surface tones for print readability
#let text-dark = rgb("#1E1A29")
#let text-muted = rgb("#605770")
#let bg-paper = rgb("#FCFBFD")
#let card-bg = rgb("#F6F3FA")
#let stroke-light = rgb("#E4DCF0")

// Fonts configuration
#let font-display = ("Space Mono", "IBM Plex Mono", "Noto Sans")
#let font-mono = ("Space Mono", "JetBrainsMono NF", "DejaVu Sans Mono")
#let font-body = ("Inter", "Noto Sans", "Zen Kaku Gothic New")
#let font-jp = ("Zen Kaku Gothic New", "Noto Sans CJK JP")

// ============================================================================
// REUSABLE MACROS & CALLOUT COMPONENTS
// ============================================================================

// 1. Cosmic Apothecary Spec Sheet (Dark Deep Void Glass Container)
#let spec-callout(title: "SPECIFICATION", body) = {
  block(
    fill: abyss,
    inset: (x: 16pt, y: 14pt),
    radius: 6pt,
    stroke: 1.2pt + glass-specular,
    width: 100%,
    [
      // #place(top + right, dy: -4pt)[
      // #text(font: font-display, size: 7pt, fill: nebula-cyan, tracking: 0.12em)[● ACTIVE SEAL]
      // ]
      #text(font: font-display, size: 9pt, weight: "bold", fill: star-gold, tracking: 0.08em)[#title]
      #v(6pt)
      #line(length: 100%, stroke: 0.8pt + glass-specular.transparentize(50%))
      #v(6pt)
      #set text(fill: rgb("#F0ECF8"), size: 8.5pt)
      #body
    ],
  )
}

// 2. Peach Parchment Apothecary Prescription Note
#let parchment-card(title: "PRESCRIPTION NOTE", stamp: "VERIFIED", body) = {
  block(
    fill: parchment-light,
    inset: (x: 16pt, y: 14pt),
    radius: 4pt,
    stroke: 1pt + parchment-border,
    width: 100%,
    [
      #grid(
        columns: (1fr, auto),
        align: (left, right),
        [
          #text(font: font-display, size: 8.5pt, weight: "bold", fill: sumi-ink, tracking: 0.06em)[#title]
        ],
        [
          #box(
            stroke: 1pt + vermilion,
            inset: (x: 6pt, y: 2pt),
            radius: 2pt,
            baseline: 0%,
            text(font: font-display, size: 7pt, weight: "bold", fill: vermilion, tracking: 0.15em)[#stamp],
          )
        ],
      )
      #v(4pt)
      #line(length: 100%, stroke: (paint: parchment-border, dash: "dashed"))
      #v(6pt)
      #set text(font: font-body, fill: sumi-ink, size: 8.8pt)
      #body
    ],
  )
}

// 3. Compact Telemetry Pill Badge
#let telemetry-pill(label, val, color: nebula-cyan) = {
  box(
    fill: abyss,
    inset: (x: 6pt, y: 3pt),
    radius: 10pt,
    stroke: 0.8pt + glass-specular.transparentize(40%),
    baseline: 20%,
    [
      #box(circle(radius: 2.2pt, fill: color))
      #h(3pt)
      #text(font: font-display, size: 6.8pt, fill: rgb("#FFFFFF"), tracking: 0.05em)[#label:]
      #h(2pt)
      #text(font: font-display, size: 6.8pt, weight: "bold", fill: star-gold)[#val]
    ],
  )
}

// 4. Metric Statistic Card
#let metric-card(title, value, subtitle: none, delta: none) = {
  block(
    fill: card-bg,
    inset: (x: 14pt, y: 12pt),
    radius: 6pt,
    stroke: 1pt + stroke-light,
    width: 100%,
    [
      #text(font: font-display, size: 7.5pt, weight: "bold", fill: text-muted, tracking: 0.08em)[#upper(title)]
      #v(4pt)
      #grid(
        columns: (1fr, auto),
        align: (bottom + left, bottom + right),
        [
          #text(font: font-display, size: 18pt, weight: "bold", fill: wisteria)[#value]
        ],
        [
          #if delta != none [
            #box(
              fill: nebula-cyan.transparentize(80%),
              inset: (x: 5pt, y: 2pt),
              radius: 4pt,
              text(font: font-display, size: 7pt, weight: "bold", fill: abyss)[#delta],
            )
          ]
        ],
      )
      #if subtitle != none [
        #v(2pt)
        #text(font: font-body, size: 7.8pt, fill: text-muted)[#subtitle]
      ]
    ],
  )
}

// 5. Styled Data Table Wrap
#let styled-table(columns: (), ..cells) = {
  table(
    columns: columns,
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + wisteria) } else { 0.5pt + stroke-light },
    fill: (x, y) => if y == 0 { abyss } else if calc.even(y) { card-bg } else { white },
    align: (col, row) => if row == 0 { center + horizon } else { left + horizon },
    ..cells
  )
}

// 6. Master Monograph Template Config
#let monograph-template(
  title: "AI-Powered Anime Data Insights",
  subtitle: "Multi-Source Unsupervised Clustering, Latent Space Projections & Empirical Archetype Discovery",
  accession: "№ 14777",
  edition: "FIRST PRODUCTION EDITION // 2026.10",
  authors: ("DeepMind Cognitive Systems", "AI Insights Autonomous Team"),
  body,
) = {
  set document(title: title, author: authors)

  // Page setup
  set page(
    paper: "a4",
    margin: (top: 2.8cm, bottom: 2.6cm, left: 2.5cm, right: 2.5cm),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 1 [
        #grid(
          columns: (1fr, auto),
          align: (left, right),
          [
            #text(font: font-display, size: 7.5pt, fill: wisteria, tracking: 0.1em)[
              #upper(title) \/\/ #accession
            ]
          ],
          [
            // #text(font: font-jp, size: 7.5pt, fill: text-muted)[
            //   宇宙にはたくさんの銀河がある。
            // ]
          ],
        )
        #v(2pt)
        #line(length: 100%, stroke: 0.6pt + glass-specular)
      ]
    },
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 1 [
        #line(length: 100%, stroke: 0.6pt + stroke-light)
        #v(4pt)
        #grid(
          columns: (1fr, auto, 1fr),
          align: (left, center, right),
          [
            // #text(font: font-display, size: 7pt, fill: text-muted)[
            //   #edition
            // ]
          ],
          [
            #box(
              circle(radius: 2pt, fill: nebula-cyan),
              baseline: 0%,
            )
            #h(4pt)
            #text(font: font-display, size: 8pt, weight: "bold", fill: wisteria)[
              #page-num
            ]
            #box(
              circle(radius: 2pt, fill: nebula-cyan),
              baseline: 0%,
            )

          ],
          [
            // #text(font: font-display, size: 7pt, fill: text-muted)[
            //   CONFIDENTIAL & PROPRIETARY
            // ]
          ],
        )
      ]
    },
  )

  // Typography
  set text(
    font: font-body,
    size: 9.6pt,
    fill: text-dark,
    spacing: 120%,
    lang: "en",
  )

  set par(
    justify: true,
    leading: 0.72em,
    first-line-indent: 0pt,
  )

  // Headings styling
  show heading.where(level: 1): it => block(
    width: 100%,
    stroke: (bottom: 2pt + wisteria),
    inset: (bottom: 6pt),
    above: 24pt,
    below: 14pt,
    [
      #grid(
        columns: (auto, 1fr),
        gutter: 10pt,
        align: (horizon, horizon),
        [
          #box(
            fill: wisteria,
            inset: (x: 8pt, y: 4pt),
            radius: 3pt,
            text(font: font-display, size: 10pt, weight: "bold", fill: white)[#counter(heading).display()],
          )
        ],
        [
          #text(font: font-display, size: 14pt, weight: "bold", fill: abyss, tracking: 0.04em)[#upper(it.body)]
        ],
      )
    ],
  )

  show heading.where(level: 2): it => block(
    above: 18pt,
    below: 10pt,
    [
      #text(font: font-display, size: 11pt, weight: "bold", fill: midnight, tracking: 0.03em)[
        #it.body
      ]
    ],
  )

  show heading.where(level: 3): it => block(
    above: 14pt,
    below: 8pt,
    [
      #text(font: font-display, size: 9.5pt, weight: "bold", fill: wisteria)[
        #it.body
      ]
    ],
  )

  // Code / raw formatting
  show raw.where(block: true): it => block(
    fill: abyss,
    inset: 10pt,
    radius: 5pt,
    width: 100%,
    stroke: 0.8pt + glass-specular.transparentize(50%),
    [
      #set text(font: font-mono, size: 7.6pt, fill: rgb("#E9E3F5"))
      #it
    ],
  )

  show raw.where(block: false): it => box(
    fill: card-bg,
    inset: (x: 4pt, y: 1.5pt),
    radius: 3pt,
    stroke: 0.5pt + stroke-light,
    text(font: font-mono, size: 8.2pt, fill: wisteria, it),
  )

  // Equations
  show math.equation.where(block: true): it => block(
    fill: card-bg,
    inset: (y: 10pt),
    radius: 4pt,
    width: 100%,
    stroke: (left: 3pt + wisteria),
    align(center, it),
  )

  body
}

// 7. Cover Page Generator
#let cover-page(
  title: "AI-POWERED ANIME DATA INSIGHTS",
  subtitle: "Multi-Source Unsupervised Clustering, Latent Space Projections and Empirical Archetype Discovery",
  kanji-title: "星間幾何学と機械学習による次元分類体系",
  accession: "ACCESSION № 14777",
  authors: ("DeepMind Cognitive Systems", "AI Insights Autonomous Team"),
  date: "OCTOBER 2026",
  abstract: none,
) = {
  page(
    paper: "a4",
    margin: 0cm,
    header: none,
    footer: none,
    [
      #rect(
        width: 100%,
        height: 100%,
        fill: abyss,
        [
          #place(top + left, dx: 1.5cm, dy: 1.5cm)[
            #rect(
              width: 18cm,
              height: 26.7cm,
              stroke: 1.5pt + glass-specular.transparentize(30%),
              radius: 8pt,
              inset: 1.6cm,
              [
                #grid(
                  columns: (1fr, auto),
                  align: (left, right),
                  [
                    #text(font: font-display, size: 8pt, fill: star-gold, tracking: 0.15em)[#accession]
                    // #telemetry-pill("SYSTEM", "COSMIC APOTHECARY // ARCH-V2", color: nebula-cyan)
                  ],
                  [
                    // #text(font: font-display, size: 8pt, fill: star-gold, tracking: 0.15em)[#accession]
                  ],
                )

                #v(2cm)

                #text(font: font-jp, size: 10pt, fill: glass-specular, tracking: 0.2em)[
                  #kanji-title
                ]

                #v(0.5cm)

                #text(font: font-display, size: 21pt, weight: "bold", fill: white, tracking: 0.04em)[
                  #title
                ]

                #v(0.5cm)

                #line(length: 100%, stroke: 2pt + star-gold)

                #v(0.5cm)

                #text(font: font-body, size: 10.5pt, fill: glass-reflection, style: "italic")[
                  #subtitle
                ]

                #v(1.0cm)

                #if abstract != none [
                  #parchment-card(title: "RESEARCH ABSTRACT // 概要", stamp: "VERIFIED")[
                    #abstract
                  ]
                ]

                #align(bottom)[
                  #grid(
                    columns: (1fr, 1fr),
                    align: (left, right),
                    [
                      #text(font: font-display, size: 8pt, fill: glass-specular)[AUTHOR:]\
                      #for a in authors [
                        #text(font: font-body, size: 8.8pt, weight: "bold", fill: white)[#a]\
                      ]
                    ],
                    [
                      #text(font: font-display, size: 8pt, fill: glass-specular)[DATE & REVISION:]\
                      #text(font: font-display, size: 8.8pt, weight: "bold", fill: star-gold)[#date]\
                      #text(font: font-display, size: 7.5pt, fill: nebula-cyan)[STATUS: PRODUCTION MASTER]
                    ],
                  )
                  #v(0.3cm)
                  #line(length: 100%, stroke: 0.6pt + glass-specular.transparentize(50%))
                  #v(0.2cm)
                  #align(center)[
                    #text(font: font-jp, size: 7.8pt, fill: glass-specular)[
                      #show link: underline
                      #link("https://github.com/fizzflip/ai-powered-data-insights/")[Codebase on GitHub] \
                      #link("https://ai-insights-anime.netlify.app/")[Marimo Notebook on Netlify]
                    ]
                  ]
                ]
              ],
            )
          ]
        ],
      )
    ],
  )
}
