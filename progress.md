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
