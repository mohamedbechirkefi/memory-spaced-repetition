<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24, session 1: M0 bootstrap and feasibility (plus M1 drafts)

**Milestone:** M0. **Bounded task:** control files, feasibility audit, source and licence audit, draft protocol and experiment registry, dependency lock, local commit.

### Starting state

`git status`: `On branch main`, `nothing to commit, working tree clean`. One commit: `347f381 Initial commit: MEMORY master prompt and the owner's licence package (...)`. Files present: `master_prompt.md` (178 lines, unchanged), licence package, `.github/`, `.gitignore`.

### Commands and actual outputs

- Hardware and tools: see `research/feasibility.md` (CPU `Apple M1 Pro`, `10` cores, `17179869184` bytes RAM, macOS `15.3.1` build `24D70`, `129Gi` free; Python `3.12.1`; uv `0.9.5`; typst `0.15.0`; pypdf `6.20.0`; pillow `11.3.0`; pandoc `3.6.3`; Node `v22.23.3`; git `2.42.1`; `tex`, `pdflatex`, `xelatex`, `typst` CLI: not found).
- Toolchain smoke (exploratory, scratchpad only, not committed): first Typst compile failed with `typst.TypstError: font fallback list must not be empty`; succeeded after passing `-V mainfont="Libertinus Serif"` to pandoc; 1-page PDF, text and PNG render inspected. LaTeX output via pandoc succeeded.
- `pandoc research/paper/manuscript.md -s -o research/paper/manuscript.tex`: succeeded (119 lines; skeleton only; not compiled).
- `uv lock`: `Using CPython 3.12.1 interpreter at: /Library/Frameworks/Python.framework/Versions/3.12/bin/python3`, `Resolved 25 packages in 36ms`. Locked direct versions: numpy 2.5.4, jsonschema 4.26.0, matplotlib 3.11.2, pytest 9.2.0, hypothesis 6.170.15 (cutoff `exclude-newer = 2026-11-10T00:00:00Z`).
- `uv lock --check`: `Resolved 25 packages in 3ms` (lock consistent).
- Literature and datasets: WebSearch and WebFetch; details and verification levels in `research/literature_review.md`. PubMed, PMC and the Psychological Science publisher page could not be read (cookie wall, bot check, HTTP 403); Crossref returned HTTP 429 once and succeeded on retry.
- No test suite exists yet, so no tests were run and no test count is claimed. `uv sync` was not run (no code to test).

### Decisions

