<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# MEMORY study protocol

**Status: FROZEN v1.1 (owner-approved 2026-11-24: round 2, "yes for all others", "Approve all"; round 3 pre-data amendment, "Approve all"). v1.0 is superseded by the round-3 recalibration (section 16): central retention interval 281 days.** The SHA-256 of this file, of the experiment protocols and of the confirmatory configurations is recorded in `research/freeze.json`, `research/experiment_registry.csv` and `research/decision_log.md` (D-009). Section 15 amends sections 1 to 14 and section 16 amends sections 1 to 15; the later section wins where they differ. Two parameters (`h0`, `σ`) are calibrated to the Duolingo traces (section 15.2); every other numerical setting is a planning assumption for a simulation.

## 1. Research question

Which review schedule maximizes modelled delayed recall of a set of synthetic items under a fixed study budget (a fixed total number of review events within a fixed study window)?

This is a question about a mathematical model of memory, answered by simulation. It makes no claim about human learners (master prompt section 10, claims boundary).

## 2. Formal model

### 2.1 Time, items and learners

- Time `t` is measured in days. The study window is `[0, D)`, with review sessions at integer days `0, 1, ..., D-1`. The delayed test occurs at `T_test = D - 1 + RI`, where `RI` (retention interval, days) is measured from the last study session.
- A simulated learner holds `N` items. Every item is first studied at session 0 (initial encoding, not counted in the budget).
- Each item `i` has a synthetic difficulty that sets its initial forgetting rate `n_i(0)` (section 2.4).

### 2.2 Forgetting models (true memory of the simulated learner)

Let `Δ = t - t_r,i` be the time since the last review of item `i`, and `n_i` its current forgetting rate.

- **Exponential** (Ebbinghaus-style curve; form as in Tabibian et al. 2019, eq. 1): `m_i(t) = exp(-n_i Δ)`. Half-life `h_i = ln 2 / n_i`, so `m = 2^(-Δ/h)` as in Settles and Meeder (2016), eq. 1.
- **Power law** (Tabibian et al. 2019, eq. 2): `m_i(t) = (1 + ω Δ)^(-n_i)`, with time-scale parameter `ω > 0` (1/day).

`m_i(t)` is a probability in `[0, 1]`, equal to 1 at `Δ = 0` and non-increasing in `Δ`.

### 2.3 Retrieval update

At a review at time `t`, the simulated recall outcome is `r ~ Bernoulli(m_i(t))`. The forgetting rate then updates multiplicatively (Tabibian et al. 2019, eq. 3, following Settles and Meeder 2016):

- success (`r = 1`): `n_i ← (1 - α) n_i`, with `0 < α < 1`;
- failure (`r = 0`): `n_i ← (1 + β) n_i`, with `β ≥ 0`;
- in both cases `t_r,i ← t`.

Within one session, item reviews are processed in a fixed, documented order (ascending item index) so that event ordering is deterministic.

### 2.4 Synthetic item difficulty

Initial half-life `h_i(0)` (days) is drawn per learner from one of three item distributions (planning assumptions):

| Name | Definition |
|---|---|
| `homogeneous` | `h_i(0) = h0` for all items |
| `lognormal` | `log h_i(0) ~ Normal(log h0, σ²)`, `σ = 0.75` |
| `bimodal` | 50/50 mixture of `h0/3` and `3 h0` |

For the exponential model `n_i(0) = ln 2 / h_i(0)`. For the power-law model `n_i(0)` is chosen so that the power-law curve has the same initial half-life: `n_i(0) = ln 2 / ln(1 + ω h_i(0))`.

### 2.5 Central parameter setting (planning assumption)

`N = 50` items, `D = 28` days, `RI = 7` days, budget `k = 4` reviews per item (`B = k N = 200` review events), `h0 = 54.0` days (fitted, section 15; draft planning value 1 day), `α = 0.4`, `β = 0.6`, `ω = 1` per day, item distribution `lognormal` with `σ = 0.759` (fitted, section 15; draft 0.75). Apart from `h0` and `σ` these values are not empirical estimates; their influence is examined in EXP-003.

## 3. Schedules (arms)

All arms place exactly `B` reviews inside sessions `1, ..., D-1`. Each arm may review an item at most once per session.

