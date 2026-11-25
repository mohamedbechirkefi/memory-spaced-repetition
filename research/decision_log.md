<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Decision log (append-only)

Each entry: id, date, decision, decided by, rationale, alternatives, consequences. Entries are never edited after the fact; corrections are new entries.

## D-001 (2026-11-24): Protective non-commercial licence instead of a permissive licence

- **Decided by:** the owner.
- **Decision:** All original material in this repository is licensed under the MEMORY Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-MEMORY-NC-Research-1.0`), with a Contributor License Agreement (CLA v1.0). The licence package (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/workflows/cla.yml`, `.gitignore`) was committed before this session.
- **Rationale:** the owner's stated reason is their own protection.
- **Deviation from the master prompt:** section 2 asks for an "owner-approved permissive code license". The owner chose a protective, source-available, non-commercial licence instead. The project is therefore not "open source" in the OSI sense; public texts must say "source-available" and must not describe the project as open source.
- **Consequences:** sessions never change the licence files. Data licences are recorded separately in `data/manifest.json`. Third-party dependencies keep their own licences.

## D-002 (2026-11-24): Zero-cost publication toolchain without TeX

- **Decided by:** session (M0), within the brief's instruction; open to owner review.
- **Decision:** Markdown is canonical. PDFs are produced by pandoc 3.6.3 (`/Users/bechir/research/labs/.tools/pandoc`) converting Markdown to Typst, then compiled by the `typst` Python package 0.15.0 in `/Users/bechir/research/labs/.tools/py/bin/python`. `research/paper/manuscript.tex` is generated from Markdown with pandoc for portability and is not compiled locally.
- **Rationale:** no TeX distribution is installed (`tex`, `pdflatex`, `xelatex` not found); installing one is unnecessary; all tools are free and local.
- **Alternatives:** installing TeX Live (large download, not needed); Chrome headless HTML printing (not chosen: Typst gives page numbers, equations and cross-references directly).
- **Consequences:** an exploratory toolchain smoke check was run this session (see `progress.md`); its PDF is in the session scratchpad and is not committed. Every future PDF must be generated and visually inspected before it is claimed.

## D-003 (2026-11-24): Synthetic data only for the draft protocol

- **Decided by:** session (M0), proposal pending owner approval.
- **Decision:** EXP-001 to EXP-003 use only synthetic items and simulated learners. No public dataset is downloaded or used.
- **Rationale:** the research question concerns modelled recall; section 10 requires no user data. DS01 (CC BY-NC 4.0) is lawful for non-commercial research but not needed; DS02 is gated and not redistributable.
- **Consequences:** all parameter values are planning assumptions, reported as such; external validity to human learners is explicitly out of scope.

## D-004 (2026-11-24): Protocol draft structure (pending owner freeze)

- **Decided by:** session (M0), proposal only. **Not frozen.**
- **Decision:** primary contrast `greedy` versus `uniform` under exponential forgetting (EXP-001); oracle-advantage sensitivity under power-law forgetting with model misspecification (EXP-002); descriptive sweep over models, budgets, retention intervals and item distributions (EXP-003). Primary metric: mean true-model recall probability at the delayed test. Unit: simulated learner; 50 matched seeds per cell.
- **Rationale:** see `research/protocol.md` sections 3 to 10.
- **Consequences:** the owner may change any of these before the freeze (G-FREEZE).

## D-005 (2026-11-24): Dependency lock with a two-week release cutoff

- **Decided by:** session (M0).
- **Decision:** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"` so that every locked package version was released at least two weeks before 2026-11-24. Python 3.12. Runtime dependencies kept minimal (NumPy, jsonschema, matplotlib); test dependencies pytest and hypothesis.
- **Consequences:** upgrades require a dated decision entry.

## D-006 (2026-11-24): M2 implementation choices where the draft protocol leaves room

