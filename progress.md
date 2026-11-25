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
