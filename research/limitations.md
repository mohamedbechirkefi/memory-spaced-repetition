<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Limitations and threats to validity (M0 draft; no results exist yet)

## Scope boundary

- MEMORY is a simulation. Simulated learners are not human participants. Nothing in this project can show that any schedule improves human learning (master prompt section 10). No user data is collected or used.
- "Recall" always means the probability or simulated outcome produced by the model, never a human measurement.

## Construct validity

- The memory models (exponential and power-law forgetting with multiplicative updates) are taken from published model families (Tabibian et al. 2019; Settles and Meeder 2016). Whether they describe human memory well is outside what this project can test.
- The primary metric (mean true-model recall at one test time) ignores the shape of retention after the test and the cost of a review beyond counting it.
- Item difficulty is a single scalar (initial half-life); real items differ in other ways.

## Internal validity

- Adaptive schedulers are given information a real system would not have (true model family in EXP-001; true initial half-lives in EXP-001 and EXP-002). EXP-002 tests part of this; the initial half-life advantage remains.
- Arms differ in daily load and in where reviews fall relative to the test; the `massed` and `expanding` arms help separate recency from targeting but do not remove the confound.
- Implementation errors are the main risk; mitigated by hand-computed examples, invariant tests and differential tests (M2).

## External validity

- All parameter values are planning assumptions, not estimates from data. Results hold only within the explored ranges (EXP-003).
- Fixed window (28 days) and a single test time per cell.

## Statistical validity

- The unit is the simulated learner; items within a learner are not independent and are averaged first.
- Fifty seeds per cell; sample-size adequacy depends on the spread of paired differences, to be measured in the exploratory smoke run.
- EXP-003 is descriptive; its many intervals are not adjusted for multiplicity and support no confirmatory statement.

## Process

- The protocol is a draft and is not frozen. Until the owner freezes it, every run is exploratory.
- Several sources are verified at metadata level only (see `research/literature_review.md`); they are not cited for content.