| Arm | Type | Rule |
|---|---|---|
| `uniform` (**baseline**) | fixed, non-adaptive | Each item gets `k` reviews at equally spaced sessions over the window, offsets staggered by item index to spread daily load. |
| `expanding` | fixed, non-adaptive | Each item gets `k` reviews with geometrically expanding gaps (ratio 2), scaled to end at session `D-1`. Pimsleur-style graduated intervals (as described in Settles and Meeder 2016, section 3.1). |
| `massed` | negative control | Each item gets its `k` reviews in the last `k` sessions of the window (cramming). |
| `leitner` | adaptive, model-free | Leitner boxes with intervals 1, 2, 4, 8, 16 days; success promotes, failure demotes to box 1 (variant shown in Settles and Meeder 2016, figure 3). Fixed daily capacity `c = B/(D-1)`, rounded with a documented carry so the total is exactly `B`; overdue items first, ties by lowest box then item index; spare capacity goes to the lowest-box items. |
| `greedy` | adaptive, model-based | Same daily capacity as `leitner`. Each session reviews the `c` items with the lowest predicted recall under the scheduler's model, using the scheduler's estimate of each item's state updated from observed outcomes. |

The `greedy` scheduler has access to the true model family and parameters in EXP-001 (oracle-model condition). EXP-002 removes that advantage.

**Why `uniform` is the baseline.** It is the simplest schedule that uses the budget and spaces practice: one parameter (the interval), no feedback, no memory model. A schedule that cannot beat equal spacing gives no reason for added complexity. `massed` is a sanity control, not the comparator: beating cramming is expected and uninformative.

## 4. Hypotheses (primary)

Primary contrast: `greedy` versus `uniform`, exponential model, central setting (EXP-001).

- **H0:** the mean paired difference in delayed recall, `E[R_greedy - R_uniform]`, equals 0.
- **H1 (two-sided):** the mean paired difference differs from 0.
- **Directional prediction (stated in advance, not tested separately):** `greedy > uniform`, because it allocates reviews to items whose predicted recall is lowest.
- **Disconfirmation.** The prediction is contradicted if the 95% confidence interval of the paired difference lies entirely below 0. If the interval contains 0 and lies within `[-δ, +δ]` with `δ = 0.02`, the arms are declared practically equivalent at this resolution. If it contains 0 but extends beyond `±δ`, the result is inconclusive. Non-significance is never reported as equivalence outside this rule.

## 5. Metrics

- **Primary metric:** delayed modelled recall `R = (1/N) Σ_i m_i(T_test)`, the mean true-model recall probability across a learner's items at the test time, in probability units (0 to 1). Direction: higher is better.
  - Justification: it answers the question directly (modelled recall), uses the exact model probability rather than a Bernoulli draw (lower variance, no extra noise), and is bounded and interpretable. It is "predicted retention" in the sense of section 10.
- **Secondary metrics:**
  1. Observed delayed recall: fraction of items recalled in one simulated Bernoulli test at `T_test` (observed retention, kept separate from predicted).
  2. Recall at `RI ∈ {1, 30}` days (EXP-003).
  3. Fraction of items with `m_i(T_test) ≥ 0.9` (mastery share).
  4. Minimum item recall and 10th percentile (equity across items).
  5. Scheduler calibration: mean absolute difference between the scheduler's predicted recall and the true `m_i` at review times (adaptive arms).
  6. Peak daily review load and number of sessions used (schedule burden).
  7. Runtime per run (seconds) and peak memory where feasible.

## 6. Experimental unit, seeds and sample size

- **Unit of analysis:** one simulated learner (one seed). Items within a learner share a schedule and a budget, so item outcomes are not independent; the learner-level mean `R` is the analysed quantity.
- **Matching:** common random numbers. For a given seed, every arm sees the same item difficulties and the same pre-drawn uniform random stream per (item, review index) and per item for the test draw. Arms are compared by paired differences per seed.
- **Seeds:** 50 seeds per cell (well above the minimum of 5 per stochastic arm). Seed list: `1000, 1001, ..., 1049`, fixed in advance.
- **Sample-size rationale:** a run takes far less than one second in a NumPy implementation (to be confirmed by the smoke run), so 50 seeds per cell is affordable across the full matrix. With 50 paired units, a 95% interval half-width is about `2 s / sqrt(50) ≈ 0.28 s`, where `s` is the standard deviation of paired differences; the interval is narrower than `δ = 0.02` when `s < 0.07`. The smoke run reports `s` and runtime. If `s ≥ 0.07`, the owner decides before the freeze whether to raise the seed count (a precision decision taken before any confirmatory result is seen). No seeds are added after confirmatory results are seen.

