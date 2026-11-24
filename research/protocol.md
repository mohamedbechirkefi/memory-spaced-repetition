<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# MEMORY study protocol

**Status: DRAFT v0.1 (2026-11-24). NOT FROZEN.** Freezing is the owner's decision (G-FREEZE). No confirmatory run may start until the owner approves a frozen version and its hash is recorded in `research/decision_log.md` and `research/experiment_registry.csv`. All numerical settings below are planning assumptions for a simulation; none is calibrated to human data.

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

`N = 50` items, `D = 28` days, `RI = 7` days, budget `k = 4` reviews per item (`B = k N = 200` review events), `h0 = 1` day, `α = 0.4`, `β = 0.6`, `ω = 1` per day, item distribution `lognormal`. These values are not empirical estimates; their influence is examined in EXP-003.

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