D-001 (owner's licence choice), D-002 (Typst toolchain), D-003 (synthetic data only), D-004 (protocol draft structure, not frozen), D-005 (two-week dependency cutoff). See `research/decision_log.md`.

### Files created or changed

Created: `CLAUDE.md`, `roadmap.md`, `progress.md`, `README.md`, `CITATION.cff`, `pyproject.toml`, `uv.lock`, `src/memory_research/__init__.py`, `src/README.md`, `tests/README.md`, `results/README.md`, `experiments/README.md`, `demo/README.md`, `articles/README.md`, `data/manifest.json`, `research/protocol.md`, `research/feasibility.md`, `research/literature_review.md`, `research/limitations.md`, `research/decision_log.md`, `research/claims_register.csv` (header only), `research/experiment_journal.jsonl` (empty: no experiment run), `research/experiment_registry.csv`, `research/experiments/EXP-001/protocol.md`, `research/experiments/EXP-002/protocol.md`, `research/experiments/EXP-003/protocol.md`, `research/paper/manuscript.md` (headings only), `research/paper/manuscript.tex` (generated), `research/paper/supplementary.md`, `research/paper/references.bib`, `research/paper/figures/README.md`, `research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}`.
Changed: `CONTRIBUTING.md` (development commands appended). Licence files untouched.

### Failures

- Typst compile without a main font (fixed as above).
- Several sources could be verified only at metadata level (Crossref); they are labelled and not cited for content.

### Outstanding risks

See `research/feasibility.md` section 7. Main ones: fairness rules of the adaptive arms (capacity and rounding), parameter values are assumptions, owner freeze latency.

### Decisions the owner must make

1. Approve or amend the draft protocol (question, H0/H1, `uniform` baseline, primary metric, arms, central parameters, 50 seeds, `δ = 0.02`) and freeze it (G-FREEZE).
2. Confirm the experiment scope: EXP-001 to EXP-003 as drafted, or cut EXP-003 levels or the EXP-002 `ω` check.
3. Confirm that no public dataset is used (DS01 CC BY-NC 4.0 is lawful for non-commercial research but unused; DS02 gated and non-redistributable, excluded).
4. Approve the toolchain decision D-002 (no TeX; Typst PDFs; LaTeX source generated only).
5. Approve the author metadata in `CITATION.cff` and `pyproject.toml` (name only, no affiliation).

### Next action

M1: read the metadata-only sources (Cepeda et al. 2008, Wixted and Ebbesen 1991, Averell and Heathcote 2011, Pavlik and Anderson 2005, Ye et al. 2022) or drop them; then M2 can start before the freeze: implement `uniform` and the exponential model first, with golden curve tests, and run the exploratory smoke matrix (seeds 1 to 5) to measure runtime and the spread of paired differences for the owner's sample-size decision.

## 2026-11-24, session 2: M2 core implementation (protocol not frozen)

**Milestone:** M2. **Bounded task:** engine, schedules, tests, schemas, manifests, CLI, report generator, exploratory smoke run; no confirmatory run.

### Starting state

`git status`: clean on `main` at `0f1a6af`. Protocol DRAFT v0.1, not frozen; registry hashes `none (not frozen)`.

### Commands and actual outputs

- `uv sync --frozen`: installed the locked environment into `.venv` (git-ignored). `uv lock` after the package version bump to 0.1.0: `Resolved 25 packages in 10ms`, `Updated memory-spaced-repetition v0.0.1 -> v0.1.0` (no dependency change).
- `uv run python -m pytest -q`: first run `1 failed, 182 passed` (a degenerate-case test expected an SD of exactly 0 for `[0.1, 0.1, 0.1]`; floating point gives 1.7e-17; test data changed to `0.25`). Second run `1 failed, 182 passed`: the differential test against the reference simulator found a relative difference of 1.46e-12 at a power-law probability near 5e-180 (log1p form versus direct power); tolerance set to 1e-9 relative, consistent with the stability test. Then `183 passed` on three consecutive runs, and `183 passed` before each commit.
- First `smoke --pdf`: Typst failed with `the document does not contain a bibliography` because pandoc read a table header `@50` as a citation; fixed (header renamed, pandoc `-citations`).
- Exploratory runs at clean revision `bad36ee` (2026-11-24T16:05:40Z to 16:06:01Z), reports regenerated by revision `13bb3d9`:
  - `smoke --pdf`: `SMOKE-001 [exploratory]: 25 runs, 25 ok, 0 excluded, 0 failed, wall clock 0.036 s`.
  - `run --config experiments/configs/probe_central.json --report --pdf`: `PROBE-001: 150 runs, 150 ok, ... wall clock 0.133 s`.
  - `probe_power.json`: `PROBE-002: 180 runs, 180 ok, ... wall clock 0.641 s`.
  - `probe_sweep.json`: `PROBE-003: 1350 runs, 1350 ok, ... wall clock 3.570 s` (an earlier run of the same matrix at `4dce703`, discarded because its provenance was marked dirty, took 1.142 s: machine-load variation).
  - `probe_floor.json`: `PROBE-004: 25 runs, 25 ok, ... wall clock 0.102 s`.
- `run --config research/experiments/EXP-00N/config.json` for N = 1, 2, 3: `refused: refusing confirmatory run of EXP-00N: research/protocol.md is marked NOT FROZEN; registry protocol_hash for EXP-00N is 'none (not frozen)', not a SHA-256`, exit status 3, no output written.
- PDFs: five reports generated (4, 4, 19, 2 and 4 pages); pages rendered to PNG and inspected; the provenance table overflowed the page and was changed to a list, then regenerated.

### Exploratory measurements (not findings)

- Runtime per run: mean 0.77 ms to 3.76 ms, median 0.72 ms to 0.92 ms, maximum 91 ms; peak resident memory at most 42.0 MiB.
- Projected full draft matrix (14,050 runs, plus 600 optional): about 12 s at the median, about 55 s at the slowest observed mean; the 2-hour cap is not binding.
- SD of paired differences versus `uniform`: 0.015 to 0.017 (PROBE-001, 30 seeds), 0.021 to 0.025 (PROBE-002); over the 216 sweep contrasts (5 seeds each) median 0.019, maximum 0.071. Under the draft rule (`s < 0.07`) 50 seeds suffice, but the spreads are compressed by the floor regime.
- Degenerate cases: the central setting is at the recall floor (baseline `R = 0.0295`, all arms below 0.10); 34 of 54 sweep cells have a baseline below 0.10; `greedy` and `leitner` leave most items never reviewed (35.7 and 31.0 of 50 on average). Details and proposals: `research/amendment_proposals.md` (AP-001 to AP-006).

### Decisions

D-006 (implementation choices), D-007 (exploratory planning runs), D-008 (amendment proposals, not applied).

### Files created or changed

Created: `src/memory_research/{models,config,items,schedules,simulate,metrics,reference,stats,schema,environment,guard,runner,report,cli,__main__}.py`, `tests/{conftest,test_models,test_config,test_schedules,test_simulate,test_stats,test_pipeline}.py`, `experiments/configs/{smoke,probe_central,probe_power,probe_sweep,probe_floor}.json`, `research/experiments/EXP-00{1,2,3}/{config.json,reproduction.md}` (drafts, refused while unfrozen), `research/amendment_proposals.md`, `results/exploratory/{SMOKE-001,PROBE-001..004}/` (results, manifests, reports, PDFs).
Changed: `src/memory_research/__init__.py`, `pyproject.toml` (version 0.1.0; pytest cache disabled), `uv.lock` (project version only), `roadmap.md`, `progress.md`, `CLAUDE.md` (commands section), `CONTRIBUTING.md` (commands appended), `README.md` (status), `src/`, `tests/`, `results/`, `experiments/` READMEs, `research/experiment_registry.csv` (statuses), `research/experiment_journal.jsonl`, `research/decision_log.md`, `research/publication/artifact_manifest.json`.

### Failures

As listed above (two test failures fixed in the tests, not the engine; one PDF build failure; one dirty-provenance rerun). No run failed or was excluded.

### Outstanding risks

- AP-002: the draft greedy rule is degenerate under the draft failure update; EXP-001 as drafted would test that pathology.
- The seed-spread estimate must be redone after any amendment to the central setting.
- Exploratory contrasts have been seen before the freeze (disclosed).

### Decisions the owner must make

1. AP-001 to AP-006 in `research/amendment_proposals.md` (central `h0` or regime; greedy rule or failure semantics; Leitner priority; seed count; EXP-003 `RI` handling).
2. Then the freeze of the (amended) protocol (G-FREEZE), and the earlier M0 decisions still open.

### Next action

Wait for the owner's decisions on AP-001 to AP-006. If amendments are accepted: update schedules, configs and tests, re-run the planning probes on seeds 1 to 30, then ask for the freeze. M3 stays blocked by G-FREEZE.

## 2026-11-24, session 3: real data, round-2 amendments and freeze (G-FREEZE, owner-approved)

**Milestone:** M1 freeze. **Bounded task:** DATA-FREEZE brief: licence check and download of DS01, ingestion, calibration method then fit, amendments A1 to A5, freeze record, records. No confirmatory run.

### Commands and actual outputs

- Dataverse API (`/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/N8XJME`): terms of use CC BY-NC 4.0; one file, id 3091087, 379,004,009 bytes, MD5 `0a1cae5eb7ad4b0bd9c0de91d74fcced`.
- `scripts/download_duolingo.py`: first attempt (urllib) failed, `HTTP Error 403: Forbidden` on the signed S3 redirect; switched to curl; second attempt verified size and MD5, SHA-256 `26cf9b33...076873`, accessed 2026-11-24T18:33:02Z.
- Commit `037b46e`: protocol section 15 (calibration method) and code, before any fit. Suite at that commit: `8 failed, 204 passed` before a test fix and the freeze record; the 8 were 6 freeze-dependent guard tests (no freeze record yet), 1 EXP-003 seed-block test (config not yet updated) and 1 MLE recovery test with uninformative delays (test data changed, not the estimator).
- `.venv/bin/python scripts/calibrate_duolingo.py` (at `037b46e`, clean): 12,854,226 rows, 0 excluded, 0 missing; subset 559,900 rows; split C 738 eligible lexemes, 1 boundary; `h0 = 54.0` days, `σ = 0.759`; split V `h0` +2.2%, `σ` -4.9%, not unstable; held-out log-loss 0.587 (curve) vs 0.328 (constant). 38.5 s.
- `run --config experiments/configs/probe_baseline_fitted.json --out results/exploratory/PROBE-005` (uniform arm only): `60 runs, 60 ok, 0 excluded, 0 failed, wall clock 0.060 s`; mean `R` 0.959 (exponential), 0.810 (power law).
- `uv lock`: `Updated memory-spaced-repetition v0.1.0 -> v0.2.0`. `uv sync --frozen --all-groups --all-extras`, then `.venv/bin/python -m pytest -q`: `212 passed` (twice).
- Guard: `freeze_status` is frozen for the three committed configurations and refuses each with a changed seed count or `h0` ("differs from the frozen configuration"); CLI exit 3 on a changed configuration (tested). No confirmatory matrix was run; `results/confirmatory/` does not exist.

### Decisions

D-009 (DS01 adopted, licence check), D-010 (amendments and fit), D-011 (freeze).

### Commits

`037b46e` (method before fit), `6a8bc29` (frozen content), and the freeze-record commit that contains this entry.

### Outstanding risks

- The fitted setting is near the ceiling for exponential learners (baseline 0.959), so EXP-001 differences are compressed (disclosed).
- The exponential curve misfits real first-review recall (held-out log-loss worse than a constant; disclosed).
- "Cover every item" read as at-least-once coverage (D-010); the owner may revisit.

### Next action

M3, when the coordinator schedules it on a quiet machine: `uv run python -m memory_research run --config research/experiments/EXP-00N/config.json --report --pdf` for N = 1, 2, 3.

## 2026-11-24, session 4: round-3 recalibration and re-freeze v1.1 (owner-approved)

**Milestone:** M1 (re-freeze). **Bounded task:** ROUND3 brief: owner rules (a), (b), (c) of `labs/_shared/owner-approvals-2026-11-24c.md` section 2, in that order; baseline arm only; no confirmatory run.

### Commands and actual outputs

- Rule (a). Protocol 16.1 and code (`duolingo.compare_models`, `scripts/diagnose_forgetting_fit.py`, 5 tests) committed at `664de3c` before computing; suite there `214 passed, 3 failed` (the 3 guard-accepts tests, protocol under amendment). `.venv/bin/python scripts/diagnose_forgetting_fit.py` (clean, `664de3c`): held-out log-loss constant 0.328, exp-median 0.587 (equals CAL-001), exp-population 0.549, exp-mle 0.569, power-median 0.473, power-population 0.476, power-mle 0.428; `neither_beats_constant: true`. 0.87 s.
- Rule (b). Protocol 16.2 and code (`memory_research.design`, `scripts/select_retention_interval.py`, 3 tests) committed at `8d4854a` before applying; suite `217 passed, 3 failed` (same 3). `.venv/bin/python scripts/select_retention_interval.py` (clean, `8d4854a`): uniform only, seeds 1 to 30; candidates in range 142 to 365; chosen `RI = 281`, baseline `R` 0.5497; monotone; power-law baseline 0.6805; `R` at 7 equals PROBE-005 (0.959).
- `.venv/bin/python -m memory_research run --config experiments/configs/probe_baseline_ri281.json --out results/exploratory/PROBE-006` (clean, `39399c5`): `60 runs, 60 ok, 0 excluded, 0 failed, wall clock 0.054 s`; means 0.5497 (exponential), 0.6805 (power).
- Rule (c). Content v1.1 committed at `dcdaf2e` (suite `219 passed, 3 failed`, the 3 guard-accepts tests before the record). Freeze record v1.1 written; `.venv/bin/python -m pytest -q`: `222 passed`.
- Guard: `freeze_status` frozen for the three v1.1 configurations; the v1.0 configurations from `6a8bc29` refused by the CLI (`refused: ... differs from the frozen configuration`, exit 3, no output written).

### Decisions

D-012 (misfit diagnosis), D-013 (RI 281; EXP-003 fourth level, revertible by the owner), D-014 (re-freeze v1.1).

### Files created or changed

Created: `src/memory_research/design.py`, `scripts/diagnose_forgetting_fit.py`, `scripts/select_retention_interval.py`, `tests/test_design.py`, `experiments/configs/probe_baseline_ri281.json`, `results/exploratory/{CAL-002,RI-001,PROBE-006}/`. Changed: `src/memory_research/duolingo.py`, `tests/test_duolingo.py`, `tests/test_pipeline.py`, `research/protocol.md` (section 16, status), EXP-001 to EXP-003 protocols and configurations, `research/freeze.json`, `research/experiment_registry.csv`, `research/experiment_journal.jsonl` (CAL-002, RI-001, PROBE-006), `research/limitations.md`, `research/decision_log.md`, `roadmap.md`, `README.md`, `research/paper/manuscript.md` (status line).

### Failures and risks

- No run failed. `research/paper/manuscript.tex` is stale relative to `manuscript.md` (since M0; not regenerated this session).
- The central cell now describes retention 281 days after a 28-day course; the seed-spread estimate was not re-measured (needs a contrast).
- Results are model-dependent (CAL-002).

### Next action

M3 when the coordinator schedules it: `uv run python -m memory_research run --config research/experiments/EXP-00N/config.json --report --pdf` for N = 1, 2, 3 (EXP-003 now 18,000 runs).

## 2026-11-25, session 5: M3 confirmatory runs (owner: "Start next")

**Milestone:** M3. **Bounded task:** `labs/_shared/M3-brief.md`: pre-run checks, smoke and metric validation, the three frozen matrices, analysis, records. No push.

### Commands and actual outputs

- Pre-run: tree clean at `e7d4ab2`; SHA-256 of `research/protocol.md`, the three experiment protocols, the three configurations and `data/manifest.json` all equal `research/freeze.json`. `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`: `Audited 24 packages`. `.venv/bin/python -m pytest -q`: `222 passed`. The package imports from this repository's `src/`. DS01 present, SHA-256 `26cf9b33...076873` equals the manifest.
- Pre-run code (`6bde8ef`, D-015): `frozen_analysis.py`, `scripts/analyse_confirmatory.py`, `scripts/validate_metrics.py`, per-run `start_utc`/`end_utc`, data manifest hash in the environment, figure labels by result kind, 12 new tests. Suite: `234 passed`.
- `.venv/bin/python scripts/validate_metrics.py`: `METRICVAL-001: 38 checks, 0 failed`.
- `.venv/bin/python -m memory_research smoke`: 25 runs ok; it overwrote the committed SMOKE-001 output, which was copied to `results/exploratory/SMOKE-001-M3/` and restored (D-016). `run --config experiments/configs/smoke_v11.json --report`: `SMOKE-002 [exploratory]: 25 runs, 25 ok, 0 excluded, 0 failed, wall clock 0.037 s`.
- Rehearsals (exploratory seeds, at clean `d4a793d`): PROBE-007 25 runs, PROBE-008 30 runs, PROBE-009 1,800 runs, all ok; the frozen analysis ran end to end on each.
- Confirmatory at clean `d4a793d`, `nice -n 10 .venv/bin/python -m memory_research run --config research/experiments/EXP-00N/config.json --report --pdf`:
  - `EXP-001 [confirmatory]: 250 runs, 250 ok, 0 excluded, 0 failed, wall clock 0.603 s` (exit 0)
  - `EXP-002 [confirmatory]: 300 runs, 300 ok, 0 excluded, 0 failed, wall clock 0.907 s` (exit 0)
  - `EXP-003 [confirmatory]: 18000 runs, 18000 ok, 0 excluded, 0 failed, wall clock 36.063 s` (exit 0)
  - Process wall clock 2026-11-24T23:36:11Z to 23:37:32Z UTC (including report and PDF generation).
- `scripts/analyse_confirmatory.py` for each experiment (EXP-002 and EXP-003 read the EXP-001 analysis). Rerun at `3811bb9` after a figure-layout fix; all analysis values identical (D-016). A second execution of EXP-001 to a scratch directory reproduced every per-run metric exactly.
- `scripts/build_experiment_records.py`: `research/experiments/EXP-00N/{results_tables.md, metrics.csv, figures/}`.

### Results (frozen rules)

- EXP-001 primary greedy minus uniform +0.0162, 95% bootstrap CI [0.0110, 0.0213]: above zero, directional prediction supported; mastery share reverses sign, so restricted to mean recall.
- EXP-002: greedy-power +0.0347 [0.0232, 0.0461] (H0a rejected); greedy-exp +0.0085 [-0.0026, 0.0195] (H0b not rejected, within ±0.02): the EXP-001 advantage is declared dependent on model knowledge.
- EXP-003 (descriptive): 70 of 72 cells with a pairwise rank reversal against EXP-001; E1 13 of 18, E2 16 of 24.

### Failures and deviations

No run failed or was excluded. No deviation from the frozen matrices. EXP-002 `ω` check not run (no frozen configuration). The 11.3 narrative reports were not written: the file tool refused report files in this session (D-016).

### Files created or changed

Created: `src/memory_research/frozen_analysis.py`, `scripts/{analyse_confirmatory,validate_metrics,build_experiment_records}.py`, `tests/test_frozen_analysis.py`, `experiments/configs/{smoke_v11,rehearsal_exp001,rehearsal_exp002,rehearsal_exp003}.json`, `results/confirmatory/`, `results/exploratory/{METRICVAL-001,SMOKE-001-M3,SMOKE-002,PROBE-007,PROBE-008,PROBE-009}/`, `research/experiments/EXP-00N/{results_tables.md,metrics.csv,figures/}`. Changed: `runner.py`, `environment.py`, `schema.py`, `report.py`, `.gitignore`, registry, journal, claims register, limitations, decision log, roadmap.

### Next action

Write the three 11.3 narrative reports from the generated tables, then M4 (evidence audit, second review pass, manuscript synthesis).

## 2026-11-25, session 5b: M3 close brief (owner decisions of 2026-11-25)

- Recorded the owner's decisions ("approve all recommendations, RIGGED A", items 4 and 6) as D-017, and updated the limitations, the registry and `research/freeze.json` (`post_freeze_record.not_run`: the EXP-002 `ω` check). The claims register needed no change.
- Item 4: the Write tool again refused `research/experiments/EXP-001/report.md` ("Subagents should return findings as text, not write report files"). As the close brief requires, the session stopped the report work without a workaround. The three narrative reports and the `reproduction.md` updates remain unwritten.
- M3 status: **in progress, not done.** The matrices are complete with no dropped runs, but the reports are missing.
- Guard still accepts the frozen configurations (the freeze record's hashed fields are unchanged).

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 3 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.

## 2026-11-25, session 6: M4 interpretation, evidence audit and manuscript (owner: "Approve all recommendations, push then next")

**Milestone:** M4. **Bounded task:** `labs/_shared/M4-brief.md`. The project-specific follow-ups of `owner-approvals-2026-11-25b.md` concern HOUSE, RIGGED and FLOW only; none applies to MEMORY. No push.

### Commands and actual outputs

- `git status`: clean at `e4f9dae`. Raw `results.json` SHA-256 of EXP-001, EXP-002 and EXP-003 equal their `SHA256SUMS` entries (EXP-003 file present locally, git-ignored).
- `scripts/m4_sensitivity.py` committed at `2e8cf05` before running; `nice -n 10 .venv/bin/python scripts/m4_sensitivity.py`: `SENS-001 [exploratory]: wrote .../results/exploratory/SENS-001/sensitivity.json in 2.5 s` (clean revision, one process). Journal entry SENS-001.
- `.venv/bin/python scripts/audit_numbers.py` (final run): manuscript 216 numbers, supplementary 216, EXP-001 report 122, EXP-002 report 130, EXP-003 report 25, claims register 86; `AUDIT: 0 unmatched`. Before the corrections and script fixes, the first runs flagged section numbers, arXiv ids and the claims register's section column (classification fixes in the script, not number changes).
- Targeted recomputation from `frozen_analysis.json`: 13 cells with greedy minus uniform below 0 are 10 power-law and 3 exponential (the EXP-003 report said 9 power-law); ties in 3 cells; E1 and E2 failure lists; manuscript Tables 1 to 3 compared programmatically with the frozen analyses (`bad 0`).
- Figures cited by the manuscript compared byte for byte with the analysis copies: identical.
- `pandoc manuscript.md -s -t latex` (3.6.3) regenerated `research/paper/manuscript.tex` (1,059 lines with header). No PDF built (M6).
- `.venv/bin/python -m pytest -q`: `234 passed in 2.49s`.

### Results (exploratory, post hoc; no frozen verdict changed)

- EXP-001 primary replicates on independent seeds (C044 0.0167 [0.0113, 0.0218]; SENS-001 0.0193 [0.0147, 0.0236]) and holds at RI 1, 7, 30; greedy reallocates reviews to hard items (5.326 against 2.714) without later placement.
- EXP-002 "equivalent within 0.02" is fragile: paired t upper bound 0.0201; independent seeds 0.0098 [0.0007, 0.0187]; RI 7 and 30: 0.0213 with intervals above 0. Verdict kept, reading restated quantitatively.
- EXP-003 instability robust: 70 of 72 resolved reversals, 54 of 56 without ceiling cells; top arm resolved in 59 cells.

### Failures and deviations

None. No confirmatory rerun; no frozen protocol, configuration or seed changed.

### Files created or changed

Created: `scripts/m4_sensitivity.py`, `scripts/audit_numbers.py`, `results/exploratory/SENS-001/sensitivity.json`, `research/publication/{evidence_audit.md, number_audit.json, review_pass_2.md}`. Changed: `research/paper/{manuscript.md, manuscript.tex, supplementary.md}`, the three `report.md` (M4 final, corrections and addenda), `research/claims_register.csv` (restructured), `research/publication/{artifact_manifest.json, claims_audit.md}`, `research/{limitations.md, decision_log.md (D-018), experiment_journal.jsonl, experiment_registry.csv}`, `roadmap.md`.

### M4 gate

Every numerical claim maps to a result id, configuration hash and figure or table (claims register, artifact manifest, number audit); every external claim maps to a source read at the stated level (abstract-only sources marked). **M4 done.**

### Risks and next action

Open: the initial half-life advantage of both greedy arms; the untested `ω` sensitivity (D-017). Next: M5 (static interactive page using the same verified results and labels).


## 2026-11-25: post-M4 owner decisions (statements)

**Starting state:** `d191875`, working tree clean. Authority: owner, 2026-11-25, "Approve all" (post-M4) (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25c.md`, item 2; coordinator brief `/Users/bechir/research/labs/_shared/POST-M4-brief.md`, item 2 only).

- Item 2: the funding, competing-interest and AI-use wording in manuscript section 11 is recorded as owner-approved (D-019). No wording changed.
- No frozen protocol, config, seed or result changed. No computation. No manuscript rebuild (the manuscript text did not change).

### Owner placeholders for M5

1. Manuscript section 10: "at a URL to be added on release (`<REPOSITORY URL: unpublished>`)". Only the owner can supply the repository URL, at a release decision (G-PUBLIC).

Section 11 (funding, competing interests, AI assistance) contains no placeholder. `research/publication/author_review.md` still has the box "Authorship and metadata approved by the owner" unticked.

### Tests

`.venv/bin/python -m pytest -q`: 234 passed in 2.66s (after the changes; src/ and tests/ unchanged).

### Next action

M5, with the placeholders above put to the owner.

## 2026-11-25, session 7: M5 interactive page (owner: "Next")

**Milestone:** M5. **Bounded task:** `labs/_shared/M5-brief.md`. Authority: owner, 2026-11-25, "Next" (`labs/_shared/owner-approvals-2026-11-25d.md`; stack: TypeScript, React and Vite from the shared template). No push.

### Starting state

`git status`: clean at `5cbef23` on `main`. `demo/` held only its README.

### Commands and actual outputs

- Template copied into `demo/` without `node_modules` (rsync), `.npmrc` kept; `npm ci --prefer-offline` (Node v22.23.3 from helix/.tools, npm cache in the session scratchpad): `added 53 packages`. No version changed, no dependency added.
- `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`: `Audited 24 packages`. Baseline `.venv/bin/python -m pytest -q`: `234 passed`.
- `.venv/bin/python scripts/export_demo_data.py`: `wrote demo/public/data/results.json`; `--check`: `EXPORT-CHECK PASS`.
- `.venv/bin/python scripts/export_engine_fixture.py`: `wrote demo/src/fixtures/engine_fixture.json (204070 bytes)`, 0.115 s wall clock; `--check`: `FIXTURE-CHECK PASS`.
- `.venv/bin/python -m pytest -q` (final): `253 passed in 2.58s` (234 earlier tests plus 19 in `tests/test_demo_export.py`).
- `npm test` (final): `Test Files  2 passed (2)`, `Tests  43 passed (43)` (18 results-validation tests, 25 engine-port tests).
- `npm run build` (final): `tsc --noEmit && vite build`, `✓ built`; `dist/assets/index-*.js` 259.88 kB, worker 6.61 kB, CSS 7.07 kB.
- `node tools/a11y_check.mjs dist --screenshots <scratchpad>/memory/shots` (final), full output:

```
PASS results render (no fail-closed panel): 6 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 29 reached of 29
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs: Sandbox output (seed 1, 20 sandbox learners, exponential forgetting, k = 4, RI 2
A11Y-CHECK PASS
```

- Earlier checker runs failed and were fixed (D-020): first run `FAIL text contrast, light scheme` (sandbox background in `color-mix`), `FAIL keyboard reaches every focusable element: 23 reached of 30` (duplicate keys), `FAIL no horizontal page scroll at 360 px: overflow 204px` (scenario select); second run `29 reached of 30` (a focusable table inside a closed `details`).
- Screenshots inspected with the Read tool: desktop light, desktop dark, mobile light (checker), plus the playground after a run in light, dark and 360 px (scratchpad script). Fixed after inspection: wrapped interval columns (now no-wrap), unreadable chart text at 360 px (narrow drawings), estimate tables at 360 px (stacked rows), the "Verdict under the frozen rule" label on exploratory and descriptive entries (now labelled by kind).
- `docs/demo.png`: 780 x 1200, 86,293 bytes, from the desktop-light screenshot.
- `grep -rn REPLACE demo/ --exclude-dir=node_modules`: no output.

### Results

No new result. The page shows only committed results; the sandbox is a browser port of the engine (exact on identical random numbers, own random generator; D-020).

### Files created or changed

Created: `demo/` (template files with the MEMORY SPDX header; `src/{engine.ts, engine.test.ts, charts.tsx, Published.tsx, fixtures/engine_fixture.json}`; rewritten `src/{App.tsx, Sandbox.tsx, sandbox.worker.ts, results.ts, results.test.ts, style.css}`; `public/data/results.json`), `scripts/export_demo_data.py`, `scripts/export_engine_fixture.py`, `tests/test_demo_export.py`, `docs/demo.png`, `articles/medium.md`, `articles/linkedin.md`. Changed: `README.md`, `CITATION.cff`, `demo/README.md`, `articles/README.md`, `CONTRIBUTING.md` (commands appended), `roadmap.md`, `research/decision_log.md` (D-020), `progress.md`.

### M5 gate

Offline after the first load (checker step 7), responsive (no horizontal scroll at 360 px; screenshots), keyboard usable (29 of 29 focusable elements reached with a visible outline), no fabricated data (every number from `results.json`, which a test ties to the manuscript and the generated tables), no runtime service (static files; no foreign request). **M5 done.**

### Owner placeholders that remain

1. `<REPOSITORY URL: unpublished>`: manuscript section 10, README, `CITATION.cff` comment, articles.
2. `<DEMO URL: unpublished>`: README, articles, `demo/README.md`.
3. `<AFFILIATION: to be supplied or confirmed by the owner>`: README, `CITATION.cff` comment; Medium byline `<AUTHOR LINE AND AFFILIATION: to be confirmed by the owner>`.
4. `research/publication/author_review.md`: all boxes unticked (owner only).

### Risks and next action

- The sandbox seed does not reproduce a research seed (different random generator); stated on the page.
- The articles are drafts the owner has not yet read; publication is the owner's decision.
- Next: M6 (clean clone, PDFs, link checks, owner review checklist).

## 2026-11-25, session 8: M6 release candidate (owner: "Next", second)

**Milestone:** M6. **Bounded task:** `labs/_shared/M6-brief.md`. Authority: owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`). No push, tag or release.

### Starting state

`git status`: clean at `46b4a11` on `main`.

### Commands and actual outputs

- Clean clone of `46b4a11` in the session scratchpad: `uv sync --frozen --all-groups --all-extras` ok; `.venv/bin/python -m pytest -q`: `253 passed in 38.38s`.
- `memory_research smoke --out <scratch>/smoke`: refused (`exploratory outputs must go under a path containing 'exploratory'`); with `--out <scratch>/exploratory/SMOKE-001`: `SMOKE-001 [exploratory]: 25 runs, 25 ok, 0 excluded, 0 failed, wall clock 0.034 s`; against `results/exploratory/SMOKE-001-M3`: only timing and provenance leaves differ (103), `summary.csv` and `contrasts.csv` byte-identical.
- `memory_research run --config research/experiments/EXP-001/config.json --out <scratch>/rerun-exp001`: `250 runs, 250 ok, 0 excluded, 0 failed, wall clock 0.288 s`; against the committed `results.json`: 1,003 differing leaves, all timing or provenance; every metric identical. Output discarded (reproducibility check, not a result).
- Demo in the clone: `npm ci --prefer-offline` `added 53 packages`; `npm test` `Tests 43 passed (43)`; `npm run build` `✓ built`; `node tools/a11y_check.mjs dist` `A11Y-CHECK PASS`. `scripts/export_demo_data.py` then `--check`: `EXPORT-CHECK PASS`; `export_engine_fixture.py --check`: `FIXTURE-CHECK PASS`; `git status` empty.
- PDFs: first build failed: `typst.TypstError: path "../experiments/EXP-001/figures/exp001_contrasts.svg" would escape the project root` (finding R1). After the builder fixes (R1 to R7 in `research/publication/reproducibility_report.md`): manuscript 15 pages (370,351 bytes), supplement 5 (138,304), EXP-001 7 (175,739), EXP-002 7 (189,070), EXP-003 10 (402,401). Pages rendered to PNG at 80 ppi and read: all manuscript and supplement pages, report pages 1 to 6, 1 to 6 and 1 to 8. pypdf: every PDF titled; 0 e-mail addresses, 0 local paths, 0 raw Markdown in text or metadata.
- Sources: ACL Anthology PDF (Settles and Meeder), arXiv PDFs (Tabibian et al. 1712.01856v2; Reddy et al. 1602.07032) and the eScholarship author manuscript (Cepeda et al.) opened; every cited statement matches (evidence audit section 6).
- `pandoc manuscript.md -s -t latex` regenerated `manuscript.tex` (1,063 lines with header).
- `.venv/bin/python scripts/audit_numbers.py`: manuscript 220 numbers, supplementary 216, EXP-001 122, EXP-002 130, EXP-003 25, claims register 88; `AUDIT: 0 unmatched`.
- `.venv/bin/python scripts/check_links.py`: `57 Markdown files, 33 relative links checked, 0 broken`, `LINK-CHECK PASS`.
- Data: DS01 SHA-256, MD5 and size equal to `data/manifest.json`; `shasum -a 256 -c SHA256SUMS`: 18, 18 and 22 OK; 40 artifact-manifest paths exist.
- Scan of 304 tracked text files: 1 e-mail (AI co-author trailer in `CLAUDE.md`), 0 keys or tokens, 0 `.env`, 18 home-path lines in 6 files (3 removed from current files; the rest listed in the reproducibility report and D-021).
- Licences: `research/publication/dependency_licences.md`, 23 Python and 84 npm packages, none flagged.
- `CITATION.cff` validated against the official CFF 1.2.0 schema (fetched to the scratchpad; `jsonschema` in a throwaway uv environment): `errors 0`.
- `.venv/bin/python -m pytest -q` (working repository, final): `256 passed`; first run failed one test (`test_committed_export_is_identical`: the export records the claims register hash, which changed), fixed by rerunning `scripts/export_demo_data.py`. Demo: `npm test` `Tests 43 passed (43)`, `npm run build` ok, `A11Y-CHECK PASS`.

### Files created or changed

Created: `scripts/check_links.py`, `tests/test_links.py`, `research/publication/dependency_licences.md`, the five PDFs. Changed: `src/memory_research/report.py` (builder), `research/paper/{manuscript.md, manuscript.tex, supplementary.md, references.bib}`, the three `report.md` (blank lines before lists; two figure heights), `research/literature_review.md`, `research/claims_register.csv` (EXT-003, EXT-004 status), `research/publication/{reproducibility_report.md, evidence_audit.md, author_review.md, release_checklist.md, number_audit.json}`, `demo/public/data/results.json` (claims register hash), `demo/README.md`, `README.md`, `CITATION.cff`, `CONTRIBUTING.md` (commands appended), `roadmap.md`, `research/decision_log.md` (D-021).

### Note on home paths in this journal

Line 258 of this file (post-M4 entry) contains an absolute home-directory path. It is left as written (append-only); see D-021.

### M6 status

Release candidate prepared, awaiting owner review and G-PUBLIC. M6 is not done until the owner signs off `research/publication/author_review.md`.

### Second clean clone (after `ac66801`)

Fresh clone of `ac66801`: `uv sync --frozen` ok; `pytest -q` `256 passed in 8.50s`; smoke `25 runs, 25 ok`, tables identical to `SMOKE-001-M3`; `LINK-CHECK PASS`; `AUDIT: 0 unmatched`; demo `Tests 43 passed (43)`, build ok, `A11Y-CHECK PASS`; export and fixture checks pass and `git status` stays clean; the five PDFs rebuild with the same page counts and sizes (only timestamps differ). Clone deleted. Recorded in `research/publication/reproducibility_report.md` section 6. Tests in the working repository after this entry: see the commit below.

### Next action

The owner reads `research/publication/author_review.md` (section "Prepared for the owner") and decides on sign-off and any publication (G-PUBLIC).

## 2026-11-26, session 9: owner answers of 2026-11-26 applied

**Bounded task:** `labs/_shared/OWNER-ANSWERS-brief.md`. Authority: owner, 2026-11-26, decision sheet (D-022). Wording and configuration only; no push, deploy, tag or release; no `author_review.md` box ticked.

### Starting state

`git status`: clean at `0c9bde0` on `main`.

### Commands and actual outputs

- Placeholder scan of tracked text files (excluding append-only logs): 10 placeholder lines in `CITATION.cff`, `README.md`, both articles, `demo/README.md`, `research/paper/manuscript.md` (and its generated `manuscript.tex`); all filled. After the edits: 0 `<REPOSITORY URL`, `<DEMO URL`, `<AFFILIATION` or `<AUTHOR LINE` outside append-only logs.
- Home-path scan (`git ls-files | xargs grep -n "/Users/"`): 14 lines before, 4 after (`progress.md` line 258; `research/decision_log.md` lines 17, 154, 161; append-only). `../.tools/py/bin/uv --version` from the repository root: `uv 0.9.5 (d5f39331a 2025-10-21)`.
- `pandoc manuscript.md -s -t latex` with the two header lines: diff against the previous `manuscript.tex` limited to `pdfauthor`, `\author` and section 10.
- `build_pdf` on the manuscript, supplement and three reports: pages 15, 5, 7, 7, 10 (unchanged); 369,428, 138,320, 175,751, 189,086, 402,413 bytes. PNG at 80 ppi inspected: manuscript pages 1 and 15, supplement page 1, report pages 1 (author line, sections 10 and 11). pypdf: manuscript author metadata "Mohamed Bechir Kefi, independent researcher"; 0 local paths. Intermediate `.typ` files moved to the session scratchpad.
- `.venv/bin/python -m pytest -q`: `256 passed in 3.07s` (the URL test in `tests/test_demo_export.py` now requires the public addresses).
- `scripts/export_demo_data.py`: `wrote demo/public/data/results.json (84389 bytes)`, `--check` `EXPORT-CHECK PASS`; `export_engine_fixture.py --check` `FIXTURE-CHECK PASS`; `results.json` unchanged.
- Demo (Node from the helix tools folder, npm cache in the session scratchpad): `npm test` `Tests 43 passed (43)`; `npm run build` `✓ built in 150ms`; `node tools/a11y_check.mjs dist`: nine `PASS` lines including "no request leaves the local origin", `A11Y-CHECK PASS`. No `http` address in `dist/index.html` or the CSS.

### Files changed

`CITATION.cff`, `CLAUDE.md`, `README.md`, `articles/{README.md, medium.md, linkedin.md}`, `demo/README.md`, `demo/src/App.tsx` (footer author line), `demo/wrangler.jsonc` (new), `research/paper/{manuscript.md, manuscript.tex, manuscript.pdf, supplementary.md, supplementary.pdf}`, `research/experiments/EXP-00{1,2,3}/{report.md, report.pdf}` (Author line only), `research/feasibility.md`, `research/publication/{author_review.md, release_checklist.md, reproducibility_report.md}`, `roadmap.md`, `research/decision_log.md` (D-022), `tests/test_demo_export.py`.

### Next action

The owner: B15 (article drafts), B16 (full-text review and sign-off of `research/publication/author_review.md`), B18 (release). The coordinator deploys `demo/dist` with `demo/wrangler.jsonc` and pushes.

## 2026-11-26, session 10: demo brand identity, motion and UI redesign

**Bounded task:** `labs/_shared/DEMO-BRAND-brief.md` for MEMORY (owner request of 2026-11-26, D-023). Demo only; no result, data, fixture or test changed.

### Commands and actual outputs

- Fonts: `npm_config_before=2026-11-12 npm install --save-exact @fontsource/zilla-slab@5.3.0 @fontsource/alegreya-sans@5.3.0` (npm cache in the session scratchpad): `added 2 packages`. Both `OFL-1.1` per `npm view`.
- Logo: generated as SVG paths by a scratchpad script (hand-built mark; wordmark outlines from Zilla Slab 600 via fontTools). `svg_audit.py` on the nine SVGs: 0 FAIL; warnings are near-miss angles of curve end cuts and of the type, and the deliberate paper curve on the favicon tile. `render_png.py` (Chrome backend): `favicon-32.png` 32x32, `apple-touch-icon.png` 180x180. Open Graph image rendered from an HTML page with Chrome headless: `og.png` 1200x630, 74,210 bytes.
- `npm test`: `Tests 43 passed (43)`. `npm run build`: `✓ built in 122ms`; JS 266.23 kB (gzip 82.54 kB), CSS about 18 kB. `dist/` total 784,375 bytes on disk (it carries woff and woff2 for each face; browsers fetch only woff2).
- `node tools/a11y_check.mjs dist`: nine `PASS` lines (contrast light and dark, 38 of 38 focusable reached, visible focus, no overflow at 360 px, reduced motion 0 running, no foreign request, offline sandbox run), `A11Y-CHECK PASS`.
- Screenshots: built folder served with `python3 -m http.server 5222 --bind 127.0.0.1` (stopped afterwards); Chrome headless desktop 1440 px full page and phone 390 px (iframe wrapper), with `--virtual-time-budget`; two critique passes. Changes from the critique: ruled lines of the overview cards aligned to the text lines; repeated question in the overview turned into a "precisely" note; direct chart labels moved clear of the markers; graph-paper grid lightened and removed from the calendar; red rule on the hero answer removed (one accessory too many); on phones the illustration tag moved above the drawing, interval captions hidden and labels enlarged, the nav row fades at its right edge.
- `.venv/bin/python -m pytest -q`: `256 passed in 2.71s` (includes the demo README number and URL tests).

### Files changed

`demo/DESIGN.md` (new), `demo/README.md` (design and third-party notes), `demo/index.html` (description, theme colour, icons, Open Graph), `demo/package.json`, `demo/package-lock.json`, `demo/public/brand/` (new), `demo/src/{App.tsx, Hero.tsx (new), ui.tsx (new), Published.tsx, charts.tsx, Sandbox.tsx, main.tsx, style.css}`, `research/decision_log.md` (D-023), `progress.md`.

### Next action

The coordinator rebuilds and deploys `demo/dist` when the owner agrees; nothing pushed or deployed here.

## 2026-11-26, session 11: unique typeface pair for the demo

**Bounded task:** `labs/_shared/FONT-UNIQUE-brief.md`, MEMORY row (owner request of 2026-11-26: no typeface shared between lab demos; Zilla Slab stays with PARADOX, Alegreya Sans with EVOLVE). Demo only; no number, data, fixture, test or wording of a scientific statement changed.

### Commands and actual outputs

- `npm uninstall @fontsource/zilla-slab @fontsource/alegreya-sans`: `removed 2 packages`. `npm_config_before=2026-11-12 npm install --save-exact @fontsource/courier-prime@5.3.0 @fontsource/crimson-pro@5.3.0`: `added 2 packages`; both `OFL-1.1` per `npm view`; `package.json` pins `5.3.0` exactly.
- Glyph check with fontTools: Crimson Pro (Latin subset, no Greek subset published) lacks ω, σ, α, β, Δ; they fall back to Georgia or Times New Roman (recorded in `demo/DESIGN.md` and `demo/README.md`). Crimson Pro has `tnum`; Courier Prime is monospaced. Courier Prime is kept to display sizes (headings, wordmark, tabs, card figures, box labels, Run button) so it does not read as monospace data labels; tables, chart text and status labels are Crimson Pro.
- Wordmark and lockups redrawn from Courier Prime Bold outlines (`memory-lockup.svg`, `memory-lockup-light.svg`, `memory-wordmark.svg`); `svg_audit.py`: 0 FAIL, near-miss-angle warnings on the type only. The mark and favicons contain no text and are unchanged. `og.png` re-rendered with Chrome headless (1200x630, 75,351 bytes).
- `npm test`: `Tests 43 passed (43)`. `npm run build`: `✓ built in 125ms`; `dist/` 675,192 bytes. `node tools/a11y_check.mjs dist`: `A11Y-CHECK PASS`. `.venv/bin/python -m pytest -q`: `256 passed in 2.85s`.
- Screenshots: `python3 -m http.server 5222 --bind 127.0.0.1` (stopped afterwards), Chrome headless desktop 1440 px and phone 390 px; type scale re-tuned for the wide monospace display face (smaller h1 and h2, body 19 px for Crimson Pro's small x-height, nav labels 0.92 rem).

### Files changed

`demo/package.json`, `demo/package-lock.json`, `demo/src/{main.tsx, style.css, App.tsx}`, `demo/public/brand/{memory-lockup.svg, memory-lockup-light.svg, memory-wordmark.svg, og.png}`, `demo/DESIGN.md`, `demo/README.md`, `progress.md`.

### Next action

The coordinator deploys `demo/dist` when the owner agrees; nothing pushed or deployed here.