## 7. Uncertainty and analysis

- Per cell: mean, standard deviation, median and full per-seed distribution of `R` for each arm.
- Paired difference versus `uniform` per seed; mean difference with a 95% percentile bootstrap interval over seeds (10,000 resamples, bootstrap seed 20261124), plus a paired t interval as a cross-check. Effect size: mean difference in probability units and relative change `(R_arm - R_uniform) / R_uniform`; standardized paired effect `d_z` reported as secondary.
- Secondary contrasts (other arms versus `uniform`): Holm adjustment across the four contrasts within a cell for any statement of difference. Sweeps in EXP-003 are descriptive (no hypothesis tests); they report intervals and rank changes.
- Deterministic quantities (for example the `homogeneous` distribution with no randomness in the non-adaptive arms) are reported as exact values, without manufactured intervals.

## 8. Inclusion, exclusion and stopping rules

- **Inclusion:** every planned run of the frozen matrix.
- **Exclusion:** a run is excluded only if it fails a validation check (probability out of `[0, 1]`, budget not exactly `B`, a review outside the window, non-monotone event times, NaN). Excluded runs are kept in raw results with the reason, counted and reported; no exclusion based on outcome values.
- **Stopping:** the full matrix runs to completion. If a bug is found after confirmatory runs start, the run stops, the bug is logged as a deviation, and the corrected matrix is rerun in full under a dated amendment; both result sets are kept.
- **Compute budget:** local laptop only (section 10). Cap of 2 hours wall-clock for the full matrix of all experiments; if exceeded, reduce EXP-003 sweep levels by an owner-approved amendment before the freeze, never the seed count of EXP-001.

## 9. Smoke matrix and full matrix

| Matrix | Content | Runs |
|---|---|---|
| Smoke (exploratory) | exponential, central setting, `N = 10`, 5 arms, seeds 1 to 5 (disjoint from the confirmatory seed list, so no confirmatory learner is seen before the freeze) | 25 |
| EXP-001 (confirmatory) | exponential, central setting, 5 arms, 50 seeds | 250 |
| EXP-002 (confirmatory) | true model power law; `greedy` scheduler with matched model (`greedy-power`) and misspecified model (`greedy-exp`, assumes exponential with the same initial half-life); plus `uniform`, `expanding`, `massed`, `leitner`; 50 seeds | 300 |
| EXP-003 (descriptive) | 2 models × budget `k ∈ {2, 4, 8}` × `RI ∈ {1, 7, 30}` × 3 item distributions × 5 arms × 50 seeds (greedy matched to true model) | 13,500 |

## 10. Sensitivity analyses that could invalidate the main interpretation

1. **Oracle advantage (EXP-002).** In EXP-001 the adaptive scheduler knows the true model. If its advantage over `uniform` disappears or reverses when its model is misspecified (`greedy-exp` on power-law learners), the EXP-001 result reflects privileged model knowledge, not a property of adaptive scheduling. This is the principal invalidation test.
2. **Retention interval (EXP-003).** Cepeda et al. (2006, 2008) report that the best spacing depends on the retention interval. If the ranking of arms reverses between `RI = 1` and `RI = 30`, no single schedule "maximizes recall"; the answer must be stated conditional on `RI`.
3. **Metric choice.** If `greedy` wins on mean recall but loses on minimum item recall or mastery share, the conclusion is limited to the mean.
4. **Budget level and item distribution (EXP-003).** Rank reversals across `k` or difficulty distributions limit generality.

## 11. Confounders and threats (summary; full list in `research/limitations.md`)

Unequal effective budget (controlled by exact `B` for every arm), daily load differences (reported), event ordering within a session (fixed rule), scheduler information advantage (EXP-002), parameter choices (EXP-003), and the validity of the memory model itself (not testable here).

## 12. Predicted versus observed

"Predicted" retention is the true-model probability `m_i(T_test)` (primary). "Observed" retention is one Bernoulli test draw per item (secondary). The scheduler's own predicted recall is a third quantity, used only for calibration (secondary metric 5). None of these is human data.

## 13. Reproducibility

