<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# demo/: the MEMORY research page (M5)

A static page (TypeScript, React, Vite; versions pinned by `package-lock.json`, from the shared lab template). It shows:

- **Overview** with the status label: simulation study, preprint draft, not peer-reviewed.
- **Forgetting curves after the course**: mean modelled recall by retention interval for the five schedules, for any (model, budget, item distribution) cell of EXP-003, with greedy minus uniform and its unadjusted 95% interval.
- **Calendar comparison**: daily review load of each schedule at the EXP-001 setting, with each arm's measured mean recall and 95% interval.
- **Published results**: EXP-001, EXP-002, the not-run EXP-002 ω check, EXP-003, SENS-001 (exploratory) and CAL-002 (exploratory), each with its status, verdict, estimates, intervals and claim ids.
- **Assumptions**, **method and limitations**.
- **Playground** (sandbox): seed, scenario, model, budget, retention interval, items, learners; run, cancel, reset; forgetting curves over time and an item-by-day review calendar; JSON download of the sandbox output.

Measured results, sandbox output and assumptions carry distinct labels and are never mixed. Numbers come only from `public/data/results.json`, written by `scripts/export_demo_data.py` from committed results; every displayed estimate and interval is the manuscript's printed text (checked by `tests/test_demo_export.py`). If the file is missing or malformed, the page shows no numbers (fail closed).

**Sandbox fidelity.** `src/engine.ts` ports the Python engine. Given the same random numbers, it reproduces the Python traces: `src/engine.test.ts` compares review events exactly and every float within 1e-12 relative (1e-15 absolute) on a fixture from `scripts/export_engine_fixture.py`. The sandbox draws its own random numbers (mulberry32 and Box-Muller, not NumPy's PCG64), so a sandbox seed is not the research seed of the same number, and sandbox output is not a research result.

**Privacy.** No visitor input is collected or stored; nothing leaves the page; no font, script or image comes from another host.

## Design and third-party notes

The page has its own brand (owner request of 2026-11-26): index cards, a Leitner box and forgetting curves plotted on graph paper, in ink blue and graphite. The plan, palette, type, layout and motion rules are in `DESIGN.md`. The hero shows an illustration of a Leitner box, labelled on the page as an illustration and not study data; it contains no result.

Brand files are in `public/brand/`: the mark (`memory-mark.svg`, with one-colour and dark-background versions), the lockup and wordmark, `favicon.svg`, `favicon-32.png`, `apple-touch-icon.png` and the Open Graph image `og.png` (1200 by 630). The mark is drawn by hand as SVG paths; the wordmark outlines come from Courier Prime Bold, which the font licence permits.

Fonts, self-hosted from npm and bundled (nothing is fetched from another host). Revised on 2026-11-26 so that no lab demo shares a typeface:

- Courier Prime, package `@fontsource/courier-prime` version `5.3.0`, weights 400 and 700, Latin subset; Alan Dague-Greene; licence `OFL-1.1` (SIL Open Font License). Display only.
- Crimson Pro, package `@fontsource/crimson-pro` version `5.3.0`, weights 400, 600 and 400 italic, Latin subset; Jacques Le Bailly; licence `OFL-1.1` (SIL Open Font License). Body, tables and charts. It has no Greek glyphs; Greek letters fall back to a system serif.

## Commands

Node 22 on `PATH` (in the development workspace, the Node binary of the shared tools folder is used read-only).

    npm ci
    npm test                 # vitest
    npm run build            # writes dist/
    npm run preview          # serves dist/ on 127.0.0.1
    node tools/a11y_check.mjs dist --screenshots <dir>

Regenerate the data and the fixture from the repository root: `.venv/bin/python scripts/export_demo_data.py` and `.venv/bin/python scripts/export_engine_fixture.py`.

## Hosting

Demo URL: https://memory-spaced-repetition.kefimohamedbechir.workers.dev.

The built page (`dist/`) is hosted as Cloudflare Workers static assets on the free plan (owner, 2026-11-26, decision sheet, B2). `wrangler.jsonc` in this folder declares the assets only (no Worker script). The deploy is done by the lab coordinator, not by any script of this repository. The page loads nothing from another origin (checked by `tools/a11y_check.mjs`, "no foreign request").
