<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Evidence audit (master prompt 11.5), M4, 2026-11-25

Scope: `research/paper/manuscript.md`, `research/paper/supplementary.md`, the three experiment reports `research/experiments/EXP-00N/report.md` and `research/claims_register.csv`. Internal quality control by the session, not external peer review.

## 1. Method

1. **Raw outputs verified.** The SHA-256 of each raw `results.json` equals its committed `SHA256SUMS` entry: EXP-001 `8662acfb...`, EXP-002 `9d58dd0a...`, EXP-003 `22c56bdb...` (the EXP-003 file is git-ignored and was present locally). SENS-001 checks the same hashes before reading.
2. **Automated number check.** `scripts/audit_numbers.py` extracts every decimal number from the scope files and requires it to equal, at its printed precision, a value in a committed source (frozen analyses, run manifests, generated results tables, SENS-001, CAL-001, CAL-002, RI-001, the journal, the freeze record and the frozen protocol). Headings, section and arXiv references and declared definitions (margins, thresholds, parameter values, versions) are classed separately. Output: `research/publication/number_audit.json`, with the line and the matching source files for every number.
3. **Targeted checks.** Counts and categorical statements that the automated check cannot see were recomputed from `frozen_analysis.json` (section 3).
4. **Artifact manifest.** `research/publication/artifact_manifest.json` (schema 0.2.0) maps every figure (FIG-001 to FIG-004), table (TAB-001 to TAB-006, SENS-001 A to C) and claim to experiment id, run ids, metric definition, result path and hash, generator, configuration and protocol hashes and code revisions; integer counts are mapped in its `integer_counts` list.
5. **External claims.** Each citation was checked against `research/literature_review.md` for the level at which the source was read.

## 2. Automated result (final run, after the corrections below)

| file | decimal numbers | matched to a source | definitions | section or arXiv references | unmatched |
|---|---|---|---|---|---|
| manuscript.md | 216 | 177 | 30 | 9 | 0 |
| supplementary.md | 216 | 207 | 9 | 0 | 0 |
| EXP-001 report | 122 | 99 | 22 | 1 | 0 |
| EXP-002 report | 130 | 111 | 18 | 1 | 0 |
| EXP-003 report | 25 | 18 | 7 | 0 | 0 |
| claims_register.csv | 86 | 77 | 7 | 2 | 0 |

The counts above are from the final run of the M4 session (`AUDIT: 0 unmatched`, recorded in `progress.md`); rerun the script after any edit. The claims register is read without its `manuscript_section` column. **Strength of this check.** A match means that some committed source holds the same value at the printed precision, not necessarily the intended one; short numbers can match by coincidence. The tables of the manuscript were therefore also compared line by line with the generated `results_tables.md` and with `sensitivity.json` (section 3).

## 3. Targeted checks and findings

| # | check | finding | action |
|---|---|---|---|
| F1 | EXP-003 report: cells with greedy minus uniform entirely below 0 | 13 cells: 10 power-law (C001, C007, C019, C025, C031, C043, C049, C055, C061, C067) and 3 exponential at `RI` 281. The report said "9 power-law cells". | **Mismatch fixed** in the EXP-003 report (marked as an M4 correction) and in CLM-007. |
| F2 | EXP-002 report and generated table: Holm p of massed minus uniform printed as 0.0000 | The paired t p-value underflows to 0.0 in double precision (t about 14 with 49 df); the true value is positive. | Reported as "0 (underflow)" in the EXP-002 report and the manuscript; the generated table is left as generated. |
| F3 | Denominators | EXP-001 250 runs (5 arms × 50 seeds), EXP-002 300 (6 × 50), EXP-003 18,000 (72 cells × 5 arms × 50 seeds); all `ok`; every contrast has 50 pairs (`n_pairs` in the analyses). | None. |
| F4 | Units and precision | All recall values are probabilities printed to 4 decimals; relative changes are fractions (0.0303), not percentages; intervals are 95% percentile bootstrap unless labelled paired t. | None. |
| F5 | Uncertainty | Every confirmatory contrast in the manuscript carries its bootstrap interval; EXP-003 intervals are labelled unadjusted; SENS-001 values are labelled exploratory. | None. |
| F6 | Ties, E1 and E2 | Ties in 3 cells (C000, C002, C016); E1 13 of 18 with 5 power-law failures; E2 16 of 24 with 7 of 8 failures under the power law. | Matches; E2 signed-difference reading disclosed (review pass 2, C6). |
| F7 | Stale status text | `research/experiment_registry.csv` still said "narrative report.md (11.3) pending" although the reports exist since M3 close. | Fixed. |
| F8 | Stale claims status | Every claims row said "M4 audit pending". | Updated; the register now has result id, run ids, configuration hash, figure or table, manuscript section and limit columns. |
| F9 | Stale figures | The figures cited by the manuscript are the committed `research/experiments/EXP-00N/figures/*.svg`, generated at analysis revision `3811bb9` from the frozen analyses; their checksums are in `results/confirmatory/EXP-00N/SHA256SUMS` (analysis copies). | None. |
| F10 | Missing failed runs | No run failed or was excluded in any matrix. The optional EXP-002 `ω` check was not run (owner, D-017) and is reported as not run. The pre-freeze draft-setting probes with the opposite sign (PROBE-001, PROBE-002) are disclosed in the manuscript (section 4.1) and the supplement. | Disclosure added to the manuscript. |
| F11 | Leakage | Seed sets are disjoint: confirmatory 1000 to 1049 and 3000 to 3349 (four blocks); exploratory 1 to 30, 101 to 105, 201 to 205, 301 to 305, 5000 to 5049. The `RI` choice used the uniform arm alone. DS01 enters only `h0` and `σ`. | None. |
| F12 | Derived numbers | "About three quarters" (reduction of the greedy advantage) is derived as (0.0347 - 0.0085) / 0.0347 = 0.755; 18,550 = 250 + 300 + 18,000; 288 = 72 × 4. | Recorded in the claims register and the manifest. |

