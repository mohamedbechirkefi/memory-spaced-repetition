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
