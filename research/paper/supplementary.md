<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Supplementary material

Companion to `research/paper/manuscript.md` (independent research manuscript / preprint draft, not peer-reviewed). M4, 2026-11-25. Every number here is in a committed result file named in the same section; the full mapping is in `research/publication/artifact_manifest.json`.

## S1. Complete experimental matrix

| experiment | kind | forgetting model | factors | arms | seeds | cells | runs | ok / excluded / failed |
|---|---|---|---|---|---|---|---|---|
| EXP-001 | confirmatory | exponential | central setting | uniform, expanding, massed, leitner, greedy (oracle) | 1000 to 1049 | 1 | 250 | 250 / 0 / 0 |
| EXP-002 | confirmatory | power law (`ω` 1 per day) | central setting | uniform, expanding, massed, leitner, greedy-power, greedy-exp | 1000 to 1049 | 1 | 300 | 300 / 0 / 0 |
| EXP-003 | confirmatory run, descriptive | both | `k` {2, 4, 8} × `RI` {1, 7, 30, 281} × items {homogeneous, lognormal, bimodal} | uniform, expanding, massed, leitner, greedy (matched) | one block of 50 per `RI`: 3000, 3100, 3200, 3300 onward | 72 | 18,000 | 18,000 / 0 / 0 |
| SENS-001 | exploratory, post hoc | both (central settings) | none (A and B reuse committed outputs) | as EXP-001 and EXP-002 | 5000 to 5049 (part C only) | 2 | 550 simulations | not applicable (no validation run) |

Central setting: `N` 50, `D` 28, `k` 4 (`B` 200), `RI` 281 days (test at day 308), `h0` 54.0 days, lognormal `σ` 0.759, `α` 0.4, `β` 0.6, `ω` 1 per day.

## S2. Extended tables

Generated tables, never edited by hand:

