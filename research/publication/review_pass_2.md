<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Second review pass (master prompt 11.5), M4, 2026-11-25

**Purpose.** To argue against the preferred hypothesis, not to polish. The preferred hypothesis of the study, stated before the runs, is that the model-based greedy scheduler beats uniform review (EXP-001), and the M3 reports read EXP-002 as showing that this advantage "reflects privileged model knowledge, not a property of adaptive scheduling as such". Both readings are challenged here. Internal quality control by the session; not external peer review.

**Material reviewed.** The three M3 experiment reports, the claims register as of M3, the first M4 synthesis of the manuscript and the exploratory SENS-001 output. The manuscript was synthesized in the same session as this pass; the changes listed below were applied to the manuscript, the reports and the claims register in response to it.

## 1. Challenges

| # | challenge (strongest alternative reading) | evidence | verdict | change made |
|---|---|---|---|---|
| C1 | The EXP-001 advantage is a seed-block accident. | Replicates on two independent blocks: 0.0167 [0.0113, 0.0218] (EXP-003 C044) and 0.0193 [0.0147, 0.0236] (SENS-001). | Does not hold. | Replications reported in manuscript 5.1 and CLM-010. |
| C2 | The 281-day test was chosen in a way that favours greedy. | The choice used the uniform arm alone. On the same learners greedy also beats uniform at `RI` 1, 7 and 30 (0.0076, 0.0189, 0.0392; all intervals above 0). | Does not hold for EXP-001. | Reported in 5.1. |
| C3 | Greedy wins by reviewing near the test (recency), not by targeting. | Same daily capacity and mean review day as uniform (14.065); last-review day slightly earlier (23.978 against 24.180); hard third gets 5.326 reviews, easy third 2.714. | Does not hold. | Table 6 and the EXP-001 report addendum. |
| C4 | The EXP-002 "equivalent within 0.02" verdict is robust evidence that a misspecified scheduler gains nothing. | Bootstrap upper bound 0.0195, 0.0005 inside the margin; paired t upper bound 0.0201, outside it. On independent seeds 0.0098 [0.0007, 0.0187], above 0. At `RI` 7 and 30, 0.0213 with intervals above 0. | **Holds.** The verdict stands as a frozen result, but the categorical label is fragile; the misspecified scheduler keeps a small positive difference near 0.01 in most checks. | Manuscript abstract, 5.2, 5.4 and 6 rewritten around the size of the reduction (about three quarters) rather than the label; EXP-002 report "Observed" and "Null result" bullets qualified, addendum added; CLM-005 qualified; CLM-009 added. The M3 wording "reflects privileged model knowledge, not a property of adaptive scheduling as such" is replaced by "declared dependent on model knowledge" plus the quantitative statement. |
| C5 | Even `greedy-exp` is an oracle: it knows each item's true initial half-life, so EXP-002 does not test a realistic scheduler. | Both greedy arms receive the true initial half-lives (protocol EXP-002 section 3). | **Holds** (known, not testable with the frozen design). | Stated as an upper bound in the discussion and as an open competing explanation in Table 6. |
| C6 | EXP-003 instability is noise or ceiling compression. | 70 of 72 cells have a reversal whose pairwise interval excludes 0; 54 of 56 without the ceiling cells; top arm resolved in 59 cells. | Does not hold. | Reported in 5.3, S4.3, CLM-012. E2's signed-difference reading disclosed. |
| C7 | "Massed is the most frequent winner" invites the reading that cramming is good. | Massed wins mostly under the power law (24 of 36 cells) and does so at 50 reviews per session, against 8 for the spread arms; the model has no gap-dependent update. | **Holds** as an overgeneralization risk. | Abstract, 5.3 and conclusion now state the load and the model mechanics next to the count. |
| C8 | The mastery-share reversal is presented as a substantial cost. | Uniform's mastery share is 0.0200, one item of 50 per learner on average. | **Holds** (the restriction is formally triggered but small). | Abstract and 5.1 give the base. |
| C9 | Leitner's deficit shows the box system is worse than equal spacing. | Leitner is forced to the fixed daily capacity, and spare capacity goes to not-yet-due items (amendment A2); the design does not separate this from the box logic. | **Holds** as an alternative explanation. | Added to 5.1 and to the limitations. |
| C10 | "Evaluating a scheduler on its own model overstates its advantage" is a general law. | One model pair, one setting: 0.0347 against 0.0085. | **Holds** as overgeneralization. | Discussion now says "can overstate" and gives the one measured factor. |
| C11 | The agreement with Cepeda et al. (2006) supports the models. | The models contain no gap-dependent update; only the abstract of that source was read. | Holds. | Discussion says the agreement is not evidence for either; the source is marked abstract-only. |
| C12 | Missing failed or unfavourable runs. | No run failed or was excluded; the EXP-002 `ω` check was not run (owner, D-017); draft-setting probes showed greedy below uniform before the freeze. | Partly holds: the pre-freeze probes were not in the M3 reports. | Disclosed in manuscript 4.1 and supplement S6. |
| C13 | Stale or mismatched numbers. | EXP-003 report said "9 power-law cells" (correct: 10); massed Holm p printed as 0.0000 (underflow). | Holds. | Corrected (evidence audit F1, F2). |
| C14 | Data leakage from the calibration data or the `RI` selection into the contrasts. | DS01 sets only `h0` and `σ`; the `RI` choice used the uniform arm on exploratory seeds; all seed blocks are disjoint. | Does not hold. | None. |
| C15 | SENS-001 is a garden of forking paths. | It was specified after the results; all its outputs, including those that support the frozen reading, are reported in S4; it changes no verdict. | Partly holds (post hoc by construction). | Labelled exploratory and post hoc everywhere; the 0.95 ceiling threshold is called post hoc. |

## 2. What changed in the conclusions

- **EXP-001.** Unchanged in direction and strength; now supported by two independent-seed replications and by the absence of a recency explanation. Still conditional on the oracle and the model, and restricted to mean recall.
- **EXP-002.** The frozen verdict stands ("EXP-001 advantage dependent on model knowledge"). Its reading changes from a categorical "no advantage without the true model" to a quantitative one: misspecification removed about three quarters of the advantage at the central setting, and what remains is a small positive difference whose classification depends on the seed block and the retention interval.
- **EXP-003.** Unchanged; the instability is robust to noise and ceiling checks. Statements about massed review now carry its load and the model mechanics.

## 3. Remaining open points

- The initial half-life advantage of both greedy arms (C5) cannot be removed without a new, separately frozen experiment.
- The `ω` sensitivity is untested (owner decision, D-017).
- The mechanism at `k = 2` (C7, CLM-011) was measured only at the central cell.