- **Decided by:** session (M2), open to owner review. None changes the draft analysis.
- **Decisions.**
  1. `uniform`: item `i` (0-based) is reviewed at sessions `ceil(g (i+1)/N + j g)`, `g = (D-1)/k`, `j = 0..k-1`, computed in exact integer arithmetic. The last item is exactly equally spaced from encoding; others are shifted earlier by less than one gap to spread the daily load. Gaps differ by at most one day (tested).
  2. `expanding`: targets `g (2^(j+1) - 1)` with `g = (D-1)/(2^k - 1)`, rounded half up, then forced strictly increasing and at least 1; the last review is at `D-1`. For `k = 4` and `D = 28`: sessions 2, 5, 13, 27. All items share the same sessions (the draft does not ask for staggering).
  3. `massed`: sessions `D-k .. D-1`.
  4. Adaptive capacity: `c_s = floor(s B/(D-1)) - floor((s-1) B/(D-1))`, which sums exactly to `B`.
  5. `leitner`: priority key (not due, box, item index), the literal reading of the draft; its starvation effect is reported in AP-003, not fixed.
  6. `greedy`: lowest predicted recall first, ties by lowest item index; the scheduler knows each item's true initial half-life and `α`, `β` (draft section 3 and EXP-002 section 7).
  7. Common random numbers: one `SeedSequence(seed)` spawns three PCG64 streams (difficulty, review uniforms indexed by item and review index, test uniforms), drawn before any arm runs.
  8. Power law evaluated as `exp(-n log1p(ω Δ))` (EXP-002 section 15).
  9. Runtime per run excludes the CRN draw; memory is the process resident-set high-water mark (`ru_maxrss`), which is monotone over a process and is reported as such.
  10. Provenance `git_dirty` ignores changes under `results/` (run outputs do not change the code).
  11. No SciPy: Student t quantiles via the regularized incomplete beta function, checked against textbook values.
- **Consequences.** Each choice is pinned by tests; changing one is a dated decision.

## D-007 (2026-11-24): exploratory planning runs before the freeze

- **Decided by:** session (M2), within the M2 brief.
- **Decision.** Five exploratory matrices on seeds disjoint from the confirmatory list: SMOKE-001 (protocol section 9 smoke matrix), PROBE-001 (central setting, N = 50, seeds 1 to 30), PROBE-002 (power-law learners, six arms, seeds 1 to 30), PROBE-003 (all 54 EXP-003 cells, seeds 1 to 5), PROBE-004 (baseline arm only, `h0` from 1 to 16 days, seeds 1 to 5). Outputs in `results/exploratory/`, journaled in `research/experiment_journal.jsonl`.
- **Rationale.** The protocol needs runtime and the SD of paired differences before the freeze; the degenerate-case scan checks the sweep. PROBE-004 runs only the baseline so that the floor diagnostic shows no arm contrast.
- **Consequences.** Contrasts at the draft settings have been seen (disclosed in `research/amendment_proposals.md`). Nothing from these runs is a finding or enters the claims register.

## D-008 (2026-11-24): amendment proposals AP-001 to AP-006 submitted to the owner, not applied

- **Decided by:** session (M2) proposes; the owner decides (G-FREEZE).
- **Decision.** `research/amendment_proposals.md` records six proposals: AP-001 central setting at the recall floor; AP-002 failure update and greedy rule review hopeless items; AP-003 Leitner priority starves items; AP-004 seed count adequate under the draft rule but to be re-measured after AP-001/AP-002; AP-005 compute budget not binding (about 12 s to 55 s for the 14,050-run matrix); AP-006 EXP-003 `RI` cells share runs.
- **Consequences.** The draft protocol, experiment protocols and draft configurations are unchanged. If amendments are accepted, configurations, tests and protocol text are updated and the planning probe is re-run before the freeze.

## D-009 (2026-11-24): Duolingo traces (DS01) adopted for calibration; licence checked

- **Decided by:** the owner ("Approve all", approvals file `labs/_shared/owner-approvals-2026-11-24b.md`, section 1: "MEMORY | Duolingo spaced-repetition logs (Settles and Meeder 2016), CC BY-NC 4.0 | Fit the forgetting parameters to real learners"). Applied by the session.
- **Licence check.** Dataverse API for doi:10.7910/DVN/N8XJME read on 2026-11-24: terms of use "This work is released under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)." Matches the approval. One file, `settles.acl16.learning_traces.13m.csv.gz`, 379,004,009 bytes, MD5 `0a1cae5eb7ad4b0bd9c0de91d74fcced` (Dataverse), SHA-256 `26cf9b33f2e9b2e8aa9a8f262a017b30699ca2f625c56a12ce699d4ea7076873`, downloaded 2026-11-24T18:33:02Z by `scripts/download_duolingo.py`.
- **Handling.** Above the 20 MB commit limit and row-level with pseudonymous learner IDs, so `data/raw/` and `data/processed/` are git-ignored; only aggregate values are committed (`results/exploratory/CAL-001/calibration.json`). D-003 (synthetic data only) is superseded for these two parameters.