- EXP-001: `research/experiments/EXP-001/results_tables.md` (primary contrast, Holm family, metric sensitivity, per-arm summary with observed recall, mastery share, equity, calibration and load).
- EXP-002: `research/experiments/EXP-002/results_tables.md` (two primary contrasts, interpretation rule, all contrasts, per-arm summary).
- EXP-003: `research/experiments/EXP-003/results_tables.md` (summary counts and, for each of the 72 cells, the mean `R` of every arm, greedy minus uniform with interval, rank order and greedy's first-rank share).
- Machine-readable: `results/confirmatory/EXP-00N/analysis/frozen_analysis.json` and `research/experiments/EXP-00N/metrics.csv`.

**EXP-002 per-arm summary** (from `results_tables.md`):

| arm | mean R | 95% bootstrap CI | mastery share | min item recall | calibration MAE | peak daily load | sessions used |
|---|---|---|---|---|---|---|---|
| massed | 0.7236 | [0.7169, 0.7304] | 0.0780 | 0.0518 | n/a | 50 | 4 |
| expanding | 0.7105 | [0.7026, 0.7189] | 0.0860 | 0.0127 | n/a | 50 | 4 |
| greedy-power | 0.7053 | [0.6908, 0.7195] | 0.0000 | 0.2490 | 0.0000 | 8 | 27 |
| greedy-exp | 0.6791 | [0.6643, 0.6941] | 0.0120 | 0.0629 | 0.1804 | 8 | 27 |
| leitner | 0.6781 | [0.6684, 0.6875] | 0.0216 | 0.0051 | n/a | 8 | 27 |
| uniform | 0.6706 | [0.6624, 0.6790] | 0.0792 | 0.0026 | n/a | 8 | 27 |

## S3. Configurations and hashes

| item | path | SHA-256 |
|---|---|---|
| study protocol v1.1 | `research/protocol.md` | `fb9258a46b4b03fa1ffb171744ab951577bdf316c6147c93a00a3854603dff0d` |
| EXP-001 protocol | `research/experiments/EXP-001/protocol.md` | `91a79174986aa519bb1f9c1bc294c474ca441ce172076a6779826535689c496d` |
| EXP-001 configuration (canonical) | `research/experiments/EXP-001/config.json` | `841629fa27db8c9652746f7dde5887afc8f8a6c8b538bb0234cddba3ca1818ce` |
| EXP-002 protocol | `research/experiments/EXP-002/protocol.md` | `9f1e4e7c1b0275fb1d052015e13b5a88500fc3eaf5f82bebc7057e79621fbfa0` |
| EXP-002 configuration (canonical) | `research/experiments/EXP-002/config.json` | `930b73f2b673f44b4b066c3c9990c26a671dced9b8287a91bd892983d5c3c44d` |
| EXP-003 protocol | `research/experiments/EXP-003/protocol.md` | `f4767c1998268d9a74272d32ec6916038acd1df92c2605e94c09bdfa771cf9a4` |
| EXP-003 configuration (canonical) | `research/experiments/EXP-003/config.json` | `7c886211f6f949112a8ff1193b6d1b073f776c391df94f4d0e542e89b264b2c8` |
| data manifest | `data/manifest.json` | `6d828809a1b2597fac61cd2e08d936383a7c86877242168421d7496c2602eb36` |
| EXP-001 raw results | `results/confirmatory/EXP-001/results.json` | `8662acfb1b6af627c22f58cf65b1463b11f73805b59ca3c95172e79a42694f88` |
| EXP-002 raw results | `results/confirmatory/EXP-002/results.json` | `9d58dd0aabc4ba620d41574c856134b6909213d47671f0884c1dceb2cc22c78c` |
| EXP-003 raw results (git-ignored) | `results/confirmatory/EXP-003/results.json` | `22c56bdb9bdb06b6e438e37f2cc8c41e04bce1b613fcc66325febcb71bd78038` |
| SENS-001 output | `results/exploratory/SENS-001/sensitivity.json` | `68930eea8fe9e46bf172ae1e29f622818177cc988cfabb3d15a8d8625a8d41c9` |

Run revision `d4a793df271ec2dc1963d00715e3a6525a07863f` (clean); analysis revision `3811bb93bca8798c57b80c55d97a8713732a13b8` (figure layout only, D-016); SENS-001 revision `2e8cf056fab41ee9391e49dabf5b781199a30e40` (clean). The superseded v1.0 hashes are kept in `research/freeze.json`.

## S4. Robustness results (SENS-001, exploratory and post hoc)

Source: `results/exploratory/SENS-001/sensitivity.json`; script `scripts/m4_sensitivity.py`; journal entry SENS-001. None of these values changes a frozen verdict.

**S4.1 Recall at other retention intervals, confirmatory learners (no new simulation).** The schedules do not depend on `RI`, so each run records recall at `RI` 1, 7 and 30 days as a secondary metric. Arm minus uniform, 95% bootstrap interval, 50 seeds.

| experiment | `RI` (days) | uniform mean | greedy (EXP-001) or greedy-power (EXP-002) | greedy-exp | expanding | massed | leitner |
|---|---|---|---|---|---|---|---|
| EXP-001 | 1 | 0.9831 | 0.0076 [0.0060, 0.0093] | n/a | 0.0118 [0.0105, 0.0131] | 0.0120 [0.0106, 0.0137] | 0.0020 [0.0007, 0.0035] |
| EXP-001 | 7 | 0.9588 | 0.0189 [0.0159, 0.0221] | n/a | 0.0120 [0.0100, 0.0142] | 0.0103 [0.0078, 0.0128] | 0.0071 [0.0053, 0.0091] |
| EXP-001 | 30 | 0.8906 | 0.0392 [0.0353, 0.0431] | n/a | 0.0132 [0.0101, 0.0162] | -0.0023 [-0.0061, 0.0015] | 0.0122 [0.0101, 0.0143] |
| EXP-002 | 1 | 0.8601 | 0.0343 [0.0259, 0.0427] | 0.0113 [0.0008, 0.0213] | 0.0740 [0.0692, 0.0786] | 0.0890 [0.0834, 0.0944] | -0.0001 [-0.0043, 0.0043] |
| EXP-002 | 7 | 0.8018 | 0.0489 [0.0398, 0.0580] | 0.0213 [0.0110, 0.0313] | 0.0456 [0.0396, 0.0516] | 0.0677 [0.0613, 0.0742] | 0.0068 [0.0021, 0.0116] |
| EXP-002 | 30 | 0.7472 | 0.0496 [0.0399, 0.0595] | 0.0213 [0.0109, 0.0314] | 0.0397 [0.0331, 0.0464] | 0.0598 [0.0529, 0.0668] | 0.0099 [0.0051, 0.0147] |

Reading: on the confirmatory learners, `greedy-exp` minus uniform has an interval entirely above 0 at every shorter retention interval, so the EXP-002 "equivalent within 0.02" classification is specific to `RI` 281.

**S4.2 Reviews per item (confirmatory runs, mean over seeds).** Uniform, expanding and massed give every item exactly 4 reviews. Greedy: minimum 1.92, maximum 8.66 (EXP-001); greedy-power: 1.96 and 15.14; greedy-exp: 1.28 and 14.52; Leitner: 3.0 and 6.8 (EXP-001), 3.0 and 6.3 (EXP-002).

**S4.3 EXP-003 reversals with resolved differences.** For each cell and each of the 10 arm pairs, a paired 95% bootstrap interval (10,000 resamples, seed 20261124). A reversal counts as resolved when the pair is ordered against EXP-001 and the interval excludes 0. Ceiling cells: uniform mean `R` above 0.95 (post hoc threshold): C000, C002, C004, C005, C008, C010, C016, C026, C028, C032, C034, C040, C050, C052, C058, C064.

| subset | cells | with a point reversal | with a resolved reversal | top arm resolved against all others | resolved top arm: massed / greedy / expanding / uniform / leitner |
|---|---|---|---|---|---|
| all | 72 | 70 | 70 | 59 | 28 / 15 / 14 / 2 / 0 |
| without ceiling cells | 56 | 54 | 54 | 46 | 28 / 10 / 6 / 2 / 0 |
| exponential | 36 | 34 | 34 | 30 | 4 / 13 / 11 / 2 / 0 |
| power law | 36 | 36 | 36 | 29 | 24 / 2 / 3 / 0 / 0 |

**S4.4 Independent-seed replication and mechanism (new simulation, seeds 5000 to 5049).** Same base settings as the frozen EXP-001 and EXP-002 configurations, read without modification.

| setting | contrast vs uniform | mean diff | 95% bootstrap CI | paired t 95% CI | rule |
|---|---|---|---|---|---|
| EXP-001 (exponential) | greedy | 0.0193 | [0.0147, 0.0236] | [0.0146, 0.0240] | above zero |
| EXP-001 | expanding | 0.0072 | [0.0040, 0.0103] | [0.0039, 0.0104] | above zero |
| EXP-001 | leitner | -0.0104 | [-0.0137, -0.0070] | [-0.0139, -0.0068] | below zero |
| EXP-001 | massed | -0.0434 | [-0.0498, -0.0371] | [-0.0500, -0.0368] | below zero |
| EXP-002 (power law) | greedy-power | 0.0317 | [0.0213, 0.0425] | [0.0205, 0.0429] | above zero |
| EXP-002 | greedy-exp | 0.0098 | [0.0007, 0.0187] | [0.0005, 0.0191] | above zero |
| EXP-002 | expanding | 0.0387 | [0.0336, 0.0440] | [0.0334, 0.0440] | above zero |
| EXP-002 | leitner | 0.0064 | [0.0027, 0.0100] | [0.0026, 0.0102] | above zero |
| EXP-002 | massed | 0.0493 | [0.0418, 0.0568] | [0.0416, 0.0571] | above zero |

| setting | arm | reviews per hard-third item | reviews per easy-third item | mean last-review day | mean review day |
|---|---|---|---|---|---|
| EXP-001 | uniform | 4.000 | 4.000 | 24.180 | 14.065 |
| EXP-001 | greedy | 5.326 | 2.714 | 23.978 | 14.065 |
| EXP-001 | leitner | 4.224 | 3.850 | 23.872 | 14.065 |
| EXP-001 | expanding | 4.000 | 4.000 | 27.000 | 11.750 |
| EXP-001 | massed | 4.000 | 4.000 | 27.000 | 25.500 |
| EXP-002 | greedy-power | 4.548 | 3.309 | 22.916 | 14.065 |
| EXP-002 | greedy-exp | 5.441 | 2.480 | 22.697 | 14.065 |

Thirds are by initial half-life within each learner (16 items each). In the EXP-002 setting, `greedy-exp` reviewed 3.6% of items at most once.

## S5. Experiment report links

- EXP-001: `research/experiments/EXP-001/report.md`, `protocol.md`, `reproduction.md`; generated report `results/confirmatory/EXP-001/report/`.
- EXP-002: `research/experiments/EXP-002/report.md`, `protocol.md`, `reproduction.md`; generated report `results/confirmatory/EXP-002/report/`.
- EXP-003: `research/experiments/EXP-003/report.md`, `protocol.md`, `reproduction.md`; generated report `results/confirmatory/EXP-003/report/`.
- Exploratory design inputs: CAL-001, CAL-002, RI-001, PROBE-001 to PROBE-009, METRICVAL-001, SMOKE-001, SMOKE-002 in `results/exploratory/` and `research/experiment_journal.jsonl`.

## S6. Deviations and owner decisions

| id | date | decision | effect on results |
|---|---|---|---|
| D-010, D-011 | 2026-11-24 | Owner-approved amendments A1 to A5 (calibrated `h0` and `σ`, coverage-first adaptive arms, 50 seeds, EXP-003 kept, disjoint `RI` seed blocks); protocol v1.0 frozen | Design inputs; no confirmatory run under v1.0 |
| D-012 | 2026-11-24 | Round-3 rule (a): forgetting-model misfit diagnosed (CAL-002); recorded as a limitation; no parameter changed | Claims boundary: all results conditional on the model |
| D-013 | 2026-11-24 | Round-3 rule (b): central `RI` 281 days, from the uniform arm alone; EXP-003 gains `RI` 281 (72 cells) | Defines the central cell |
| D-014 | 2026-11-24 | Re-freeze v1.1 (owner-approved); v1.0 hashes kept as superseded | Frozen design of all runs |
| D-015 | 2026-11-25 | Analysis readings fixed in code before any output (Holm statement, interpretation-rule readings, tie sharing, reversal definition, E1 and E2 criteria) | Applied unchanged |
| D-016 | 2026-11-25 | Figure layout changed after output; all analysis values identical; EXP-003 raw file git-ignored | Presentation only |
| D-017 | 2026-11-25 | Owner: the EXP-002 `ω` check is not run (no frozen configuration); reports written from committed results | Robustness to `ω` untested |
| D-018 | 2026-11-25 | M4: SENS-001 exploratory checks; evidence audit; two report corrections | No frozen verdict changed |

Pre-freeze exposure (C4 disclosure, `research/freeze.json`): draft-setting probes showed greedy below uniform (PROBE-001 -0.0286 [-0.0349, -0.0226]; PROBE-002 greedy-power -0.0321 [-0.0402, -0.0241]) on seeds disjoint from the confirmatory ones. No deviation from the frozen matrices occurred.