## 4. External claims

| claim | source | level read | use in the manuscript |
|---|---|---|---|
| Exponential and power-law recall models, multiplicative update, optimal intensity grows as recall falls | Tabibian et al. (2019) | Content read (arXiv:1712.01856 v2) | Sections 1 to 3 |
| Half-life form, Pimsleur and Leitner descriptions | Settles and Meeder (2016) | Content read (abstract, sections 1 to 3.3) | Sections 2, 4.3 |
| Optimal inter-study interval increases with the retention interval (839 assessments, 317 experiments) | Cepeda et al. (2006) | **Abstract only**, marked as such in the text and the reference list | Sections 2, 6 |
| Leitner system as a queueing network | Reddy et al. (2016) | **Abstract only**, marked as such | Section 2 |
| DS01 dataset, licence CC BY-NC 4.0 | Settles (2017), Harvard Dataverse | Metadata and file read (downloaded, hashed) | Section 4.2 |
| Wixted and Ebbesen (1991), Averell and Heathcote (2011), Pavlik and Anderson (2005), Ye et al. (2022), Cepeda et al. (2008) | metadata only | Not read | Named as not read; not cited for content |

No external claim relies on a source that was not read at the stated level.

## 5. Verdict

Every decimal number in the manuscript, the supplement, the three reports and the claims register maps to a committed result or record; every figure and table maps to an experiment id, run ids, configuration and figure source in the manifest; every external claim maps to a source read at the stated level. Two mismatches were found and fixed (F1, F2) and two stale status texts updated (F7, F8). The M4 evidence gate holds.

## 6. M6 addendum (2026-11-25): sources rechecked in full text

At M6 a free, legal full text was opened for each external source that a claim depends on, and each cited statement was checked against it. No paid access, login or shadow library was used. Classification used for the M6 counts: **full text checked for the cited statements** (the full text was obtained and the passages that support the citation were read; the rest of the work was not necessarily read), **abstract only**, **unverified** (metadata only).

| source | full text used | where the cited statement was checked | result | level after M6 |
|---|---|---|---|---|
| Tabibian et al. (2019) | arXiv:1712.01856 v2 (21 pages) | section 2, equations 1 (exponential), 2 (power law) and 3 (multiplicative update); section 3, the intensity `u*(t) = q^(-1/2)(1 - m(t))` under quadratic loss; section 4, Uniform and Threshold baselines | matches; the PNAS version itself was not opened (version correspondence unverified, as before) | full text checked |
| Settles and Meeder (2016) | ACL Anthology PDF P16-1174 (11 pages) | section 3.1 (Pimsleur, exponentially increasing intervals); section 3.2 and Figure 3, p. 1850 (Leitner boxes 1, 2, 4, 8, 16 days); section 3.3, equation 1 (`p = 2^(-Δ/h)`) | matches | full text checked |
| Cepeda et al. (2006) | author manuscript, UC San Diego eScholarship (https://escholarship.org/uc/item/3rr6q10c, 36 pages) | abstract; Method, literature search (317 experiments in 184 articles, 839 assessments of distributed practice); Results and Discussion (optimal ISI increases with retention interval) | matches; the published APA version was not opened | full text checked (was abstract only) |
| Reddy et al. (2016) | arXiv:1602.07032 PDF (10 pages) | abstract; section 3.1, The Leitner Queue Network | matches | full text checked (was abstract only) |
| Settles (2017) dataset | Dataverse metadata and the downloaded file | licence CC BY-NC 4.0; SHA-256 rechecked at M6 | matches | dataset record |
| Wixted and Ebbesen (1991), Averell and Heathcote (2011), Pavlik and Anderson (2005), Ye et al. (2022), Cepeda et al. (2008) | none | not cited for content | unchanged | unverified (metadata only) |

Counts: 4 sources with the full text checked for the cited statements (none read cover to cover), 0 abstract only, 5 unverified and not cited for content, 1 dataset. No claim needed to be qualified further; the labels in manuscript section 2 and the reference list, `research/literature_review.md`, `research/claims_register.csv` (EXT-003, EXT-004) and `research/paper/references.bib` were updated. The remark in `review_pass_2.md` (C11) that "only the abstract of that source was read" is a dated M4 record and is left as written; the discussion in manuscript section 6 still refers to the abstract's statement, which the full text confirms. The number audit was rerun after the edits: `AUDIT: 0 unmatched`.
