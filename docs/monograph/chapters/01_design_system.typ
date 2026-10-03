// ============================================================================
// CHAPTER 01: MASTER DESIGN SYSTEM & UI KIT SPECIFICATION
// Cosmic Lofi Apothecary Monograph // Accession: № 14777
// ============================================================================

#import "../theme.typ": *

= Master Design System & UI Kit Specification

== Tactile Skeuomorphism & Physical Materiality

The *Cosmic Lofi Apothecary* UI architecture represents an intentional departure from the homogenized "flat SaaS" aesthetic that has characterized digital interfaces over the past decade. Where typical analytics dashboards rely on generic rounded rectangles, washed-out grey containers, and sterile vector charts, our design system treats the user interface as a physical, handcrafted laboratory apparatus. The interface is engineered to evoke the tactile heft of laboratory borosilicate glassware, the organic tooth of heavy-cotton prescription parchment, the lathe-turned weight of knurled brass hardware, and the celestial luminescence of stellar radiation.

By anchoring interactive data components to physical optics and Newtonian mechanics, cognitive dissonance is reduced: users interact not with abstract database abstractions, but with tangible physical containers whose behavior conforms to intuitive optical and kinetic laws.

#v(8pt)

#align(center)[
  #image("../assets/flask_mockup.svg", width: 75%)
]

#v(8pt)

== The 7 Core Production UI Kit Components

The visual and functional hierarchy of the interface is grounded in seven distinct physical components, detailed comprehensively below:

=== 1. Beveled Glass Terrarium Flask
The outer vessel models the optics of heavy-cast, molded borosilicate glass ($n approx 1.47$). Rather than the primitive Gaussian-blurred panels of "Glassmorphism 1.0", our *Glassmorphism 2.0* architecture models multi-pass surface reflections, Fresnel boundary bevels, and atmospheric drop shadows.

The chassis utilizes a compound box-shadow array to simulate physical glass wall thickness:
- *Outer Atmospheric Shadow*: `0 24px 48px -12px rgba(9, 7, 16, 0.55)` grounds the container against the Wisteria canvas.
- *Specular Rim Highlight*: `-1px -1px 0 1px rgba(255, 255, 255, 0.75)` models sharp incident light along the top-left crown.
- *Inner Beveled Highlight*: `inset 2px 2px 0 0 rgba(255, 255, 255, 0.85)` and `inset 6px 6px 18px 0 rgba(213, 185, 243, 0.35)` simulate internal refraction within the glass wall.
- *Dark Refraction Rim*: `inset -4px -4px 14px 0 rgba(13, 11, 24, 0.65)` provides opposing optical absorption.
- *Cast Glass Slab Base*: `inset 0 -18px 24px -6px rgba(8, 4, 20, 0.85)` reproduces the dense, light-trapping base of antique spirits decanters.

Dual vertical specular streaks are positioned along the left flank of the vessel: a primary 5px streak (`rgba(255, 255, 255, 0.85)`) running 380px vertically, and an adjacent secondary 2px hairline highlight (`rgba(213, 185, 243, 0.5)`) to replicate the cylindrical curvature of the vial walls.

=== 2. Cosmic Apothecary Label
The prescription label is constructed as an untreated cotton-parchment ground (`#FAC4A7`) imprinted with sumi ink (`#2C211B`) and a vermilion cinnabar seal (`#E07A5F`). To break flat screen plane monotony, the label is rendered with an authentic *3D axonometric tilt projection*:

```css
.apothecary-label {
  transform: perspective(900px) rotateY(-11deg) rotateX(5deg)
             rotateZ(-1deg) skewY(2.5deg);
  box-shadow: 3px 6px 14px rgba(9, 7, 16, 0.45),
              inset 0 0 10px rgba(212, 188, 148, 0.35);
}
```

The label features an authentic Japanese bilingual typographic hierarchy:
- Primary Title: `SPACE JUICE FROM THE MILKY WAY` typeset in monospaced uppercase with `0.08em` tracking.
- Japanese Inscription: `宇宙 にはたくさんの銀河がある。` rendered with `font-feature-settings: "palt" 1` to guarantee proportional Japanese punctuation metrics and eliminate awkward typographic whitespace.
- Barcode Strip: A procedural repeating linear gradient simulating commercial code bars with variable line weights (1.5px, 3.0px, 4.5px), accompanied by the accession serial `№ 14777`.
- Telemetry Row: Monospaced chemical fraction and volume metadata (`● H2O 500ml ● H·II · VII`).