Each run records config, seed, code revision, package versions, OS, CPU, runtime and peak memory in a versioned JSON result schema (M2). Commands will be fixed in `research/experiments/EXP-NNN/reproduction.md` before the freeze.

## 14. Freeze procedure

1. Owner reviews this draft and the three experiment protocols.
2. Changes requested by the owner are applied; version becomes v1.0.
3. The owner approves; the SHA-256 of each frozen protocol file and the commit are recorded in `research/decision_log.md` and `research/experiment_registry.csv`.
4. Only then are EXP-001 to EXP-003 run as confirmatory.

## References (verified as described in `research/literature_review.md`)

- Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. Psychological Bulletin, 132(3), 354-380. https://doi.org/10.1037/0033-2909.132.3.354
- Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. Psychological Science, 19(11), 1095-1102. https://doi.org/10.1111/j.1467-9280.2008.02209.x (metadata only)
- Settles, B., & Meeder, B. (2016). A trainable spaced repetition model for language learning. ACL 2016, 1848-1858. https://doi.org/10.18653/v1/P16-1174
- Tabibian, B., Upadhyay, U., De, A., Zarezade, A., Schölkopf, B., & Gomez-Rodriguez, M. (2019). Enhancing human learning via spaced repetition optimization. PNAS, 116(10), 3988-3993. https://doi.org/10.1073/pnas.1815156116 (content read in the arXiv version, arXiv:1712.01856)

## 15. Amendments before freeze (owner-approved 2026-11-24, round 2)

Authority: the owner's answers "yes for all others" (amendments, first round) and "Approve all" (real data, second round), recorded in the coordinator's approvals file `labs/_shared/owner-approvals-2026-11-24b.md`, sections 1 and 7, MEMORY rows. Where this section and sections 1 to 14 differ, this section wins. Section 15.2 (the calibration method) was written and committed before any fit was made.

### 15.1 Approved amendments (section 7 of the approvals file)

Approved text: "Starting half-life h0 about 6 days, unless fitted from Duolingo. Greedy and Leitner cover every item (state the capacity and tie rule). 50 seeds. Keep EXP-003. EXP-003 retention cells must not reuse the same runs."

