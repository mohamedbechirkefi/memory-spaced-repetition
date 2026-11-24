<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Roadmap

Target: five focused development days (planning estimate, never a reason to weaken evidence). If the target is threatened, cut optional UI and EXP-003 levels first (owner-approved, before the freeze), never controls, reporting or truthfulness. Section 11.6 additions of the master prompt are included in every milestone.

Status values: `done`, `in progress`, `planned`, `blocked (reason)`.

| ID | Milestone | Depends on | Acceptance criteria (gate) | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | Control files of section 2 exist; feasibility audit with commands; source and licence audit; scope, cost (zero) and exclusions stated; zero-cost publication toolchain confirmed (11.6); registry, manuscript skeleton and draft experiment protocols initialized (11.6); dependency lock produced. Gate: the owner can understand question, cost and exclusions. | P0 | 0.5 day | done (pending owner review) | Owner review of the M0 package |
| M1 | Research and preregistration | M0 | Content-level reading of the metadata-only sources (L04 to L07, L09) or explicit removal; formal model finalized; baselines justified; fixture manifest; EXP-001 to EXP-003 protocols complete per 11.2 with reproduction commands; owner freezes protocols and the hashes are recorded (11.6). Gate: protocol frozen before confirmatory runs; exploratory results visibly separated. | P0 | 0.5 day (+ owner time) | in progress (drafts written in M0) | **G-FREEZE: owner approval of the protocol**; owner decisions listed in `progress.md` |
| M2 | Core implementation | M1 draft (implementation may proceed before the freeze; confirmatory runs may not) | Reference baseline (`uniform`) first, then other arms; pure seeded functions; exponential and power-law models; retrieval updates; versioned JSON result schema with validation; reproducibility manifests and report generators alongside the core (11.6); unit, invariant (probability in [0,1], exact budget, event ordering, monotone decay between reviews), golden (known curve values, hand-computed examples) and differential tests; CLI for smoke, full run, report export and test; exploratory smoke run measuring runtime and paired-difference spread. Gate: correctness before UI polish. | P0 | 1.5 days | planned | None (can start before freeze) |
| M3 | Experiments | M1 freeze, M2 | Smoke run, metric validation, frozen matrices of EXP-001 to EXP-003 run in full; raw machine-readable results retained; figures with uncertainty; each experiment report written as it finishes (11.6); all failures and deviations recorded; provenance captured at run time. Gate: complete planned matrix or documented failure; no silently dropped runs. | P0 | 0.75 day | blocked (G-FREEZE) | Frozen protocol |
| M4 | Interpretation | M3 | Confounder inspection; sensitivity analyses (EXP-002, EXP-003, metric choice); expected vs observed; claims register filled; limitations updated; experiment reports finished; evidence audit; manuscript synthesized including contradictory results; second review pass challenging the preferred hypothesis (11.5, 11.6). Gate: each numerical claim maps to result id, config and figure; each external claim to a read source. | P0 | 0.75 day | planned | M3 |
| M5 | Interactive experience | M4 | Static page: forgetting curves and calendar schedule comparison; overview, playground (reset, seed, scenario), results with uncertainty, methodology, limitations; measured vs visitor sandbox vs assumptions clearly separated; accessibility (keyboard, contrast, reduced motion, mobile); offline after load; identical results and labels to paper and reports (11.6). Gate: offline, responsive, keyboard usable, no fabricated data, no runtime service. | P1 | 0.75 day | planned | M4 |
| M6 | Release candidate | M5 | Clean clone; locked install; tests and smoke reproduction; demo build; manuscript and report PDFs compiled with the Typst toolchain and visually inspected; references, cross-links, equations, figures and metadata verified; manifests and links verified; secret and licence scan; owner review checklist (11.6). Gate: verified facts only; owner approves any publication (G-PUBLIC). | P0 | 0.5 day | planned | M5; owner approval for any publication |

## Dependencies (summary)

M0 → M1 → (M2 may start in parallel with M1 review) → M1 freeze → M3 → M4 → M5 → M6.

## Optional cuts if the five-day target is threatened (in order)

1. Demo polish beyond the minimum viable page.
2. EXP-002 `ω` descriptive check.
3. EXP-003 factor levels (owner-approved before freeze).