=== 3. Liquid Meniscus Fluid Physics
When fluid contacts solid glass, adhesive forces between liquid molecules and the silicate surface overcome cohesive fluid tension, creating a curved capillary boundary known as the *elliptical meniscus*. In our interface, the cosmic void liquid does not end at an artificial horizontal line; it curves upward dynamically where it touches the glass chassis.

To simulate responsive fluid motion during user interaction (such as mouse movement, container dragging, or scroll acceleration), the meniscus is driven by a *Damped Harmonic Oscillator*:

$ m frac(d^2 x, d t^2) + c frac(d x, d t) + k x = F_("external") $

In our discrete client-side physics loop, the state update is computed at 60 Hz as follows:

$ F_("spring") = -k dot x_t $
$ v_(t+1) = (v_t + F_("spring")) dot (1 - gamma) $
$ x_(t+1) = x_t + v_(t+1) $

where:
- $k = 0.045$ represents the spring tension constant of the cosmic fluid,
-  = 0.88$ represents the viscous damping coefficient,
- $x_t$ is the liquid slosh displacement amplitude (clamped within $[-40"px", +40"px"]$).

The resulting boundary is mapped to an SVG cubic Bézier path (`d="M 60,leftY Q 200,controlY 340,rightY L ..."`), producing smooth, organic waves that dissipate naturally after perturbation.

=== 4. Drifting Astronaut & Planetary Rings
Floating within the interior chamber is a vectorized zero-g astronaut and a Saturnian gas giant:
- *Gas Giant Planet*: A 48px spherical body styled with an internal radial gradient transitioning from peach parchment (`#FAC4A7`) through terracotta rose (`#CFA7AA`) to deep wisteria (`#503C8F`). Encircling the sphere is an elliptical ring system tilted at an authentic astrodynamic inclination of $-24^\circ$ (`transform: translate(-50%, -50%) rotate(-24deg)`).
- *Zero-G Astronaut*: Rendered with an EVA spacesuit (`#E7D2F3`), deep midnight life-support backpack (`#251C58`), and a curved golden visor (`#FCE277`).
- *Harmonic Oscillation*: The astronaut undergoes an unhurried 7-second sinusoidal drift cycle (`zeroGFloat`) combining vertical translation ($Delta y in [-10"px", +4"px"]$) and gentle angular rotation ($theta in [-3 degree, +6 degree]$), visually communicating weightless equilibrium.

=== 5. 4-Point Diamond Starbursts (✦ / ✧)
To evoke the aesthetic of vintage science-fiction cel animation, stellar sparkles are modeled as geometric *astroids* rather than generic circles or 5-point stars. The Cartesian astroid satisfies:

$ x^(2/3) + y^(2/3) = a^(2/3) $

Approximated in vector rendering via an 8-point polygon clipping path:
```css
clip-path: polygon(
  50% 0%, 58% 42%, 100% 50%, 58% 58%,
  50% 100%, 42% 58%, 0% 50%, 42% 42%
);
```
Each starburst is styled with Star Gold (`#FCE277`) and an ambient neon bloom (`filter: drop-shadow(0 0 6px #FCE277)`). Sparkles animate with asynchronous phase offsets ($-1.2"s"$, $-2.1"s"$), executing combined scale pulsation ($0.70 arrow.r 1.15$) and 180-degree axial rotation over a 3.2-second cycle.

=== 6. Threaded Brass Stopper & Glass Neck HUD
The top of the vessel features an industrial closure system comprising:
- *Lathe-Knurled Brass Stopper*: A brass cap (`#C89E48` to `#7D5E20`) featuring high-density vertical knurling textures achieved via a repeating linear gradient of 1.5px micro-ridges (`#5A4214` to `#FCE59F`).
- *Precision Screw Threads*: Dual beveled thread ridges demonstrating mechanical engagement with the glass neck.
- *Glass Neck Telemetry HUD*: A rounded telemetry pill (`#140C37` background with a glass-specular border) enclosing an active `#4DF0D2` cyan beacon. The HUD displays real-time atmospheric seal telemetry: `SEAL: HERMETIC // 0.024 G`.

=== 7. Tactile Ingredient & Nutrition Spec Table
Affixed as an accompanying laboratory data sheet, the specification table renders quantitative media telemetry using an authentic apothecary formulation schema:
- *Wisteria Essence / 藤紫星雲抽出液*: `420.0 mg` (Visual color-ground density)
- *Zero-G Quartz / 反重力水晶末*: `18.5 mg` (Inertial physics weight)
- *Indigo Photons / 真夜中藍光粒子*: `120.0 μL` (Latent manifold energy)

All tabular figures enforce `font-variant-numeric: tabular-nums` to guarantee vertical decimal alignment during live telemetry updates.

