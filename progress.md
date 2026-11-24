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
