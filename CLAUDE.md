<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# CLAUDE.md: how every session works in MEMORY

Project MEMORY asks: which review schedule maximizes modelled delayed recall under a fixed study budget? It is a simulation study. `master_prompt.md` is the authority and is never edited. If this file and `master_prompt.md` conflict, `master_prompt.md` wins; record the conflict in `progress.md`.

## 1. Reading order (before modifying anything)

1. `master_prompt.md` (authority; sections 2, 3, 5, 10 and 11 are binding).
2. `roadmap.md` (milestones, status, blockers).
3. `progress.md` (append-only journal; read the latest entry and its "next action").
4. `research/protocol.md` (current protocol and its status: DRAFT or FROZEN with hash).
5. `research/claims_register.csv` (every claim that may be made, with evidence).

Then run `git status` and inspect existing files. Never overwrite the owner's changes. State the current milestone and the next bounded task before working.

## 2. Mandatory requirements (master prompt section 11, all sessions)

- **Publication tree (11.1).** Maintain `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical; manuscript.tex and manuscript.pdf generated), `research/experiments/EXP-NNN/` (protocol.md, report.md, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- **Stable identifiers.** EXP-NNN for experiments, RUN ids within an experiment (a seed is a run, not a new experiment), FIG and CLM ids. A new question or materially different protocol gets a new EXP id.
- **Before each experiment (11.2).** A complete `EXP-NNN/protocol.md`, frozen with a recorded hash and owner approval before any confirmatory run. Post-hoc changes are exploratory, dated and justified.
- **Every registered experiment gets a standalone report (11.3)** with the twelve mandatory sections, including failed, null, abandoned and exploratory ones, visibly labelled.
- **One integrated manuscript (11.4)**, venue-neutral, default status "independent research manuscript / preprint draft, not peer-reviewed".
- **Evidence pipeline (11.5).** Tables and figures are generated once from versioned results and reused everywhere. An artifact manifest maps every number, table and figure to EXP id, run ids, metric definition, result path, generator script, config/protocol hash and code revision. A second review pass challenges the preferred hypothesis.
- **Milestone additions (11.6).** M0/M1: registry, manuscript skeleton, experiment protocols, zero-cost toolchain, freeze before execution. M2: versioned output schemas, reproducibility manifests and report generators alongside the core. M3: reports written as experiments finish; provenance captured at run time. M4: reports finished, evidence audit, synthesis into the manuscript. M5: demo, paper, reports and articles use identical verified results. M6: compile and visually inspect PDFs, verify references and links, reproduce smoke in a clean clone, owner review checklist.
- **Toolchain (decision D-002).** No TeX distribution exists. PDFs are built as Markdown to Typst with pandoc (`/Users/bechir/research/labs/.tools/pandoc`), compiled with the `typst` Python package in `/Users/bechir/research/labs/.tools/py/bin/python`; `manuscript.tex` is generated from Markdown with pandoc and is not compiled. Never claim a PDF exists unless it was generated and inspected.

## 3. Rules

### Gates
- Never push, add a remote, create a GitHub repository or publish anything (G-PUBLIC).
- No paid service of any kind. The owner's coding subscription is never an inference backend.
- Never freeze a protocol yourself: freezing is the owner's decision (G-FREEZE). Until the owner freezes, every run is exploratory and labelled so.
- No confirmatory experiments without a frozen, owner-approved protocol. Tiny exploratory smoke checks of the toolchain or engine are allowed and labelled exploratory.

### Scope
- Work only inside `/Users/bechir/research/labs/memory-spaced-repetition/`. Tools under `/Users/bechir/research/labs/.tools/` and `/Users/bechir/research/helix/.tools/node/bin` are used read-only; never modify them.
- Do not touch any other folder under `/Users/bechir/research` (hive, helix, cogkt, trading, other labs).
- Never kill processes you did not start. Never delete anything you did not create in the current session.

### Truthfulness
- Never fabricate results, citations, test counts or PDFs.
- Record commands and their actual outputs in `progress.md`.
- A source not actually opened is labelled unverified and is not cited as read.
- Simulated learners are not human participants. No claim of demonstrated human learning gains (master prompt section 10, claims boundary). No user data.

### Files and style
- New text and code files start with `SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0` as a comment where the format allows; JSON and CSV are covered by `NOTICE.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner" (they/them).
- The licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`) are the owner's decision and are not changed. Development commands may be appended to `CONTRIBUTING.md`.
- Large generated outputs stay out of git (`results/raw/`); provide deterministic regeneration scripts and small fixtures.

### Session end
1. Append a dated entry to `progress.md` (commands, actual outputs, failures, changed files, risks, next action).
2. Update `roadmap.md` statuses and blockers. Never mark incomplete work done.
3. Append decisions to `research/decision_log.md`.
4. Run the test suite if code changed, or record why not.
5. Commit locally only, with the owner's git identity passed as `git -c user.name=... -c user.email=... commit` (identity given in the session brief; the address is deliberately not written in this repository), message ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## 4. Commands (planned; see CONTRIBUTING.md once implemented)

- Lock dependencies: `/Users/bechir/research/labs/.tools/py/bin/uv lock`
- Sync environment: `/Users/bechir/research/labs/.tools/py/bin/uv sync`
- Tests, smoke, full run, report export: defined in M2 and recorded here when they exist.