## D-010 (2026-11-24): round-2 amendments applied and calibration fitted

- **Decided by:** the owner ("yes for all others", section 7 of the approvals file); applied by the session as written in `research/protocol.md` section 15.
- **Applied.** A1 `h0` and `σ` fitted from DS01 (method 15.2 committed at `037b46e` before the fit): `h0 = 54.0` days, `σ = 0.759` (CAL-001); fallback `h0 = 6` not needed. A2 coverage-first rule for every adaptive arm; capacity unchanged (exact carry); Leitner ties by due, earliest due day, box, index (AP-003 order); greedy ties by predicted recall, index. A3 50 seeds. A4 EXP-003 kept. A5 EXP-003 `RI` levels on disjoint seed blocks 3000, 3100, 3200 (50 each); configuration field `seeds.block_by`.
- **Not calibrated, by stated rule (15.2.8).** `α`, `β`, `ω` and the design factors.
- **Interpretation choice by the session.** "Cover every item" is read as "every item is reviewed at least once" (coverage-first key), not as a fixed per-item quota; the per-item allocation after coverage stays adaptive. The owner may revisit this before M3.
- **Consequences.** The calibrated exponential curve fits held-out first-review recall worse than a constant (log-loss 0.587 vs 0.328), and the fitted central setting is near the ceiling for exponential learners (baseline-only PROBE-005: mean `R` 0.959; power law 0.810). Both are disclosed (freeze record, limitations).

## D-011 (2026-11-24): protocol frozen (G-FREEZE, owner-approved)

- **Decided by:** the owner ("yes for all others", "Approve all"). Recorded by the session.
- **Frozen.** `research/protocol.md` v1.0 SHA-256 `0d437fd2b722c3361b8e67b8107f933468da5b2631ff246656d9be94f6df4da4`; EXP-001 `df9a38cf...`, EXP-002 `596ab71f...`, EXP-003 `be44baa1...` protocols; configuration hashes in `research/freeze.json` (which also holds the git revision and the data manifest hash).
- **Guard.** `run` accepts a confirmatory configuration only if the study protocol, the experiment protocol and the canonical configuration hash all match the freeze record; any change is refused (exit 3). Tested both ways without running a confirmatory matrix.

## D-012 (2026-11-24): round-3 rule (a), forgetting-model misfit diagnosed

- **Decided by:** the owner ("Approve all", 2026-11-24, round 3; approvals file `labs/_shared/owner-approvals-2026-11-24c.md`, section 2, rule (a): "Diagnose the misfit first. Write a pre-stated method in the protocol, then compare the exponential and power-law forgetting fits by held-out log-loss on the validation split."). Applied by the session.
- **Method.** `research/protocol.md` section 16.1, committed at `664de3c` before any computation. Seven predictors fitted on split C only, scored on split V only; no simulation, no schedule arm.
- **Outcome (CAL-002).** Held-out log-loss per trial: constant 0.328; best exponential (`exp-population`) 0.549; best power law (`power-mle`, `n = 0.0764`, `ω = 1`) 0.428. The power law fits better, but neither family beats the constant. Real first-review recall is nearly flat in the delay (0.91 to 0.87).
- **Consequences.** Recorded as a limitation; the claims boundary now states that every result is conditional on the assumed memory model (protocol 16.3, `research/limitations.md`). No parameter changed.

## D-013 (2026-11-24): round-3 rule (b), central retention interval 281 days

- **Decided by:** the owner (same approval, rule (b): "Move off the ceiling by changing the study design, not the fitted parameters. [...] the baseline uniform schedule's recall lands in [0.4, 0.7] at the central cell."). The selection rule was written by the session in protocol 16.2 and committed at `8d4854a` before it was applied.
- **Rule.** Step 1: `RI` from 1 to 365 days, uniform arm only, exploratory seeds 1 to 30; the candidate in `[0.4, 0.7]` closest to 0.55, ties to the smaller `RI`. Step 2 (harder-half lexeme subset) only if step 1 fails.
- **Outcome (RI-001, PROBE-006).** Candidates 142 to 365 days; `RI* = 281` days, baseline mean `R` 0.550 (exponential); 0.680 under the power law (descriptive). Step 2 not used; no parameter value changed. No other arm and no contrast was computed.
- **Consequences (fixed in 16.2.5 before the value was known).** EXP-001 and EXP-002 central `RI = 281`. EXP-003 adds `RI = 281` as a fourth level (seed block 3300 to 3349; 72 cells, 18,000 runs). This EXP-003 extension is the session's reading of "the central cell" for a full-factorial sweep; the owner may revert it to the three original levels before M3.
- **Not done.** The seed-spread estimate was not re-measured at `RI = 281`: it needs a contrast, which rule (b) forbids.