#v(10pt)

== The 20-Point "Craft & Polish" Zero-Slop Audit Checklist

To guarantee that the production implementation maintains uncompromised craftsmanship and eliminates sloppy design artifacts, the entire user interface is audited against the strict 20-point verification checklist below:

#v(6pt)

#styled-table(
  columns: (32pt, 125pt, 1fr),
  [#text(fill: white, weight: "bold")[№]],
  [#text(fill: white, weight: "bold")[Dimension]],
  [#text(fill: white, weight: "bold")[Verification Gate & Inspection Standard]],

  [*01*], [*Glass Bevel Optics*], [Flask borders must use multi-pass inset shadows (`inset 2px 2px`, `inset -4px -4px`). Zero flat 1px solid white borders permitted.],
  [*02*], [*Fluid Meniscus Curve*], [Liquid boundary must adhere upward at glass walls using dynamic SVG Bézier geometry or calibrated border radius.],
  [*03*], [*Axonometric Label Skew*], [Apothecary label must be projected with 3D axonometric tilt (`perspective(900px) rotateY(-11deg) rotateX(5deg) ...`).],
  [*04*], [*Risograph Paper Grain*], [Background and vessel surfaces must exhibit subtle stochastic paper tooth via SVG `<feTurbulence>` filter overlay.],
  [*05*], [*Bilingual Font Metrics*], [Japanese typography must declare `font-feature-settings: "palt" 1` to eliminate disproportionate whitespace around punctuation.],
  [*06*], [*Zero-G Harmonic Drift*], [Drifting astronaut must oscillate with a 7-second sinusoidal ease-in-out cycle combining translation and rotation.],
  [*07*], [*Astroid Starburst Form*], [4-point diamond sparkles must use mathematical astroid geometry or 8-point polygon clipping. Zero 5-point stars.],
  [*08*], [*Display P3 Fallbacks*], [All OKLCH color declarations (Wisteria, Star Gold, Cyan) must provide standard sRGB hex fallbacks for legacy browsers.],
  [*09*], [*Dual Specular Highlights*], [Vessel flank must render two distinct vertical light streaks (`primary` at 5px, `secondary` at 2px) with linear alpha decay.],
  [*10*], [*Barcode Precision*], [Barcode stripes must be procedurally generated with varying line weights (1.5px, 3px, 4.5px) rather than static bitmap clips.],
  [*11*], [*Knurled Brass Stopper*], [Vessel closure must feature simulated lathe-knurled brass grooves and visible mechanical screw threads.],
  [*12*], [*Slosh Damping Physics*], [Cursor movement must introduce kinetic fluid slosh that settles smoothly via a damped harmonic oscillator ($k=0.045, gamma=0.88$).],
  [*13*], [*Planetary Inclination*], [Saturnian gas giant rings must possess an authentic astrodynamic axial tilt of $-24^\circ$.],
  [*14*], [*No Nested Blur Filters*], [`backdrop-filter: blur(...)` is restricted strictly to the outer chassis to prevent GPU compositing thrash and frame drops.],
  [*15*], [*Zero Text Selection Leaks*], [Purely decorative elements (barcodes, serial numbers, planetary spheres) must declare `user-select: none`.],
  [*16*], [*Tabular Numeral Stability*], [All numeric telemetry, stardates, and serial identifiers must enforce `font-variant-numeric: tabular-nums` to eliminate layout jitter.],
  [*17*], [*Reduced Motion Honors*], [When `prefers-reduced-motion: reduce` is active, astronaut drift, starburst twinkling, and fluid slosh instantly freeze.],
  [*18*], [*Responsive Stage Scaling*], [Flask stage scales fluidly across viewports via `width: min(85vw, 420px)` and CSS container queries without element clipping.],
  [*19*], [*Passive Event Handlers*], [All client-side pointer tracking and scroll listeners must declare `{ passive: true }` to keep the main thread unblocked.],
  [*20*], [*Core Web Vitals Integrity*], [Complete interactive stage must achieve 60fps scrolling, Cumulative Layout Shift (CLS) $\equiv 0.000$, and LCP $\le 1.1\text{s}$.]
)

#v(10pt)

#spec-callout(title: "ENGINEERING VERIFICATION SUMMARY")[
  The 20-Point Craft & Polish standard ensures that the *Cosmic Lofi Apothecary* UI functions not merely as an illustrative novelty, but as a production-grade, highly performant scientific user interface. By adhering to strict GPU memory budgets, CSS hardware acceleration, and tabular typographic alignment, the interface marries artisanal visual delight with uncompromising runtime efficiency.
]
