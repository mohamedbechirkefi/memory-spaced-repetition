<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Limitations and threats to validity (M0 draft, extended at the freeze, in M3 and in M4)

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

## Added at the freeze (2026-11-24, round 2)

- **Calibration fit.** `h0` and `σ` come from first-review recall in the Duolingo traces (protocol 15.2). The single exponential curve through `p(0) = 1` predicts held-out first-review recall worse than a constant (log-loss 0.587 vs 0.328, CAL-001): real recall stays near 0.9 at short delays. The calibrated parameters therefore match the median half-life of real lexemes, not the shape of real forgetting curves.
- **`σ` is an upper estimate.** Per-lexeme half-lives include sampling noise (protocol 15.2.6).
- **Ceiling regime.** At the fitted setting with `RI = 7`, baseline recall is about 0.96 for exponential learners (PROBE-005, baseline only). Superseded in round 3: the central `RI` is now 281 days (see below).
- **Not calibrated.** `α`, `β`, `ω` remain planning values.
- **Population.** Duolingo learners and lexemes in 2013 data; not representative of other learners or materials.

## Added at the round-3 re-freeze (2026-11-24, protocol section 16)

- **Model dependence (CAL-002).** Neither forgetting model beats a constant predictor of held-out first-review recall in DS01: best power-law curve 0.428, best exponential curve 0.549, constant 0.328 (log-loss per trial). Real recall is nearly flat in the delay (0.91 below one hour, 0.87 at 30 days or more). Every result is therefore a property of the assumed memory model, conditional on it; the calibration sets the time scale of the simulated items and does not validate the model.
- **Long central retention interval.** To leave the ceiling, the central `RI` is 281 days (rule 16.2, baseline-only; baseline recall 0.550 exponential, 0.680 power law). The study window stays 28 days, so the central cell describes retention about nine months after a four-week course.
- **Ceiling at short `RI`.** EXP-003 keeps `RI = 1, 7, 30`, where exponential baselines are 0.98, 0.96 and 0.89 at `k = 4` (RI-001); differences there are compressed.
- **Seed spread not re-measured** at `RI = 281` (it needs a contrast, which rule (b) forbids); the achieved interval width is reported with the results.

## Added in M3 (2026-11-25, after the confirmatory runs)

- **Oracle dependence (EXP-002).** The EXP-001 greedy advantage (+0.016) does not survive model misspecification: with an exponential model on power-law learners, greedy is practically equivalent to uniform within 0.02 (CLM-004, CLM-005). Both greedy schedulers also receive each item's true initial half-life, an advantage no deployed scheduler has.
- **Metric dependence (EXP-001).** Greedy raises the weakest items and lowers mastery share (CLM-002); the conclusion holds for mean recall only. Observed (Bernoulli) recall gives an interval that contains 0.
- **Setting dependence (EXP-003).** The ranking of arms changes across forgetting model, budget, retention interval and item distribution (CLM-007); at `k = 2` greedy is below uniform in 13 cells. Many exponential cells at `RI` 1 to 30 sit at the ceiling (automatic flags in the generated EXP-003 report), where differences are compressed.
- **Daily load confound.** `expanding` and `massed` place every item's reviews on the same 4 sessions (peak load 50 reviews per session), while `uniform`, `leitner` and the greedy arms spread reviews over 27 sessions with a peak of 8. Total budget is equal; daily burden is not.
- **Achieved precision.** At `RI = 281` the SD of paired differences was 0.0186 (EXP-001 primary) and 0.041 (EXP-002 primary contrasts), below the 0.07 adequacy threshold of protocol section 6.
- **EXP-002 `ω` check not run.** The descriptive check with `ω ∈ {0.3, 3}` (EXP-002 protocol section 16) has no frozen configuration; robustness to `ω` is untested.
- **`ω` check not run (owner decision, D-017).** The owner decided on 2026-11-25 ("approve all recommendations, RIGGED A", item 6) that the optional EXP-002 `ω` check is not run, because it has no frozen configuration. It is recorded as not run.

## Added in M4 (2026-11-25, interpretation and second review pass)

- **Fragile equivalence (EXP-002).** The frozen verdict stands, but the "equivalent within 0.02" classification of `greedy-exp` sits on the margin: bootstrap upper bound 0.0195, paired t upper bound 0.0201. Exploratory checks (SENS-001) give an interval above 0 on independent seeds (0.0098 [0.0007, 0.0187]) and at `RI` 7 and 30 on the confirmatory learners (0.0213 in both). What is robust is the size of the reduction (0.0347 to 0.0085), not the label (CLM-009).
- **Initial half-life advantage.** Both greedy arms know each item's true initial half-life; the EXP-002 misspecification removes only the model-family advantage. Any remaining greedy advantage is an upper bound for a realistic scheduler. Not testable without a new, separately frozen experiment.
- **No gap-dependent update.** In the model a review changes the forgetting rate by its outcome only, not by the gap since the previous review. "Spacing" acts only through review success and recency, so the results say nothing about the psychological spacing effect.
- **Leitner capacity.** Leitner is forced to the fixed daily capacity of the adaptive arms, and spare capacity goes to items not yet due (A2). Its deficit against uniform in EXP-001 may reflect this rule rather than the box logic.
- **Mastery share on a small base.** The EXP-001 mastery-share reversal (0.0200 to 0) concerns about one item of 50 per learner.
- **Massed wins at a higher daily load.** In EXP-003 massed is the most frequent top arm (29 cells, 24 of them under the power law) while reviewing 50 items per session against 8 for the spread arms.
- **Mechanism measured at one cell.** The reallocation diagnostics (CLM-011) come from the central cell (`k = 4`); the explanation of greedy's deficit at `k = 2` is not measured.
- **Post hoc checks.** SENS-001 was specified after the confirmatory results were seen; its ceiling threshold (0.95) is post hoc. It changes no frozen verdict.
- **E2 reading.** E2 compares signed differences; in groups where greedy is below uniform for every distribution, a magnitude reading could classify them differently (D-015 reading kept).
- **Pre-freeze exposure.** Draft-setting probes with greedy below uniform (PROBE-001, PROBE-002) were seen before the freeze; disclosed in the freeze record and the manuscript.
