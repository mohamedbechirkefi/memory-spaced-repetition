<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Feasibility audit (M0, 2026-11-24)

All outputs below are copied from commands actually run in this session. Note (2026-11-26, owner, 2026-11-26, decision sheet, B9): the commands were run with absolute paths; the home folder is now written `~`, and the shared tools folder `../.tools/` (relative to the repository) and `helix/.tools/` (under the research root). Outputs are unchanged.

## 1. Hardware

| Item | Command | Output |
|---|---|---|
| CPU | `sysctl -n machdep.cpu.brand_string` | `Apple M1 Pro` |
| Cores | `sysctl -n hw.ncpu` | `10` |
| Memory | `sysctl -n hw.memsize` | `17179869184` (16 GiB) |
| OS | `sw_vers` | `macOS 15.3.1`, build `24D70` |
| Free disk | `df -h ~` | `129Gi` available at the first check, `128Gi` at the second (460Gi volume) |

Confirms the brief: Apple M1 Pro, 10 cores, 16 GB RAM, macOS 15.3.1, about 127 to 129 GB free.

## 2. Tools

| Tool | Command | Output |
|---|---|---|
| Python | `/usr/local/bin/python3 --version` | `Python 3.12.1` |
| uv | `../.tools/py/bin/uv --version` | `uv 0.9.5 (d5f39331a 2025-10-21)` |
| typst, pypdf, pillow | import in `../.tools/py/bin/python` | `typst 0.15.0`, `pypdf 6.20.0`, `pillow 11.3.0` |
| pandoc | `../.tools/pandoc --version` | `pandoc 3.6.3` |
| Node | `helix/.tools/node/bin/node --version` | `v22.23.3` (read-only use) |
| git | `git --version` | `git version 2.42.1` |
| TeX | `which tex pdflatex xelatex typst` | all `not found` (no TeX distribution; no typst CLI on PATH; the Python package is used) |

## 3. Publication toolchain (decision D-002)

Exploratory smoke check, run in the session scratchpad (not committed):

1. `pandoc smoke.md -s -o smoke.typ` then `typst.compile('smoke.typ', output='smoke.pdf')` failed with `typst.TypstError: font fallback list must not be empty`. Cause: pandoc's Typst template emits `font: ()` when no main font is set.
2. Fix: `pandoc smoke.md -s -V mainfont="Libertinus Serif" -o smoke.typ`; compilation succeeded. `pypdf` reported 1 page; the extracted text contained the heading, both equations and the table. A PNG render (`format='png'`) was inspected visually: title, section heading, inline equations and table rendered correctly, page number present.
3. `pandoc smoke.md -s -o smoke.tex` succeeded (LaTeX source only; not compiled).

Rule for all later PDF builds: pass `-V mainfont="Libertinus Serif"` (or another font bundled with typst) to pandoc.

## 4. Time and compute budget

- Five focused development days (planning estimate). Milestone efforts in `roadmap.md`.
- Compute: local laptop only. The model is a small discrete-event simulation; the full matrix (14,050 runs in the draft protocol) is expected to fit well inside the 2-hour cap, to be confirmed by the exploratory smoke timing in M2.
- Cost: zero. No paid API, dataset, compute or hosting.

## 5. Sources and licences

See `research/literature_review.md` and `data/manifest.json`. Draft protocol uses synthetic data only.

## 6. Scope, exclusions and fallback

- In scope: exponential and power-law forgetting, retrieval updates, five schedules, synthetic item difficulty, three experiments, a static demo, reports and one manuscript.
- Excluded: human data, user studies, real-world efficacy claims, any public dataset, any paid service, any publication without owner approval.
- Fallback if the demo stack is unavailable or over budget: a static HTML page with precomputed results and a minimal plain-JavaScript sandbox; if PDF generation fails, deliver Markdown sources plus build instructions and say that no PDF exists.

## 7. Feasibility risks

1. Adaptive scheduler with daily capacity and exact budget: rounding and tie rules must be specified and tested (risk of unfair comparisons).
2. Parameter values are assumptions; conclusions may be fragile (addressed by EXP-003, but only within ranges).
3. Owner freeze latency: confirmatory runs (M3) are blocked until the freeze.
4. Several literature sources verified only at metadata level; M1 must read them or drop them.
5. Demo stack (Node from another project's tools folder, read-only): installing npm packages needs a local `node_modules` inside this repository and network access to the npm registry (free); not tested in M0.
