<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# EXP-003 protocol: robustness sweep over models, budgets, retention intervals and item distributions

**Status: FROZEN v1.0 (owner-approved 2026-11-24, round 2), not yet run. Protocol hash: recorded in `research/freeze.json` and `research/experiment_registry.csv`.** Descriptive (no hypothesis tests). Depends on EXP-001 and EXP-002 engines. Shared definitions: `research/protocol.md`.

## 1. Precise question

Across forgetting models, study budgets, retention intervals and item-difficulty distributions, does the ranking of schedules by mean delayed modelled recall stay the same as at the central setting?

## 2. Mechanism and rationale

Cepeda et al. (2006, abstract) report that the inter-study interval that maximizes retention increases with the retention interval. A schedule that wins at `RI = 7` may lose at `RI = 1` (recency favours late reviews) or at `RI = 30`. Item heterogeneity determines how much difficulty targeting can gain: with `homogeneous` items an adaptive scheduler has little to target.

## 3. Competing explanations

Rank changes may reflect the budget-capacity rule rather than spacing (load reported), or parameter regions where all arms are near floor or ceiling (reported as such).

## 4. Hypotheses

None tested. Pre-stated expectations (not confirmatory): (E1) `massed` improves relative to `uniform` as `RI` decreases; (E2) the `greedy` advantage over `uniform` is smallest for `homogeneous` items. A rank reversal relative to EXP-001 in any cell limits the generality of the EXP-001 conclusion.

## 5. Estimand

Per cell, mean `R` per arm and mean paired difference versus `uniform`, with intervals; rank order of arms.

## 6. Unit and scope

Simulated learner. Full factorial: model {exponential, power law (`ω = 1`)} × `k ∈ {2, 4, 8}` × `RI ∈ {1, 7, 30}` × distribution {homogeneous, lognormal, bimodal} = 54 cells; 5 arms per cell (`greedy` matched to the true model); other parameters central.

## 7. Variables

Independent: the four factors and arm. Dependent: primary metric and secondary metrics 3 and 4.

## 8. Treatment and control

Control `uniform` in every cell.

## 9. Seeds

Seeds 1000 to 1049 in every cell (common random numbers within a cell).

## 10. Sample size

50 seeds per cell, 13,500 runs. Descriptive; intervals reported without multiplicity adjustment and labelled as such.

## 11. Compute budget

Hard cap 90 minutes wall-clock (study cap 2 hours). If the smoke-run timing predicts more, the owner reduces factor levels before the freeze.

## 12. Metrics

As EXP-001.

## 13. Uncertainty

Per-cell bootstrap intervals for paired differences (10,000 resamples). Rank stability reported as the share of seeds in which each arm ranks first.

## 14. Exclusion and stopping

As study protocol section 8.

## 15. Failure modes

Floor effects at `k = 2`, `RI = 30` (all recalls near zero) make differences uninformative; reported as such. For `homogeneous` items under non-adaptive arms the outcome is deterministic up to the test draw; exact values reported.

## 16. Sensitivity

This experiment is itself the sensitivity analysis for parameter range and item distribution.

## 17. Reproducibility commands

To be fixed in M2, before the freeze.

## Amendments before freeze (owner-approved 2026-11-24, round 2)

Applied from study protocol section 15; these lines override the sections above where they differ.

- Kept with all 54 cells (A4). Other parameters central: `h0 = 54.0` days, `σ = 0.759` (fitted, study protocol 15.2 and 15.3).
- Section 9 is replaced: each `RI` level has its own seed block, `RI = 1` seeds 3000 to 3049, `RI = 7` seeds 3100 to 3149, `RI = 30` seeds 3200 to 3249 (A5). Within a cell all arms share common random numbers; no run is shared across `RI` levels or with EXP-001 and EXP-002. `RI` cells are independent samples.
- Adaptive arms follow the coverage-first rules of study protocol 15.1 (A2).
- Run count 13,500 (unchanged).
- Reproduction: `uv sync --frozen`, then `uv run python -m memory_research run --config research/experiments/EXP-003/config.json --report --pdf`. The guard accepts only the configuration whose canonical hash is in `research/freeze.json`.
