<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Reproducibility report (M6, 2026-11-25)

Only actual outputs are recorded here. Machine: Apple M1 Pro laptop, macOS (the confirmatory runs' platform). Tools: uv 0.9.5 and the Typst Python package 0.15.0 from the shared tools folder, pandoc 3.6.3, Node v22.23.3 (read-only, shared tools folder), npm cache in the session scratchpad. At most one computation ran at a time.

## 1. Clean clone (first pass, revision `46b4a11`)

The working tree was clean at `46b4a11` (M5 close). Nothing was committed before the clone.

| step | command (run inside the clone unless stated) | actual output |
|---|---|---|
| clone | `git clone -q <repository folder> <scratch>/clone` (local, no network) | HEAD `46b4a11` |
| locked install | `uv sync --frozen --all-groups --all-extras` | environment created; last lines `+ sortedcontainers==2.4.0`, `+ typing-extensions==4.16.0`, `+ tzdata==2026.6` |
| test suite | `.venv/bin/python -m pytest -q` | `253 passed in 38.38s` |
| documented smoke | `.venv/bin/python -m memory_research smoke --out <scratch>/smoke` | refused by design: `exploratory outputs must go under a path containing 'exploratory'` (the output guard; not a failure) |
| documented smoke | `.venv/bin/python -m memory_research smoke --out <scratch>/exploratory/SMOKE-001` | `SMOKE-001 [exploratory]: 25 runs, 25 ok, 0 excluded, 0 failed, wall clock 0.034 s` |
| smoke comparison | leaf-by-leaf JSON comparison with `results/exploratory/SMOKE-001-M3/results.json` (the committed smoke output of the current engine; `SMOKE-001/` holds the pre-calibration M2 output, D-016) | 103 differing leaves, all timing or provenance fields: `start_utc`, `end_utc`, `runtime_s`, `peak_rss_bytes` (25 each), `git_revision`, `wall_clock_s`, `created_utc` (1 each); every metric identical |
| smoke tables | `cmp` of `report/summary.csv` and `report/contrasts.csv` with `SMOKE-001-M3/report/` | both byte-identical |
| reproduction of a committed result | `.venv/bin/python -m memory_research run --config research/experiments/EXP-001/config.json --out <scratch>/rerun-exp001` (README quick start; output kept in scratch, discarded, not a new result) | `EXP-001 [confirmatory]: 250 runs, 250 ok, 0 excluded, 0 failed, wall clock 0.288 s`; the guard accepted the frozen configuration |
| comparison | leaf-by-leaf JSON comparison with the committed `results/confirmatory/EXP-001/results.json` | 1,003 differing leaves, all timing or provenance fields: `runtime_s`, `start_utc`, `end_utc`, `peak_rss_bytes` (250 each), `wall_clock_s`, `git_revision`, `created_utc` (1 each); every metric value identical (documented tolerance in `research/experiments/EXP-001/reproduction.md`: bit-identical except timing and memory fields). File SHA-256 differs only through those fields. |
| demo install | `npm ci --prefer-offline` (in `demo/`) | `added 53 packages in 1s` |
| demo tests | `npm test` | `Test Files  2 passed (2)`, `Tests  43 passed (43)` |
| demo build | `npm run build` | `✓ built in 421ms`; `index-*.js` 259.88 kB, worker 6.61 kB, CSS 7.07 kB |
| accessibility and offline check | `node tools/a11y_check.mjs dist` | nine `PASS` lines (6 experiment panels; contrast light and dark; keyboard 29 of 29; visible focus; overflow 0 px at 360 px; 0 running animations; no foreign request; offline sandbox run) and `A11Y-CHECK PASS` |
| export determinism | `.venv/bin/python scripts/export_demo_data.py`, then `--check`; `scripts/export_engine_fixture.py --check`; `git status --short` | `wrote demo/public/data/results.json (84389 bytes)`, `EXPORT-CHECK PASS`, `FIXTURE-CHECK PASS`; `git status` empty (deterministic) |

## 2. Findings during M6 and their fixes (working repository)

| # | finding | fix |
|---|---|---|
| R1 | `build_pdf` used the Markdown file's folder as the Typst root, so the manuscript, which cites figures in `research/experiments/*/figures/`, failed: `path "../experiments/EXP-001/figures/exp001_contrasts.svg" would escape the project root`. | The Typst root is the repository root for files inside the repository (`_typst_root` in `src/memory_research/report.py`). |
| R2 | Reports and the supplement had no PDF title (pypdf metadata). | `_set_pdf_title` sets the document title from the first level-1 heading when the Markdown has no YAML title. |
| R3 | Pandoc wrapped Typst lines at 72 columns; a line beginning with `0. Third` became a numbered list item in manuscript section 5.2. | Pandoc runs with `--wrap=none`. |
| R4 | Lists written directly under a bold label (no blank line) rendered as inline dashes or numbers in the EXP-001, EXP-002 and EXP-003 reports (5 places). | Blank line inserted before each list in the report Markdown; text unchanged. |
| R5 | Tables with fixed equal column widths overlapped (supplement S1, S3, S4.1) and long tables did not break across pages, so the S6 table ran over the page footer. | Pandoc runs with `--columns=10000` (content-sized columns), figures are breakable (`#show figure: set block(breakable: true)`), table text is 0.85 em. The S3 hash table became a list (64-character hashes cannot wrap); the S1 matrix was merged into 5 columns. Values unchanged. |
| R6 | The two tall EXP-003 figures (first-rank share heat map; all-cells overview) filled a page and pushed their captions to the next page. | Height limited to 20 cm in the Markdown image attributes. |
| R7 | Two absolute home-directory paths in current files (`src/memory_research/report.py` defaults; `demo/README.md`). | The builder derives the tools folder from the package location (`../.tools`, overridable by `MEMORY_PANDOC` and `MEMORY_TYPST_PYTHON`); the demo README names the shared tools folder without a path. |

No result, protocol, configuration, seed or generated table changed. The number audit was rerun after the Markdown edits: `AUDIT: 0 unmatched` (manuscript 220 numbers, supplement 216, EXP-001 122, EXP-002 130, EXP-003 25, claims register 88).

## 3. PDFs (Typst toolchain, D-002)

Built with `memory_research.report.build_pdf` (pandoc 3.6.3 to Typst, compiled by the `typst` package 0.15.0); pages rendered to PNG at 80 ppi in scratch from the final intermediate `.typ` files and read with an image viewer, two pages per sheet. Every report page that was not inspected (the last page of each report) holds text only (pypdf: no image object).

| file | pages | bytes | pages inspected |
|---|---|---|---|
| `research/paper/manuscript.pdf` | 15 | 370,351 | all 15 |
| `research/paper/supplementary.pdf` | 5 | 138,304 | all 5 |
| `research/experiments/EXP-001/report.pdf` | 7 | 175,739 | 1 to 6 (figures on 4 to 5) |
| `research/experiments/EXP-002/report.pdf` | 7 | 189,070 | 1 to 6 (figures on 4 to 5) |
| `research/experiments/EXP-003/report.pdf` | 10 | 402,401 | 1 to 8 (figures on 4 to 8) |

Metadata (pypdf): every PDF has a title (manuscript: the approved title; supplement: "Supplementary material"; reports: their level-1 heading); the manuscript also carries the author name from its YAML header. Text and metadata scan: 0 e-mail addresses, 0 local paths, 0 raw Markdown markers, 0 stray `$`. Remaining cosmetic points, not fixed: in the manuscript the captions of Tables 4 and 5 sit at the bottom of a page with the table on the next page; the cell labels of the first-rank-share heat map (FIG-004) are small (vector SVG, legible when zoomed; the figure is a committed generated artifact and was not regenerated); some negative numbers in tables print with a hyphen rather than a minus sign. The PDFs are committed (no `.gitignore` rule or decision excludes them); the intermediate `.typ` files are not.

## 4. References, links, manifests

- **Bibliography.** The manuscript cites by author and year (pandoc citations are disabled in the builder). Every entry of the manuscript reference list (5) now has a `references.bib` entry (2 added: Reddy et al. 2016; Settles 2017 dataset), and every bib entry is in the reference list: 5 of 5.
- **Sources rechecked in full text (free, legal copies).** Settles and Meeder (2016), ACL Anthology PDF: sections 3.1, 3.2 with Figure 3 (p. 1850) and 3.3, equation 1. Tabibian et al., arXiv:1712.01856 v2: equations 1 to 3 (section 2), the quadratic-loss intensity (section 3), the Uniform and Threshold baselines (section 4). Cepeda et al. (2006), author manuscript on eScholarship (UC San Diego): Method (literature search: 317 experiments in 184 articles, 839 assessments) and Results and Discussion (optimal ISI increases with retention interval). Reddy et al. (2016), arXiv:1602.07032: section 3.1 (The Leitner Queue Network). Each cited statement matches. No paid access, login or shadow library was used.
- **Relative links.** `.venv/bin/python scripts/check_links.py`: `57 Markdown files, 33 relative links checked, 0 broken`, `LINK-CHECK PASS` (test `tests/test_links.py`). An additional scan of back-quoted repository paths in the README, manuscript, supplement, articles, reports and reproduction files found 10 non-existent strings, all placeholders or schema names (`EXP-NNN`, `memory-result/1.0.0`, `report/`, `analysis/` relative to a results folder), none a broken reference.
- **Numbers.** Every decimal number of `README.md`, `articles/medium.md`, `articles/linkedin.md` and `articles/README.md` occurs in the manuscript or the supplement (ad hoc scan: 0 missing); `tests/test_demo_export.py` already enforces this for README, `CITATION.cff`, the articles and the demo README.
- **Data manifest.** `data/manifest.json`: DS01 file present locally (git-ignored), SHA-256 `26cf9b33...6873`, MD5 and size 379,004,009 bytes equal to the manifest. Only `data/manifest.json` is tracked under `data/`; no data file is bundled.
- **Result checksums.** `shasum -a 256 -c SHA256SUMS`: EXP-001 18 OK, EXP-002 18 OK, EXP-003 22 OK, 0 failures.
- **Artifact manifest.** 40 repository paths in `research/publication/artifact_manifest.json`; all exist (one is the pattern `results/confirmatory/EXP-00N/analysis/frozen_analysis.json`, whose three expansions exist).

## 5. Secret, identifier and licence scan (`git ls-files`, 304 text files)

- E-mail addresses: 1 hit, `CLAUDE.md` line 59, the commit-trailer address of the AI co-author instruction (not personal; kept).
- Tokens, keys, private-key headers (AWS, GitHub, Slack, Google, generic `api_key/secret/token/password = "..."` patterns): 0.
- `.env` files tracked: 0.
- Absolute home-directory paths: 18 lines in 6 files before M6. Removed from current files: `src/memory_research/report.py` (2), `demo/README.md` (1). Kept: `CLAUDE.md` (5; operating instructions that name the shared tools), `research/feasibility.md` (5; the M0 record of commands and outputs), and the append-only `progress.md` (1) and `research/decision_log.md` (3), where a note is appended instead (D-021). No git history was rewritten. Update of 2026-11-26: `CLAUDE.md` and `research/feasibility.md` were scrubbed (section 7).
- Dependency licences: `research/publication/dependency_licences.md` (23 Python packages, 84 npm packages); none outside the permissive set.
- SPDX headers: every tracked text file whose format allows a comment carries `LicenseRef-MEMORY-NC-Research-1.0`, except the owner's licence files and `master_prompt.md` (initial commit, before M0) and the `SHA256SUMS` files (a comment line would break `shasum -c`).

## 6. Clean clone (second pass, M6 commit `ac66801`)

A fresh local clone of `ac66801` in the session scratchpad (deleted afterwards), to re-check the fixes of section 2.

| step | actual output |
|---|---|
| `uv sync --frozen --all-groups --all-extras` | environment created (last line `+ tzdata==2026.6`) |
| `.venv/bin/python -m pytest -q` | `256 passed in 8.50s` |
| `memory_research smoke --out <scratch>/exploratory/SMOKE-001` | `25 runs, 25 ok, 0 excluded, 0 failed, wall clock 0.029 s`; against `SMOKE-001-M3`: 103 differing leaves, all timing or provenance; `summary.csv` and `contrasts.csv` identical |
| `scripts/check_links.py` | `LINK-CHECK PASS` |
| `scripts/audit_numbers.py` | `AUDIT: 0 unmatched` |
| demo: `npm ci --prefer-offline`, `npm test`, `npm run build`, `node tools/a11y_check.mjs dist` | `added 53 packages`; `Tests 43 passed (43)`; `✓ built`; `A11Y-CHECK PASS` |
| `scripts/export_demo_data.py`, `--check`; `export_engine_fixture.py --check`; `git status --short` | `EXPORT-CHECK PASS`, `FIXTURE-CHECK PASS`; 0 changed files |
| PDF rebuild of the manuscript, supplement and three reports with `build_pdf` (the clone lies outside the labs folder, so `MEMORY_PANDOC` and `MEMORY_TYPST_PYTHON` were set as documented) | builds succeed (finding R1 fixed); pages 15, 5, 7, 7, 10 and byte sizes identical to the committed PDFs; every PDF titled; the files differ from the committed ones only in 3 lines each (creation and modification timestamps), so PDFs are reproducible except for their timestamps |

## 7. Owner answers applied (2026-11-26)

Authority: owner, 2026-11-26, decision sheet (D-022). Wording and configuration only; no result, analysis, figure, configuration, seed, frozen protocol, protocol hash or checksummed output changed.

| step | actual output |
|---|---|
| `.venv/bin/python -m pytest -q` | `256 passed` |
| `scripts/export_demo_data.py`, `--check`; `export_engine_fixture.py --check` | `wrote demo/public/data/results.json (84389 bytes)`, `EXPORT-CHECK PASS`, `FIXTURE-CHECK PASS`; `results.json` unchanged |
| demo: `npm test`, `npm run build`, `node tools/a11y_check.mjs dist` | `Tests 43 passed (43)`; `✓ built`; nine `PASS` lines including "no request leaves the local origin", `A11Y-CHECK PASS` |
| `manuscript.tex` regenerated with pandoc 3.6.3 | differs from the previous file only in the author line, `pdfauthor` and section 10 |
| PDF rebuild with `build_pdf` (manuscript, supplement, three reports; every source changed) | pages 15, 5, 7, 7, 10 (unchanged); bytes 369,428, 138,320, 175,751, 189,086, 402,413; manuscript metadata author "Mohamed Bechir Kefi, independent researcher"; 0 local paths in the text. Inspected as PNG at 80 ppi: manuscript pages 1 (author line) and 15 (sections 10 and 11), the first page of the supplement and of each report (author line) |

**Absolute home paths remaining in tracked files (B9).** 4 lines, all in append-only records that are never edited: `progress.md` line 258 and `research/decision_log.md` lines 17, 154 and 161 (D-002, D-019, D-020). They name the shared tools folder and the coordinator's brief and approval files. They stay as written because the records are append-only; they were already public in the history, which is not rewritten. Scrubbed on 2026-11-26: `CLAUDE.md` (5 lines; paths now relative to the repository, `../.tools/`, and "the research root" in words; `../.tools/py/bin/uv --version` from the repository root prints `uv 0.9.5`) and `research/feasibility.md` (5 lines; the M0 command record now writes `~` and relative tool paths, with a dated note that the commands were run with absolute paths). Frozen protocols, checksummed results, run logs and licence files contain no home path.
