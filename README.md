<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# MEMORY: forgetting and learning schedules

**Question.** Which review schedule maximizes modelled delayed recall under a fixed study budget?

**Status: simulation study; M6 release candidate prepared (2026-11-25), awaiting the owner's review and any publication decision; independent research manuscript / preprint draft, not peer-reviewed.** The three frozen experiments (protocol v1.1, owner-approved 2026-11-24) ran in full: 18,550 runs, none excluded or failed. The owner approved the manuscript title and the funding, competing-interest and AI-use statements on 2026-11-25. Full-text owner review of the manuscript is still pending (`research/publication/author_review.md`). Simulated learners are not human participants: nothing here shows a human learning gain.

![Screenshot of the MEMORY research page: the question, the status line, three result cards (0.0162 with interval [0.0110, 0.0213]; 0.0085 with interval [-0.0026, 0.0195]; 70 of 72 cells) and the forgetting-curve chart of mean modelled recall by retention interval for five schedules.](docs/demo.png)

## Why it matters

Spaced-repetition tools decide when to review each item. Model-based schedulers review the items whose predicted recall is lowest, but a simulation that gives the scheduler the true memory model makes that comparison easy to win. MEMORY compares five schedules under an exactly matched review budget, then asks how much of the model-based advantage survives a wrong model and a sweep over other settings.

## Key findings (verified; numbers as printed in the manuscript)

- **EXP-001 (confirmatory).** At the central setting (exponential forgetting, test 281 days after a 28-day study window), an oracle greedy scheduler beat equal spacing by 0.0162 in mean modelled recall (95% bootstrap interval [0.0110, 0.0213]; 50 paired simulated learners). The effect is small, and mastery share moves the other way (-0.0200 [-0.0248, -0.0152]), so the conclusion is restricted to mean recall.
- **EXP-002 (confirmatory).** On power-law learners, greedy with the true model gained 0.0347 [0.0232, 0.0461]; with a misspecified exponential model it gained 0.0085 [-0.0026, 0.0195], which the frozen rule classifies as practically equivalent to uniform. The EXP-001 advantage is therefore declared dependent on model knowledge. Exploratory checks show the "equivalent" label is fragile; the stable finding is the drop of about three quarters.
- **EXP-003 (confirmatory run, descriptive).** Across 72 settings, the EXP-001 ranking changed in 70 cells; massed review was the most frequent best arm (29 cells), mostly under power-law forgetting and at a much higher daily load.
- **Not run.** The optional EXP-002 check with ω in {0.3, 3} had no frozen configuration and was not run (owner decision, D-017). Sensitivity to ω is untested.
- **Model validity (exploratory).** Neither forgetting model predicts held-out real first-review recall better than a constant (log-loss 0.328 for the constant, 0.549 for the best exponential curve, 0.428 for the best power-law curve). Every result is conditional on the assumed memory model.

## Experiments

| ID | Question | Status | Report |
|---|---|---|---|
| EXP-001 | Greedy (model-based) versus uniform under exponential forgetting, with expanding, Leitner and massed arms | confirmatory, complete (250 of 250 runs) | `research/experiments/EXP-001/report.md` |
| EXP-002 | Does the advantage survive a wrong model (power-law learners)? | confirmatory, complete (300 of 300 runs); ω check not run | `research/experiments/EXP-002/report.md` |
| EXP-003 | Rank stability across models, budgets, retention intervals and item distributions | confirmatory run of a descriptive experiment, complete (18,000 of 18,000 runs) | `research/experiments/EXP-003/report.md` |
| SENS-001 | Exploratory, post hoc robustness checks | exploratory | `research/paper/supplementary.md` section S4 |

## Research navigation

- Manuscript: `research/paper/manuscript.md` (canonical), supplement `research/paper/supplementary.md`. PDFs (built with the Typst toolchain and visually inspected at M6): `research/paper/manuscript.pdf`, `research/paper/supplementary.pdf`, `research/experiments/EXP-00N/report.pdf`.
- Protocols and freeze record: `research/protocol.md`, `research/experiments/EXP-00N/protocol.md`, `research/freeze.json`.
- Evidence: `research/claims_register.csv`, `research/publication/artifact_manifest.json`, `research/publication/evidence_audit.md`.
- Limitations: `research/limitations.md`. Decisions: `research/decision_log.md`.
- Interactive page: `demo/` (see below). Articles (drafts): `articles/medium.md`, `articles/linkedin.md`.

## Interactive page (demo)

A static page with the forgetting curves of the EXP-003 sweep, a calendar comparison of the schedules, every published result with its interval, the assumptions, the method and limitations, and a playground that runs a port of the engine in the browser (seed, scenario, reset). Measured results, sandbox output and assumptions are labelled separately. It runs offline after the first load and sends nothing anywhere. Demo URL: `<DEMO URL: unpublished>`.

Quick start (Node 22):

    cd demo && npm ci && npm run build && npm run preview

Checks: `npm test` (vitest: results validation and the engine port against a Python fixture) and `node tools/a11y_check.mjs dist` (offline, keyboard, contrast, mobile width, reduced motion). The page's data file is regenerated with `.venv/bin/python scripts/export_demo_data.py`.

## What is implemented

A Python package `memory_research` (`src/`): exponential and power-law forgetting, multiplicative retrieval updates, synthetic item difficulty with common random numbers, five schedules (uniform baseline, expanding, massed, Leitner, greedy with matched or misspecified model), run validation, versioned JSON results and run manifests, a report generator, the frozen analysis and a CLI. Tests in `tests/` (unit, property, hand-computed, differential and demo-consistency tests). The static page in `demo/` (TypeScript, React, Vite).

## Quick start and full reproduction

    uv sync --frozen
    uv run python -m memory_research test
    uv run python -m memory_research run --config research/experiments/EXP-001/config.json --report --pdf

Repeat the run for EXP-002 and EXP-003, then `scripts/analyse_confirmatory.py`; the exploratory checks run with `.venv/bin/python scripts/m4_sensitivity.py`. Details: `research/experiments/EXP-00N/reproduction.md`.

## Data sources and licences

The simulated items are synthetic. Two parameters (initial half-life 54.0 days and its spread 0.759) are calibrated to the public Duolingo spaced-repetition traces (Settles 2017, Harvard Dataverse, doi:10.7910/DVN/N8XJME, CC BY-NC 4.0), downloaded by `scripts/download_duolingo.py` and never committed. See `data/manifest.json`.

## Limitations

Recall is a model probability, not a human measurement; the models do not fit real first-review recall; the greedy arms know each item's true initial half-life; expanding and massed concentrate reviews on 4 days; α, β and ω are planning values. Full list: `research/limitations.md` and manuscript section 7.

## Licence

Source-available, non-commercial: MEMORY Source-Available Non-Commercial Research License v1.0 (`LicenseRef-MEMORY-NC-Research-1.0`). This is not an OSI-approved open-source licence. See `LICENSE` and `NOTICE.md`. Third-party material keeps its own terms.

## Citation

See `CITATION.cff`. Repository URL: `<REPOSITORY URL: unpublished>`. Affiliation: `<AFFILIATION: to be supplied or confirmed by the owner>`. There is no publication yet; the manuscript is a preprint draft, not peer-reviewed. An AI system (Claude, Anthropic) was used as a research and development assistant; it is not an author.
