<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Design plan: the MEMORY demo page

Owner request of 2026-11-26: every lab demo gets its own brand, motion and premium UI. This page replaces the shared editorial look.

## Subject, audience, job

- **Subject.** Review schedules for flash cards: when to see a card again, under a fixed number of reviews. The vernacular is the paper Leitner box (index cards filed in boxes that are reviewed less and less often) and the forgetting curve as a psychologist would plot it by hand on graph paper.
- **Audience.** A curious technical reader; an admissions committee skimming for rigour; a researcher checking the numbers and the method.
- **Primary job.** State the question and the honest answer in one sentence, show the forgetting curves of the five schedules as a lab sheet, then let the reader check every estimate, assumption and limitation, and play with the engine.

## Colour (light only: the brand is paper and ink)

| Name | Hex | Role |
|---|---|---|
| Graph paper | `#ECF1EF` | page ground, a cool sea-glass grey, never cream |
| Card stock | `#FDFDFB` | index cards, tables, the sandbox tray |
| Rule cyan | `#A9CBD1` | ruled lines of the cards and the graph-paper grid; decoration only, never text |
| Ink blue | `#1D3787` | headings, links, axes, the logo, the greedy arm |
| Graphite | `#33373D` | body text, pencil annotations (muted graphite `#565B62` for secondary text) |
| Margin red | `#B8323A` | the single red header rule of an index card, the focus ring, "forgotten" and "not run" |

Arm colours are inks that sit on paper: ink blue (greedy), red ink (expanding), graphite (uniform), green ink (Leitner), ochre (massed), violet (greedy with power model), magenta (greedy with exponential model). Every line keeps its own dash pattern and a direct label, so colour never carries meaning alone.

## Type

Revised on 2026-11-26 (owner request: no typeface shared between lab demos; Zilla Slab and Alegreya Sans belong to other demos).

- **Courier Prime** (700 and 400; OFL): display only. Headings, the wordmark, the filing tabs and section tabs of the bar, the typed figures on the overview index cards, the box labels of the hero and the Run button. Index cards were typed on typewriters; Courier Prime is a typewriter face redrawn for the screen, so headings read as typed card labels.
- **Crimson Pro** (400, 400 italic, 600; OFL): body, tables, chart labels, controls, status labels. An old-style book serif that reads like the printed page of a psychology paper, with tabular figures (`tnum`) for every column of numbers.

Monospace check: a monospace face for small data labels is one of the generated-page tells. Courier Prime is therefore kept to display sizes and to the typed card entries; every table, chart tick, axis label and status label is set in Crimson Pro. Crimson Pro has no Greek glyphs, so ω, σ, α, β and Δ fall back to Georgia or Times New Roman, both serifs close to Crimson Pro in weight.

Scale: body 19 px (Crimson Pro has a small x-height), 15 px small, h1 clamp(26 px, 3.3vw, 41 px) and h2 clamp(23 px, 3vw, 30 px) in Courier Prime 700 with -0.02em tracking (a monospace is wide, so display sizes are smaller than with the earlier slab), card figures 37 px. Prose capped at 42 rem.

## Layout concept

A lab notebook on a graph-paper desk. Content is left aligned in one 72 rem column, prose capped at 40 rem. The sticky bar is a strip of card-index tabs.

```
+------------------------------------------------------------------------+
| [mark] Memory   Question  Curves  Calendar  Results  ...  Playground    |  sticky tab strip
+------------------------------------------------------------------------+
| Which review schedule maximizes        |  +--------------------------+  |
| modelled recall under a fixed budget?  |  | recall of one card ~~/|~~ |  |
|                                        |  |  [1][2][3][4][5] Leitner  |  |
| Answer: no schedule is best in general |  |   cards sliding box to box|  |
| status, author line                    |  |  Illustration, not data   |  |
+----------------------------------------+--+--------------------------+--+
|  _EXP-001_   _EXP-002_   _EXP-003_       filed index cards with tabs     |
|  0.0162      0.0085      70 of 72                                        |
+------------------------------------------------------------------------+
| Lab sheet: forgetting curves on graph paper; segmented controls          |
| interval chart; table                                                    |
+------------------------------------------------------------------------+
| Calendar | Results (cards per experiment) | Assumptions | Method          |
| Playground: a card tray with Run, progress as a card filling            |
| Footer: links, licence, AI-use line, font credits                       |
+------------------------------------------------------------------------+
```

## Motion

- **One orchestrated hero moment (about 2.6 s, once).** A Leitner box of five compartments. Cards lift one after another from box 1 and slide to the next box; one card is forgotten, gets a red pencil tick and slides back to box 1. Above, one card's forgetting curve is inked from left to right, its saw-tooth jumping back at each review and decaying more slowly each time. CSS keyframes on `transform` and `opacity`, plus a `clip-path` reveal for the ink line. Labelled visibly "Illustration, not study data"; it shows no numbers other than the box numbers, which are a real sequence.
- **Motion that answers the reader.** Charts ink in once when scrolled into view (`clip-path` reveal of the plot, 700 ms, strong ease-out). Segmented controls (forgetting model, budget, items) move a card-stock thumb with `transform` (200 ms). The playground's progress is a card filling; finished output appears with an opacity fade. The Run button presses to `scale(0.97)`.
- **Rules.** Transform, opacity and clip-path only; `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`; no `transition: all`; hover effects only under `(hover: hover) and (pointer: fine)`; under `prefers-reduced-motion` every animation is removed and the hero shows its final arrangement.

## The one memorable thing

The Leitner box that sorts itself when the page opens. Everything else stays quiet: paper, ink, ruled lines.

## Review against the generated-page tells, and against the other demos

- *Cream plus terracotta*: avoided. The ground is a cool graph-paper grey-green; the only warm colour is a thin red rule, as on a real index card.
- *Near-black with one acid accent*: not used; light paper only.
- *All-caps tracked eyebrows*: the old kicker "MEMORY · a simulation study..." (an uppercase eyebrow joined with a middle dot) is removed. Card tabs carry experiment ids in sentence case; they are filing information, not decoration.
- *Mono data labels*: none; tables and charts use Crimson Pro tabular figures; Courier Prime appears only at display sizes (see Type).
- *01/02/03 markers*: only the Leitner box numbers 1 to 5, which are a real sequence.
- *Identical rounded SaaS cards*: the three overview cards were first planned as plain rounded panels; revised into index cards with ruled lines, a red header rule and a filing tab, with a 2 px radius like real card stock. Result panels below are lab-sheet sections, not cards.
- *Fade-up on every section*: none. Only charts ink in, once.
- *Middle-dot meta strings*: the "Report ... · Claims ..." line becomes two labelled lines.
- *Against the other demos*: STREAK (warm daylight habit calendar, day grid) is warm and grid-of-days; MEMORY is cool paper, ink and cards, with curves rather than grids as its signature. FARE, ECHO, PULSE and SCROLL use boards, discs, strips and timers; none uses index cards or graph paper.

What changed after this review: the overview panels became tabbed index cards; the eyebrow and middle-dot strings were removed; a planned handwriting font for chart annotations was dropped (a third family, and hard to read at small sizes); the dark scheme was dropped because ink on paper is the brand and a half-hearted dark version would weaken it.
