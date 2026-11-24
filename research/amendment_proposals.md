<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Protocol amendment proposals for the owner (pre-freeze)

**Status: proposals only, written by the M2 session on 2026-11-24. None is applied.** The draft protocol (`research/protocol.md`, DRAFT v0.1) and the three experiment protocols are unchanged. Accepting, changing or rejecting each proposal, and freezing, is the owner's decision (G-FREEZE).

Every number below comes from the exploratory planning runs of 2026-11-24 (code revision `bad36ee`), all on seeds 1 to 30 or 1 to 5, disjoint from the confirmatory seed list 1000 to 1049. The runs are exploratory, recorded in `research/experiment_journal.jsonl`, stored under `results/exploratory/`, and are not findings. They are reported here only because protocol section 6 and the M2 brief ask the smoke run to check planning values before the freeze.

**Disclosure.** To measure the spread of paired differences, the probes necessarily computed arm contrasts at the draft central setting (PROBE-001, PROBE-002) and in the 54 sweep cells (PROBE-003). The owner and the session have therefore seen the direction of those exploratory contrasts before the freeze. Any amendment chosen below should be justified by the planning diagnostics (floor level, starvation, runtime, spread), not by which arm looked better. The floor probe PROBE-004 ran the baseline arm only, so it shows no contrast.

## AP-001: the central setting sits at the recall floor

- **Observation.** With `h0 = 1` day, uniform gaps of about 6.75 days and `RI = 7`, the baseline `uniform` has mean delayed recall `R = 0.0295` (PROBE-001, 30 seeds); every arm has mean `R < 0.10`, and `leitner` and `greedy` have `R < 0.01` for every seed. In the EXP-003 scan (PROBE-003, 5 seeds per cell), the baseline has `R < 0.10` in 34 of 54 cells and at most `0.290` in any cell.
- **Why it matters.** At the floor, all differences are compressed towards 0, the primary metric loses resolution, and the question "which schedule maximizes recall" is answered in a regime where almost nothing is remembered.
- **Baseline-only diagnostic (PROBE-004, uniform arm, 5 seeds, central otherwise).** Mean `R` of `uniform` by initial half-life: `h0 = 1`: 0.0295; `2`: 0.0983; `4`: 0.2791; `8`: 0.5571; `16`: 0.8022 days.
- **Proposal.** Choose the central `h0` (or, equivalently, the window, budget or `RI`) so that the baseline is away from floor and ceiling, using the baseline level only. For example `h0 = 4` or `h0 = 8` days puts the baseline between about 0.28 and 0.56 in this probe. Re-centre the EXP-003 sweep the same way. Alternative: keep `h0 = 1` and state explicitly that the study addresses a high-difficulty regime.

## AP-002: the failure update makes the greedy rule review hopeless items

- **Observation.** Under the draft update, a failed review multiplies the forgetting rate by `1 + β = 1.6`. Reviewing an item that is already forgotten therefore makes it worse. The draft `greedy` rule reviews the items with the lowest predicted recall, which are exactly those items. In PROBE-001 it left on average 35.7 of 50 items never reviewed and reviewed single items up to 27 times (once per session), with a review success rate of 0.007. `greedy-power` and `greedy-exp` behave the same way under power-law learners (PROBE-002: 38.5 and 34.0 of 50 items never reviewed).
- **Why it matters.** EXP-001's primary contrast would then test a degenerate adaptive rule, not adaptive scheduling as practised or as analysed in the literature. This is a fairness problem in the opposite direction of a strawman baseline: the treatment is a strawman.
- **Options for the owner (not implemented).** (a) Keep the rule and report the pathology as the result (honest, but narrow). (b) A threshold rule: each session review the items whose predicted recall has fallen below a target `r*` (for example 0.9), most at risk first, with a documented rule for spare capacity. (c) A MEMORIZE-style rule (Tabibian et al. 2019) with review intensity proportional to `1 - m`. (d) Change the failure semantics, for example `β = 0` or a failed review followed by corrective feedback that re-encodes the item. Options (b) to (d) change the protocol and must be decided before the freeze.

## AP-003: the Leitner priority rule is ambiguous and starves items

- **Observation.** The draft text reads "overdue items first, ties by lowest box then item index". Implemented literally (key: not due, box, item index), low-index items that fail return to box 1 and are due again the next day, so they monopolise the daily capacity. In PROBE-001 `leitner` left on average 31.0 of 50 items never reviewed.
- **Proposal.** Among due items, order by due day (oldest first), then box, then item index; give spare capacity to the lowest box, then the earliest due day. The current implementation keeps the literal draft rule until the owner decides.

## AP-004: seed count (protocol section 6 rule)

- **Observation.** SD of paired differences versus `uniform` at the central setting (30 seeds): PROBE-001 `s` from 0.0152 to 0.0174 (projected 95% half-width with 50 seeds 0.0043 to 0.0050); PROBE-002 `s` from 0.0205 to 0.0249 (half-width 0.0058 to 0.0071). Over the 216 sweep contrasts of PROBE-003 (5 seeds each, rough estimates) the median `s` is 0.0193 and the maximum 0.0714 (one contrast above 0.07).
- **Reading.** Under the draft rule (`s < 0.07`), 50 seeds are adequate at the central setting. These spreads are measured at the floor (AP-001) and are compressed by it; they must be re-measured after AP-001 and AP-002 are settled.
- **Proposal.** Keep 50 seeds as the minimum, re-run the planning probe on seeds 1 to 30 after the amendments, and consider raising the seed count (AP-005 shows the cost is negligible). The decision must be taken before any confirmatory result is seen.

## AP-005: compute budget is not binding

- **Observation.** Mean runtime per run between 0.77 ms (PROBE-001) and 3.76 ms (PROBE-004) across the five exploratory matrices; medians 0.72 to 0.92 ms; maximum single run 91 ms (PROBE-003); process peak resident memory at most 42.0 MiB. The run-to-run variation is dominated by machine load, not by the arms.
- **Projection.** The draft full matrix has 14,050 runs (EXP-001 250, EXP-002 300, EXP-003 13,500), plus 600 runs for the optional EXP-002 `ω` check. At the median runtime (about 0.8 ms) that is about 12 s; at the slowest observed mean (3.76 ms) about 55 s. PROBE-003 itself ran 1,350 runs in 3.57 s wall clock. This is far below the 2-hour cap of protocol section 8 and the 10-minute caps of EXP-001 and EXP-002.
- **Proposal.** No EXP-003 level needs to be cut for compute reasons. Update the planning text of protocol section 6 ("far less than one second") with the measured values.

## AP-006: retention-interval cells of EXP-003 share their runs

- **Observation.** No arm's schedule depends on `RI` (the fixed arms by construction; `leitner` and `greedy` are myopic). For a fixed (model, `k`, distribution, seed), the three `RI` cells therefore have identical schedules and review outcomes and differ only in the evaluation time. The engine already records recall at `RI` of 1, 7 and 30 days in every run (`recall_mean_at_ri`).
- **Proposal.** Treat the `RI` levels of EXP-003 as repeated measures of the same runs, not as independent cells (no pooling across `RI` as if independent), or compute them from one run per (model, `k`, distribution, seed), which divides the EXP-003 run count by three. This changes the analysis description, so it is the owner's decision.