## D-014 (2026-11-24): re-freeze v1.1 (rule (c), G-FREEZE owner-approved)

- **Decided by:** the owner (same approval, rule (c): "Then re-freeze. Keep the superseded hashes, and add the C4 disclosure of everything seen."). Recorded by the session.
- **Frozen v1.1.** `research/protocol.md` SHA-256 `fb9258a46b4b03fa1ffb171744ab951577bdf316c6147c93a00a3854603dff0d`; EXP-001 `91a79174...`, EXP-002 `9f1e4e7c...`, EXP-003 `f4767c19...` protocols; configuration hashes, git revision `dcdaf2e` and the data manifest hash in `research/freeze.json`.
- **Superseded.** The v1.0 hashes (protocol `0d437fd2...`, git revision `6a8bc29`) are kept under `superseded` in `research/freeze.json` with the reason. No confirmatory run was made under v1.0.
- **C4.** Extended with CAL-002, RI-001 and PROBE-006 (values and paths).
- **Guard.** Accepts the three v1.1 configurations; refuses the v1.0 configurations (CLI exit 3, checked on the configurations at `6a8bc29`) and any changed configuration (tested).

## D-015 (2026-11-25): M3 pre-run analysis code and provenance fields, before any confirmatory output

- **Decided by:** the session, under the M3 brief (the owner's "Start next", 2026-11-25). Committed before any confirmatory run; `results/confirmatory/` did not exist.
- **Analysis code.** `src/memory_research/frozen_analysis.py` and `scripts/analyse_confirmatory.py` apply the frozen rules (study protocol sections 4, 7, 10; experiment protocols 4, 13, 16). The M2 report generator remains the generic table and figure source; it applies Holm across every non-baseline arm of a cell, which is the EXP-001 secondary family but not the EXP-002 primary family, hence the dedicated module.
- **Implementation readings fixed now (the protocols leave them implicit).** (1) A "statement of difference" under Holm means a Holm-adjusted paired t p-value below 0.05. (2) "EXP-001 shows a positive difference" (EXP-002 interpretation rule) means the EXP-001 primary 95% bootstrap interval lies entirely above 0. (3) "H0b is not rejected" means the Holm-adjusted (over the two EXP-002 primary contrasts) paired t p-value is at least 0.05; the interval in that rule is the 95% bootstrap interval. (4) EXP-003 "share of seeds where each arm ranks first": exact ties share the credit equally; the number of tied seeds is reported. (5) EXP-003 "rank reversal relative to EXP-001": a pair of arms whose order of cell means differs from their order of EXP-001 means; the top arm and the sign of greedy minus uniform are also compared. (6) E1 holds in a (model, k, distribution) group if massed minus uniform is non-increasing in `RI`; E2 holds in a (model, k, RI) group if greedy minus uniform is smallest for `homogeneous` items. All descriptive.
- **Provenance fields.** Each run now records `start_utc` and `end_utc`; the environment records the SHA-256 of `data/manifest.json`. Both are optional schema fields (`memory-result/1.0.0` remains valid for earlier files).
- **Labels.** The M2 figure titles said "EXPLORATORY" for every result file; they now follow the result's kind.
- **Not run.** The EXP-002 `ω ∈ {0.3, 3}` descriptive check (EXP-002 protocol section 16) has no frozen configuration; it is not run in M3 (brief: an optional experiment runs only if it has a frozen config). Writing its configuration would require choosing its seeds and arms, which the protocol does not fix.

## D-016 (2026-11-25): M3 confirmatory runs, records and one presentation change

- **Decided by:** the session, under the M3 brief (the owner's "Start next", 2026-11-25).
- **Runs.** EXP-001 (250 runs), EXP-002 (300) and EXP-003 (18,000) ran once each through the guard at clean revision `d4a793d`, with the frozen configurations and seeds; every run `ok`, none excluded or failed. No protocol, configuration, seed, exclusion rule or analysis code changed after the output existed.
- **Presentation change after output (no analysis change).** The forest-plot titles and axis labels of `scripts/analyse_confirmatory.py` were clipped; the figure size and label line breaks were changed at `3811bb9` and the analysis rerun. Every value in the three `frozen_analysis.json` files was compared before and after and is identical; only the generator revision differs.
- **Smoke output overwritten and restored.** `python -m memory_research smoke` writes to `results/exploratory/SMOKE-001/`, which held the committed M2 smoke output. The session copied the new output to `results/exploratory/SMOKE-001-M3/` and restored the committed files with `git restore` (its own modification only).
- **Storage.** EXP-003 outputs total about 24 MB, above the 20 MB limit; its `results.json` (15.5 MB) is git-ignored and regenerable (bit-identical on the same platform); the run manifest, SHA-256 manifest, generated report, analysis and tables are committed. EXP-001 and EXP-002 are committed in full.
- **Not run.** EXP-002 `ω` descriptive check (no frozen configuration; D-015).
- **Records blocked.** The 11.3 narrative reports `research/experiments/EXP-00N/report.md` were not written in this session: the session's file tool refused to create report files. The generated tables (`results_tables.md`), generated reports and PDFs (`results/confirmatory/EXP-00N/report/`) and the analysis files exist; the narrative reports are pending for the owner or a later session.

## D-017 (2026-11-25): owner decisions closing M3

- **Decided by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (coordinator file `labs/_shared/owner-approvals-2026-11-25.md`, items 4 and 6). Recorded by the session.
- **Item 6, EXP-002 `ω` check.** "EXP-002's optional ω check is not run, because it has no frozen config." "It is recorded as not run." Recorded in `research/limitations.md`, `research/freeze.json` (`post_freeze_record`), the registry and `progress.md`. Robustness to `ω` stays untested.
- **Item 4, experiment reports.** The owner approves writing the missing 11.3/11.6 reports from the committed results, tables and figures only, with no recomputation. In this session the file tool again refused to create `research/experiments/EXP-001/report.md`. Under the close brief the session stopped without a workaround, so the three narrative reports remain unwritten and M3 stays in progress.

## D-018 (2026-11-25): M4 interpretation, exploratory sensitivity, evidence audit and manuscript

- **Decided by:** the session, under the M4 brief (owner, 2026-11-25, "Approve all recommendations, push then next"; coordinator file `labs/_shared/owner-approvals-2026-11-25b.md`, section 5). No project-specific follow-up in that file concerns MEMORY.
- **Exploratory sensitivity SENS-001.** `scripts/m4_sensitivity.py` was committed at `2e8cf05` before it ran, then ran once (2.5 s, one process). Part A and B reuse committed raw outputs (SHA-256 checked); part C re-simulates the frozen EXP-001 and EXP-002 base settings on new exploratory seeds 5000 to 5049. Output `results/exploratory/SENS-001/sensitivity.json`, journal SENS-001. It is post hoc and changes no frozen verdict, configuration, protocol or seed.
- **Conclusions after M4.** EXP-001 unchanged and replicated on independent seeds; recency explanation ruled out at the central cell. EXP-002 frozen verdict kept; its reading qualified as fragile and restated quantitatively (reduction of about three quarters). EXP-003 instability robust to resolved-difference and ceiling checks.
- **Evidence audit.** `scripts/audit_numbers.py` and `research/publication/{evidence_audit.md, number_audit.json}`; manifest schema 0.2.0. Fixed: EXP-003 report "9 power-law cells" to 10; massed Holm p "0.0000" reported as an underflow; stale registry and claims status texts.
- **Claims register.** Restructured with result id, run ids, configuration hash, figure or table, manuscript section and limit columns; CLM-005 and CLM-007 qualified; CLM-009 to CLM-014 and EXT-001 to EXT-004 added.
- **Reports.** The three reports are marked M4 final, with corrections marked and an M4 addendum each; no frozen value was edited.
- **Manuscript.** Synthesized to the 11.4 structure, revised after `research/publication/review_pass_2.md`; status "independent research manuscript / preprint draft, not peer-reviewed". `manuscript.tex` regenerated with pandoc; no PDF is claimed (M6).