- **A1, central half-life.** `h0` and the `lognormal` spread `σ` are fitted from the Duolingo traces by the method of 15.2. The fitted values replace the planning values `h0 = 1` day and `σ = 0.75` in every confirmatory configuration (EXP-001, EXP-002 and the "other parameters central" of EXP-003). The approved fallback `h0 = 6` days (with `σ = 0.75`) applies only if the fit is declared unusable by rule 15.2.7. This answers AP-001.
- **A2, coverage, capacity and tie rules of the adaptive arms.** Capacity is unchanged: `c_s = floor(s B/(D-1)) - floor((s-1) B/(D-1))` for session `s = 1..D-1`, which sums exactly to `B`; at most one review per item per session. Every adaptive arm (`leitner`, `greedy`, `greedy-exp`, `greedy-power`) first reviews items that have not been reviewed since encoding (coverage rule). Because `B = k N >= N`, every item is reviewed at least once. After that:
  - `leitner` orders items by (due before not due, earliest due day, lowest box, lowest item index). Spare capacity therefore goes to not-yet-due items by earliest due day, then lowest box, then index. This is the ordering of AP-003 with the coverage rule added in front.
  - `greedy` (and its EXP-002 variants) orders items by (lowest predicted recall under the scheduler's own model, lowest item index).
  The full key, in order, is: coverage, then the arm's own key. This answers AP-003 and the starvation part of AP-002. The failure update (`β`) and the rest of the greedy rule are unchanged; the greedy rule may still concentrate later reviews on items with low predicted recall, and that behaviour is reported, not corrected.
- **A3, seeds.** 50 seeds per cell, as drafted (AP-004). No seed is added after a confirmatory result is seen.
- **A4, EXP-003 kept** with all 54 cells (AP-005 shows the compute cap is not binding).
- **A5, EXP-003 retention cells use separate runs.** Each `RI` level of EXP-003 gets its own disjoint seed block: `RI = 1` seeds 3000 to 3049, `RI = 7` seeds 3100 to 3149, `RI = 30` seeds 3200 to 3249 (configuration `seeds.block_by`, step 100). No EXP-003 run is shared between `RI` levels or with EXP-001 and EXP-002 (seeds 1000 to 1049). The `RI` cells are therefore independent samples and may be compared as such (this replaces the repeated-measures option of AP-006). The run count stays 13,500.

### 15.2 How the real data enters the study (calibration, method fixed before fitting)

The simulation stays the controlled part of the study. The real data sets two parameters of the simulated item population; it is never used to compare schedules.

1. **Dataset.** DS01, Settles (2017), "Replication Data for: A Trainable Spaced Repetition Model for Language Learning", Harvard Dataverse, doi:10.7910/DVN/N8XJME, version 1.0, file `settles.acl16.learning_traces.13m.csv.gz` (379,004,009 bytes), licence CC BY-NC 4.0. Downloaded by `scripts/download_duolingo.py`; size, MD5 and SHA-256 in `data/manifest.json`. The file is git-ignored: it is above the 20 MB commit limit and holds row-level data with pseudonymous learner identifiers. Only aggregate fitted values are committed.
2. **Rows and schema.** Columns `p_recall, timestamp, delta, user_id, learning_language, ui_language, lexeme_id, lexeme_string, history_seen, history_correct, session_seen, session_correct`. A row is excluded, with its reason counted, if a field is empty, a number does not parse, `delta < 0`, `history_seen < 1`, `history_correct` is outside `[0, history_seen]`, `session_seen < 1`, or `session_correct` is outside `[0, session_seen]`. Missing values are counted per column. Ingestion is a pure function (`memory_research.duolingo.ingest`).
3. **Calibration subset.** Valid rows with `history_seen = 1` and `delta > 0`. The learner had seen the lexeme exactly once before (the first exposure, our encoding), so the row measures recall at the first review, when the item's forgetting rate is still its initial value `n(0)`. This mirrors the simulation, where encoding at day 0 does not change `n`. The delay is `Δ = delta / 86400` days. Following Settles and Meeder (2016), the row contributes `session_seen` trials with `session_correct` successes at delay `Δ`.
4. **Split.** By learner: a learner is in the calibration split C if `int(sha256(user_id)[:8], 16)` is even, otherwise in the validation split V. All rows of a learner fall in one split. Only split C sets parameters.
5. **Per-lexeme estimate.** For each `lexeme_id` with at least 100 trials in split C, the half-life `ĥ` is the maximum-likelihood estimate under the exponential model `p = 2^(-Δ/h)` with binomial likelihood `Σ [k log p + (n - k) log(1 - p)]`, restricted to `h ∈ [0.01, 3650]` days. The log-likelihood is concave in the rate `λ = ln 2 / h`, so the estimate is found by bisection on the score in `log λ` (60 iterations). If the score has no sign change, the estimate sits at the nearer bound (for example, a lexeme recalled in every trial sits at 3650 days) and is counted as a boundary estimate.
6. **Fitted values.** `h0 = exp(median_ℓ log ĥ_ℓ)` (the median, which is the median of the simulated `lognormal` distribution) and `σ = 1.4826 × median_ℓ |log ĥ_ℓ - log h0|` (a robust standard deviation, insensitive to boundary estimates). Both are rounded to three significant figures and written into the configurations. Per-lexeme estimates include sampling noise, so `σ` is an upper estimate of the true spread; this is disclosed, not corrected. The pooled maximum-likelihood half-life over all split C rows is reported as a secondary value and is not used.
7. **Usability rule.** The fit is declared unusable, and the approved fallback (`h0 = 6` days, `σ = 0.75`) is used instead, if fewer than 200 lexemes are eligible, if more than 25% of eligible lexemes have a boundary estimate, or if `h0` falls outside `[0.25, 365]` days. The outcome is recorded either way.
8. **What is not calibrated.** `α`, `β`, `ω`, `N`, `D`, `RI`, `k` and the `bimodal` factor keep their planning values. The traces count the outcome of the first exposure in `history_correct` and give no separate encoding event, so the review updates cannot be separated from encoding without further assumptions; the forgetting-curve family (exponential or power law) remains a factor of the design (EXP-002, EXP-003), not a fitted choice. The calibration uses only the exponential form; under the power law the same `h0` is the initial half-life by construction (section 2.4).
9. **Second test (validation on split V).** The real data is not a second test of the hypotheses: Duolingo did not assign schedules at random, so the traces cannot compare `greedy` with `uniform`. The second test checks the calibration itself, on split V only, after the values from split C are fixed: (a) `h0` and `σ` recomputed on split V by the same method, with the relative differences; the calibration is flagged unstable if either differs by more than 25% (a disclosure; the split C values are used regardless); (b) held-out mean binomial log-loss per trial on split V calibration-subset rows of the calibrated population curve `p = 2^(-Δ/h0)`, compared with a constant predictor equal to the split C mean recall rate. Both are reported descriptively.
10. **Independence from the primary contrast.** The fit reads only DS01 recall rows. No simulation is run, no schedule arm is evaluated, and no paired difference enters the fit. A baseline-only diagnostic of the fitted setting (the `uniform` arm alone, exploratory seeds 1 to 30, no other arm) may be run after the fit to locate the regime relative to floor and ceiling; it shows no contrast.
11. **Journal.** The fit is an exploratory journal entry (`research/experiment_journal.jsonl`, CAL-001) with code revision, data SHA-256, counts and values; outputs in `results/exploratory/CAL-001/`.

### 15.3 Fitted values (recorded after the fit, CAL-001)

The fit ran once, at code revision `037b46e` (which already contained section 15.2), on DS01 with SHA-256 `26cf9b33f2e9b2e8aa9a8f262a017b30699ca2f625c56a12ce699d4ea7076873`. Output: `results/exploratory/CAL-001/calibration.json`; journal entry CAL-001.

- Ingestion: 12,854,226 rows, all valid (0 excluded, 0 missing values); 559,900 rows in the calibration subset (split C 276,676 rows, 415,315 trials, 31,234 learners; split V 283,224 rows, 427,005 trials, 31,271 learners).
- Split C: 738 eligible lexemes, 1 boundary estimate (0.14%). **`h0 = 54.0` days, `σ = 0.759`.** Usability rule 15.2.7 met, so these values are used. Pooled MLE half-life 54.2 days (secondary, unused).
- Validation on split V: `h0 = 55.2` days (+2.2%), `σ = 0.721` (-4.9%); not flagged unstable. Held-out log-loss per trial: calibrated curve 0.587, constant predictor (split C mean recall 0.898) 0.328. The single exponential curve through `p(0) = 1` predicts first-review recall worse than a constant: in the traces, recall stays near 0.9 even at short delays, which this model form cannot represent. This is disclosed as a limitation of the memory model, not corrected.
- Consequence for the regime (baseline-only diagnostic PROBE-005, `uniform` arm only, exploratory seeds 1 to 30, no contrast): mean baseline `R` at the fitted central setting is 0.959 under exponential forgetting and 0.810 under the power law. The draft setting sat at the recall floor (AP-001); the fitted setting sits near the ceiling for exponential learners, which compresses differences between arms. The owner's rule ("the fitted value wins") is applied as written; the regime is disclosed in the freeze record.

## 16. Pre-data amendment, round 3 (owner-approved 2026-11-24, round 3): recalibration

Authority: the owner's answer "Approve all" (2026-11-24, round 3) to the coordinator's list, recorded in `labs/_shared/owner-approvals-2026-11-24c.md`, section 2 (MEMORY: recalibration). Approved rule, quoted: "(a) Diagnose the misfit first. [...] (b) Move off the ceiling by changing the study design, not the fitted parameters. [...] (c) Then re-freeze." No confirmatory run has taken place. Each subsection below was written and committed before the computation it governs. Where this section and sections 1 to 15 differ, this section wins.

### 16.1 Rule (a): diagnosis of the forgetting-model misfit (method fixed before computing)

1. **Data.** The DS01 calibration subset of 15.2.3 and the learner split of 15.2.4, read from the processed arrays written by CAL-001 (`data/processed/DS01_first_review_subset.npz`, git-ignored; its SHA-256 is recorded with the result). Every curve below is fitted on split C only and evaluated on split V only. No simulation is run and no schedule arm is evaluated.
2. **Score.** Held-out mean binomial log-loss per trial on split V (the measure of 15.2.9b), with probabilities clipped to `[1e-12, 1 - 1e-12]`.
3. **Predictors compared.** All curves predict recall at the first review after a delay `Δ` (days) since the first exposure.
   - `constant`: the split C mean recall rate (as in 15.2.9b).
   - `exp-median`: `p = 2^(-Δ/h0)` with the frozen `h0 = 54.0` days (the 15.2.9b curve).
   - `exp-population`: the recall the simulated `lognormal` item population implies, `p = E[2^(-Δ/H)]` with `log H ~ Normal(log h0, σ²)`, `h0 = 54.0`, `σ = 0.759`, computed by 64-node Gauss-Hermite quadrature.
   - `power-median`: `p = (1 + ωΔ)^(-n)` with `ω = 1` per day and `n = ln 2 / ln(1 + ω h0)` (section 2.4, same initial half-life).
   - `power-population`: the same power law averaged over the `lognormal` population of initial half-lives, by the same quadrature.
   - `exp-mle`: the exponential curve with one pooled half-life fitted by maximum likelihood on split C (the pooled value of 15.2.6), the best single exponential curve.
   - `power-mle`: the power law with `ω = 1` per day and one pooled exponent `n` fitted by maximum likelihood on split C. The log-likelihood is concave in `n`; the estimate is found by bisection on the score in `log n` (60 iterations) over `n ∈ [ln 2 / 3650, ln 2 / 0.01]`, as in 15.2.5.
4. **Comparison and decision.** The exponential family is represented by the lowest held-out log-loss among `exp-median`, `exp-population` and `exp-mle`; the power-law family by the lowest among `power-median`, `power-population` and `power-mle`. The families are compared with each other and each with `constant`. A family "beats the constant" if its held-out log-loss is strictly lower than that of `constant`. If neither family beats the constant, this is recorded as a limitation, and the claims boundary states that every result is conditional on the assumed memory model and not supported by the real traces' first-review recall.
5. **Descriptive calibration table.** For split V, by delay bin (`Δ` < 1 hour, 1 hour to 1 day, 1 to 7 days, 7 to 30 days, 30 days or more): number of trials, observed recall rate and the mean prediction of every curve above.
6. **What rule (a) does not change.** No parameter of the simulation (`h0`, `σ`, `ω`, `α`, `β`) is refitted or changed by this diagnosis, whatever its outcome. The forgetting-model family stays a design factor (EXP-002, EXP-003).
7. **Journal.** Exploratory entry CAL-002 in `research/experiment_journal.jsonl`; output `results/exploratory/CAL-002/model_comparison.json`.

### 16.2 Rule (b): moving the central cell off the ceiling (rule fixed before applying it)

Approved target: "the baseline uniform schedule's recall lands in [0.4, 0.7] at the central cell", reached "by changing the study design, not the fitted parameters", with the baseline arm only.

1. **Central cell and measurement.** The central cell is the EXP-001 setting (exponential forgetting, `N = 50`, `D = 28`, `k = 4`, `h0 = 54.0` days, `σ = 0.759`, `α = 0.4`, `β = 0.6`, `lognormal` items). The quantity is the mean over exploratory seeds 1 to 30 (disjoint from every confirmatory seed) of the learner-level `R` of the `uniform` arm. No other arm is simulated and no contrast is computed. Because the uniform schedule does not depend on `RI`, one simulation per seed gives `R` at every `RI` (`memory_research.simulate.recall_at`); the selected value is then re-checked once with the standard runner (uniform arm only).
2. **Step 1, retention interval only (preferred; changes no parameter value).** Candidate `RI` are the integers 1 to 365 days. Among candidates whose baseline mean `R` lies in `[0.4, 0.7]`, choose the one closest to the midpoint 0.55; ties go to the smaller `RI`. If a candidate exists, the item population and every fitted value stay as frozen in v1.0, and step 2 is not used.
3. **Step 2, item-difficulty subset (only if step 1 finds no candidate).** The item population is restricted to the harder half of the vocabulary: split C eligible lexemes (15.2.5) whose split C recall rate is strictly below the median recall rate of eligible lexemes. `h0` and `σ` are the 15.2.6 statistics of these lexemes' per-lexeme estimates (the same estimator, applied to the chosen subset), rounded to three significant figures. Step 1 is then repeated with these values.
4. **Failure.** If step 2 also finds no candidate, nothing is re-frozen; the outcome is reported to the owner.
5. **Consequences fixed now, before the value is known.** The selected `RI*` replaces `RI = 7` as the central retention interval in EXP-001 and EXP-002 (EXP-002 shares the central setting). EXP-003 keeps its levels `RI ∈ {1, 7, 30}` and gains `RI*` as a fourth level (unless `RI*` already is one of them), so that the sweep contains the new central cell; that level gets its own disjoint seed block (`3000 + 100 × level index`, that is 3300 to 3349), and the run count becomes 2 × 3 × 4 × 3 × 5 × 50 = 18,000. The secondary metric "recall at `RI ∈ {1, 30}`" is unchanged. Seeds, arms, metrics, analysis and every other parameter are unchanged.
6. **Disclosure.** The baseline mean `R` under power-law forgetting at `RI*` (EXP-002's baseline, still the `uniform` arm alone) is recorded as well, descriptively; it plays no role in the selection.
7. **Journal.** Exploratory entries RI-001 (selection, `results/exploratory/RI-001/selection.json`) and PROBE-006 (runner re-check, `results/exploratory/PROBE-006/`).

### 16.3 Outcomes and applied changes (recorded after the computations)

**Rule (a), CAL-002** (method 16.1 committed at `664de3c`; output `results/exploratory/CAL-002/model_comparison.json`). Held-out log-loss per trial on split V (427,005 trials): `constant` 0.328; `exp-median` 0.587, `exp-population` 0.549, `exp-mle` 0.569 (pooled half-life 94.5 days); `power-median` 0.473, `power-population` 0.476, `power-mle` 0.428 (pooled exponent `n = 0.0764` with `ω = 1`). The power-law family fits better than the exponential family (0.428 against 0.549), but **neither family beats the constant predictor**. Observed split V recall is nearly flat in the delay: 0.912 below one hour, 0.905 from one hour to one day, 0.900 from 1 to 7 days, 0.890 from 7 to 30 days, 0.868 at 30 days or more. A curve that starts at `p(0) = 1` cannot represent recall that stays near 0.9 even at the shortest delays. Consequences, as 16.1.4 and 16.1.6 require:

- **Limitation.** Neither forgetting model used by the simulation predicts the real first-review recall of DS01 better than a constant. The real data calibrates the time scale of the simulated item population (`h0`, `σ`); it does not validate the memory model.
- **Claims boundary (model dependence).** Every result of EXP-001 to EXP-003 is a property of the assumed memory model (exponential or power-law forgetting with multiplicative updates, section 2), conditional on that model. No result is a claim about the schedules' effect on Duolingo learners or on any human learner, and the DS01 calibration does not turn it into one.
- No parameter is changed by rule (a).

**Rule (b), RI-001 and PROBE-006** (rule 16.2 committed at `8d4854a`; outputs `results/exploratory/RI-001/selection.json`, `results/exploratory/PROBE-006/`). Uniform arm only, exponential learners, exploratory seeds 1 to 30. Baseline mean `R` is non-increasing in `RI` (checked): 0.982 at `RI = 1`, 0.959 at 7, 0.895 at 30, 0.776 at 90, 0.652 at 180, 0.483 at 365. Candidates in `[0.4, 0.7]`: `RI` 142 to 365 days. Step 1 succeeds: **`RI* = 281` days, baseline mean `R` 0.550** (per seed 0.454 to 0.606). Step 2 (difficulty subset) is not used, so no parameter value changes. The runner re-check (PROBE-006) gives the same mean. Descriptive (16.2.6): the power-law baseline at `RI = 281` is 0.680. No other arm was simulated and no contrast was computed at any `RI`.

**Applied changes (v1.1).**

- B1. Central retention interval `RI = 281` days in EXP-001 and EXP-002 (replacing 7). The delayed test is at `T_test = 27 + 281 = 308` days.
- B2. EXP-003 levels `RI ∈ {1, 7, 30, 281}`; the new level has seed block 3300 to 3349; 72 cells, 18,000 runs. The other three blocks are unchanged.
- Unchanged: `h0 = 54.0` days, `σ = 0.759`, `ω`, `α`, `β`, `N`, `D`, `k`, arms, seeds 1000 to 1049 for EXP-001 and EXP-002, metrics, analysis, `δ`.
- Sample size: the seed-spread estimate of section 6 has not been re-measured at `RI = 281`, because measuring it needs a second arm (a contrast), which rule (b) forbids. The 50 seeds stay as approved; the achieved interval width is reported with the results.

### 16.4 Re-freeze (rule (c))

The SHA-256 values of v1.1 (this file, the three experiment protocols and the three configurations) are in `research/freeze.json`, which keeps the v1.0 values under `superseded` with the reason, and extends the C4 disclosure with everything seen in rounds 1 to 3. The guard accepts only the v1.1 configurations.
