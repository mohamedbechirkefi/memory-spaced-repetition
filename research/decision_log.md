<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Decision log (append-only)

Each entry: id, date, decision, decided by, rationale, alternatives, consequences. Entries are never edited after the fact; corrections are new entries.

## D-001 (2026-11-24): Protective non-commercial licence instead of a permissive licence

- **Decided by:** the owner.
- **Decision:** All original material in this repository is licensed under the MEMORY Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-MEMORY-NC-Research-1.0`), with a Contributor License Agreement (CLA v1.0). The licence package (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/workflows/cla.yml`, `.gitignore`) was committed before this session.
- **Rationale:** the owner's stated reason is their own protection.
- **Deviation from the master prompt:** section 2 asks for an "owner-approved permissive code license". The owner chose a protective, source-available, non-commercial licence instead. The project is therefore not "open source" in the OSI sense; public texts must say "source-available" and must not describe the project as open source.
- **Consequences:** sessions never change the licence files. Data licences are recorded separately in `data/manifest.json`. Third-party dependencies keep their own licences.

## D-002 (2026-11-24): Zero-cost publication toolchain without TeX

- **Decided by:** session (M0), within the brief's instruction; open to owner review.
- **Decision:** Markdown is canonical. PDFs are produced by pandoc 3.6.3 (`/Users/bechir/research/labs/.tools/pandoc`) converting Markdown to Typst, then compiled by the `typst` Python package 0.15.0 in `/Users/bechir/research/labs/.tools/py/bin/python`. `research/paper/manuscript.tex` is generated from Markdown with pandoc for portability and is not compiled locally.
- **Rationale:** no TeX distribution is installed (`tex`, `pdflatex`, `xelatex` not found); installing one is unnecessary; all tools are free and local.
- **Alternatives:** installing TeX Live (large download, not needed); Chrome headless HTML printing (not chosen: Typst gives page numbers, equations and cross-references directly).
- **Consequences:** an exploratory toolchain smoke check was run this session (see `progress.md`); its PDF is in the session scratchpad and is not committed. Every future PDF must be generated and visually inspected before it is claimed.

## D-003 (2026-11-24): Synthetic data only for the draft protocol

- **Decided by:** session (M0), proposal pending owner approval.
- **Decision:** EXP-001 to EXP-003 use only synthetic items and simulated learners. No public dataset is downloaded or used.
- **Rationale:** the research question concerns modelled recall; section 10 requires no user data. DS01 (CC BY-NC 4.0) is lawful for non-commercial research but not needed; DS02 is gated and not redistributable.
- **Consequences:** all parameter values are planning assumptions, reported as such; external validity to human learners is explicitly out of scope.

## D-004 (2026-11-24): Protocol draft structure (pending owner freeze)

- **Decided by:** session (M0), proposal only. **Not frozen.**
- **Decision:** primary contrast `greedy` versus `uniform` under exponential forgetting (EXP-001); oracle-advantage sensitivity under power-law forgetting with model misspecification (EXP-002); descriptive sweep over models, budgets, retention intervals and item distributions (EXP-003). Primary metric: mean true-model recall probability at the delayed test. Unit: simulated learner; 50 matched seeds per cell.
- **Rationale:** see `research/protocol.md` sections 3 to 10.
- **Consequences:** the owner may change any of these before the freeze (G-FREEZE).

## D-005 (2026-11-24): Dependency lock with a two-week release cutoff

- **Decided by:** session (M0).
- **Decision:** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"` so that every locked package version was released at least two weeks before 2026-11-24. Python 3.12. Runtime dependencies kept minimal (NumPy, jsonschema, matplotlib); test dependencies pytest and hypothesis.
- **Consequences:** upgrades require a dated decision entry.
