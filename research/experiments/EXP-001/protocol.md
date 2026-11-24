<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# EXP-001 protocol: schedule comparison under exponential forgetting

**Status: FROZEN v1.0 (owner-approved 2026-11-24, round 2), not yet run. Protocol hash: recorded in `research/freeze.json` and `research/experiment_registry.csv`.** Shared definitions are in `research/protocol.md` (FROZEN v1.0); where this file and the study protocol differ, the study protocol wins.

## 1. Precise question

Under exponential forgetting with multiplicative retrieval updates, at the central parameter setting, does a model-based greedy schedule produce a different mean delayed modelled recall than equal-interval (uniform) review, with the same total budget of review events?

## 2. Mechanism and rationale

Under `m = exp(-n Δ)`, recall decays fastest for items with high forgetting rate `n`. A successful review multiplies `n` by `(1 - α)` and a failure by `(1 + β)`. Uniform review spends the same number of reviews on easy and hard items. A scheduler that reviews the items with the lowest predicted recall should move reviews from easy items to hard ones. Tabibian et al. (2019; arXiv:1712.01856, sections on the memory model and MEMORIZE) derive an optimal review intensity proportional to `1 - m(t)` under a soft review cost; Settles and Meeder (2016, section 3) describe the fixed Pimsleur and adaptive Leitner schedules. Cepeda et al. (2006, abstract) report that the best spacing depends on the retention interval.

## 3. Competing explanations

- Any greedy advantage may come from end-of-window placement (reviewing close to the test) rather than from difficulty targeting. Control: the `massed` arm isolates pure recency; the `expanding` arm isolates late placement without feedback.
- The advantage may come from oracle knowledge of the true model (tested in EXP-002).
- Daily capacity rules may favour one arm (load reported as a secondary metric).

## 4. Hypotheses

- H0: `E[R_greedy - R_uniform] = 0`. H1 (two-sided): `E[R_greedy - R_uniform] ≠ 0`. Directional prediction: positive.
- **Contradicting result:** a 95% bootstrap interval of the paired difference entirely below 0. **Practical equivalence:** interval within `[-0.02, +0.02]`. Otherwise inconclusive.

## 5. Estimand

Mean over simulated learners (population defined by the seed list and the central setting) of the paired difference `R_greedy - R_uniform`, in probability units.

## 6. Experimental unit and scope

Unit: one simulated learner (seed). Scope: synthetic items only, exponential forgetting, central setting: `N = 50`, `D = 28`, `RI = 7`, `k = 4` (`B = 200`), `h0 = 1` day, `α = 0.4`, `β = 0.6`, `lognormal` difficulty with `σ = 0.75`.

## 7. Variables

- Independent: schedule arm (`uniform`, `expanding`, `massed`, `leitner`, `greedy`).
- Dependent: primary `R` (mean `m_i(T_test)`); secondary metrics 1, 3, 4, 5, 6, 7 of the study protocol.
- Held constant: all model parameters, budget, window, test time.

## 8. Treatment and control

Treatment: `greedy` (oracle model). Control (baseline): `uniform`. Additional arms: `expanding`, `leitner` (secondary contrasts), `massed` (negative control).

## 9. Sampling and seeds

Seeds 1000 to 1049 (50 learners). Common random numbers across arms: item difficulties and uniform streams per (item, review index) and per item for the test are drawn from the seed before any arm runs.

## 10. Sample-size rationale

As in study protocol section 6: with 50 paired units the 95% half-width is about `0.28 s`; adequate when `s < 0.07`. The exploratory smoke run will report `s`; any change of the seed count is the owner's decision before the freeze.

## 11. Compute budget

Expected below one minute for 250 runs (to be measured in the smoke run). Hard cap: 10 minutes wall-clock on the local laptop.

## 12. Metric formulas and units

- `R = (1/N) Σ_i m_i(T_test)`, probability units, higher is better.
- Observed recall: `(1/N) Σ_i 1[u_i,test < m_i(T_test)]` with pre-drawn `u_i,test ~ Uniform(0,1)`.
- Mastery share: `(1/N) Σ_i 1[m_i(T_test) ≥ 0.9]`.
- Equity: `min_i m_i(T_test)` and 10th percentile.
- Calibration (adaptive arms): mean of `|m̂_i(t) - m_i(t)|` over review events, where `m̂` is the scheduler's prediction.

## 13. Uncertainty method

Paired differences per seed; mean with 95% percentile bootstrap interval (10,000 resamples, bootstrap seed 20261124); paired t interval as a cross-check; Holm adjustment over the four arm-versus-uniform contrasts for secondary statements; full per-seed distributions reported.

## 14. Exclusion and stopping rules

As in study protocol section 8. No outcome-based exclusion. All 250 runs reported.

## 15. Anticipated failure modes

Budget rounding errors in daily capacity; ties in greedy selection (broken by item index); floating-point underflow of `m` for very hard items at long delays (values below 1e-300 are reported as computed, not clipped); Leitner leaving capacity unused (forbidden by the rule, checked by test).

## 16. Sensitivity tests

Main invalidation test is EXP-002 (oracle advantage). Within EXP-001: report the primary contrast with the observed-recall metric and with the equity metrics; if the sign differs from the primary metric, the conclusion is restricted to the mean.

## 17. Reproducibility commands (to be fixed in M2, before the freeze)

Planned: `uv sync --frozen`, then a CLI of the form `uv run python -m memory_research.run --config research/experiments/EXP-001/config.json`. Not implemented yet.

## Amendments before freeze (owner-approved 2026-11-24, round 2)

Applied from study protocol section 15; these lines override the sections above where they differ.

- Central setting: `h0 = 54.0` days and `σ = 0.759` (fitted from DS01, study protocol 15.2 and 15.3), replacing `h0 = 1` day and `σ = 0.75` in section 6.
- `leitner` and `greedy`: coverage-first capacity and tie rules of study protocol 15.1 (A2).
- Seeds 1000 to 1049 (50 seeds, A3), unchanged.
- Reproduction: `uv sync --frozen`, then `uv run python -m memory_research run --config research/experiments/EXP-001/config.json --report --pdf`. The guard accepts only the configuration whose canonical hash is in `research/freeze.json`.
