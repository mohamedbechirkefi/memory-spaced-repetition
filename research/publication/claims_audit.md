<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Claims audit checklist (M4, completed 2026-11-25)

Details and findings: `research/publication/evidence_audit.md`; challenges: `research/publication/review_pass_2.md`.

- [x] Every row of `research/claims_register.csv` has an evidence path that exists (CLM-001 to CLM-014, EXT-001 to EXT-004).
- [x] Every numerical claim maps to EXP id, run ids, config hash and figure or table (register columns; `artifact_manifest.json`).
- [x] Every external claim maps to a source whose content was read at the stated level; abstract-only sources are marked as such.
- [x] Denominators, units, precision, uncertainty and sample counts cross-checked against raw outputs (`number_audit.json`; evidence audit F3 to F5). Two mismatches fixed (F1, F2).
- [x] No claim of demonstrated human learning gains.
- [x] No unsupported causal or universal statement (review pass 2, C7, C10, C11).
- [x] Failed, null and exploratory results are reported and labelled (no failed runs; EXP-002 `ω` check not run; SENS-001 exploratory; pre-freeze probes disclosed).
- [x] Second review pass that challenges the preferred hypothesis completed and recorded (`review_pass_2.md`).
