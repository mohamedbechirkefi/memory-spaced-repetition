<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# EXP-002 protocol: oracle advantage and model misspecification under power-law forgetting

**Status: FROZEN v1.0 (owner-approved 2026-11-24, round 2), not yet run. Protocol hash: recorded in `research/freeze.json` and `research/experiment_registry.csv`.** Depends on EXP-001 (shared engine and analysis). Shared definitions: `research/protocol.md`.

## 1. Precise question

When simulated learners forget by a power law, does the greedy schedule still differ from uniform review in mean delayed modelled recall, (a) when the scheduler uses the true power-law model and (b) when it wrongly assumes exponential forgetting?

## 2. Mechanism and rationale

In EXP-001 the greedy scheduler knows the true model and parameters, an advantage no real scheduler has. Tabibian et al. (2019; arXiv:1712.01856) state both exponential and power-law forms; the power law has a heavier tail, so an exponential scheduler underestimates long-delay recall for those learners and may over-review. This is the principal test that could invalidate the interpretation of EXP-001.

## 3. Competing explanations

A greedy advantage that survives misspecification may still depend on matched initial half-lives (both schedulers are given the true initial half-life of each item). This information advantage remains and is stated as a limitation.

## 4. Hypotheses

- H0a: `E[R_greedy-power - R_uniform] = 0`; H1a two-sided.
- H0b: `E[R_greedy-exp - R_uniform] = 0`; H1b two-sided.
- Holm adjustment over these two primary contrasts of EXP-002.
- **Interpretation rule:** if EXP-001 shows a positive difference and H0b is not rejected with an interval inside `±0.02`, or the interval is entirely below 0, the EXP-001 advantage is declared dependent on model knowledge.

## 5. Estimand

Mean paired differences versus `uniform` for `greedy-power` and `greedy-exp`, probability units.

## 6. Unit and scope

Simulated learner (seed); power-law true model with `ω = 1` per day, initial half-life matched as in study protocol section 2.4; otherwise the central setting.

## 7. Variables

Independent: arm (`uniform`, `expanding`, `massed`, `leitner`, `greedy-power`, `greedy-exp`). Dependent: as EXP-001. The `greedy-exp` scheduler converts each item's true initial half-life into an exponential rate `ln 2 / h_i(0)` and uses `α`, `β` as given.

## 8. Treatment and control

Treatments: `greedy-power`, `greedy-exp`. Control: `uniform`.

## 9. Seeds

Seeds 1000 to 1049, the same seed list as EXP-001; common random numbers across all six arms.

## 10. Sample size

50 seeds, as EXP-001, same rationale.

## 11. Compute budget

300 runs; hard cap 10 minutes.

## 12. Metrics

As EXP-001. Calibration (secondary metric 5) is the key diagnostic for `greedy-exp`.

## 13. Uncertainty

As EXP-001, with Holm adjustment over the two primary contrasts.

## 14. Exclusion and stopping

As study protocol section 8.

## 15. Failure modes

Power-law curves with large `n` may produce near-zero recall; numeric check that `(1 + ωΔ)^(-n)` is evaluated as `exp(-n log1p(ωΔ))` for stability.

## 16. Sensitivity

Repeat the two primary contrasts with `ω ∈ {0.3, 3}` as a descriptive check (owner may drop before freeze if over budget; 600 extra runs).

## 17. Reproducibility commands

To be fixed in M2, before the freeze.

## Amendments before freeze (owner-approved 2026-11-24, round 2)

Applied from study protocol section 15; these lines override the sections above where they differ.

- Central setting: `h0 = 54.0` days and `σ = 0.759` (fitted, study protocol 15.2 and 15.3).
- `leitner`, `greedy-power` and `greedy-exp`: coverage-first capacity and tie rules of study protocol 15.1 (A2).
- Seeds 1000 to 1049 (50 seeds, A3), unchanged.
- Reproduction: `uv sync --frozen`, then `uv run python -m memory_research run --config research/experiments/EXP-002/config.json --report --pdf`. The guard accepts only the configuration whose canonical hash is in `research/freeze.json`.
