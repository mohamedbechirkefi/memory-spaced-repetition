<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Release checklist (M6)

**Status (2026-11-25, corrected 2026-11-26): release candidate `0.2.0-rc1` prepared and verified; awaiting the owner's review and sign-off. The repository was pushed and is public at https://github.com/mohamedbechirkefi/memory-spaced-repetition since 2026-11-25 (owner, 2026-11-26, decision sheet, A1); nothing has been tagged or released, and no DOI or preprint exists.** Each ticked item was verified in the M6 session; the evidence is in `research/publication/reproducibility_report.md` (section numbers below).

- [x] Clean clone in a separate directory; `uv sync --frozen` succeeds. Evidence: local clone of `46b4a11` in the session scratchpad, `uv sync --frozen --all-groups --all-extras` completed (section 1); second clone after the M6 commit (section 6).
- [x] Full test suite run; actual counts recorded. Evidence: clone `253 passed in 38.38s`; working repository after M6 changes `256 passed` (3 new link tests); demo `Tests 43 passed (43)` (sections 1 and 6).
- [x] Smoke reproduction matches committed results within the documented tolerance. Evidence: `smoke` 25 runs ok, every metric identical to `results/exploratory/SMOKE-001-M3/results.json`, summary and contrast CSVs byte-identical; EXP-001 rerun to scratch, 250 runs ok, every metric identical to the committed `results.json` (only timing and provenance fields differ, the documented tolerance) (section 1).
- [x] Demo builds and works offline after initial load; keyboard and reduced-motion checks. Evidence: `npm ci`, `npm test`, `npm run build`, `node tools/a11y_check.mjs dist` printed `A11Y-CHECK PASS` (offline sandbox run, keyboard 29 of 29, 0 running animations under reduced motion); export rerun left `git status` clean (section 1).
- [x] Manuscript and report PDFs generated with the Typst toolchain and visually inspected. Evidence: 5 PDFs (manuscript 15 pages, supplement 5, reports 7, 7 and 10), every manuscript and supplement page and every report figure page read as PNG; seven layout findings fixed in the builder or the Markdown (R1 to R7); titles set, 0 e-mail addresses or local paths in text or metadata (sections 2 and 3).
- [x] References and cross-links verified. Evidence: 5 of 5 references in `references.bib` and in the reference list; 4 sources' cited statements checked in free full texts (evidence audit section 6); `scripts/check_links.py` `LINK-CHECK PASS` (33 relative links, 0 broken) (section 4).
- [x] Data manifest verified; no non-redistributable data bundled. Evidence: DS01 SHA-256, MD5 and size equal to `data/manifest.json`; only the manifest is tracked under `data/`; `SHA256SUMS` 18, 18 and 22 OK; 40 artifact-manifest paths exist (section 4).
- [ ] Secret scan and personal-identifier scan clean. Secrets: clean (0 keys, tokens, private-key headers or `.env` files). Personal identifiers: not fully clean. 1 e-mail address (the AI co-author trailer in `CLAUDE.md`, not personal); absolute home-directory paths, which contain the local user name, remained at M6 in `CLAUDE.md` (5 lines), `research/feasibility.md` (5) and the append-only `progress.md` (1) and `research/decision_log.md` (3); the two in current code and the demo README were removed. On 2026-11-26 (owner, decision sheet, B9) the editable files `CLAUDE.md` and `research/feasibility.md` were scrubbed; the 4 lines in the append-only logs stay as written and were already public in the history, which is not rewritten (section 5 and section 7).
- [ ] Owner sign-off of `research/publication/author_review.md` (owner only).
- [ ] Owner approval for any push or publication recorded (G-PUBLIC; owner only).

## Version and date at the release (owner, 2026-11-26, decision sheet, B8)

The release candidate keeps `version: "0.2.0-rc1"` and no `date-released` in `CITATION.cff`. At the release, the version becomes `0.2.0` and `date-released` is set to the release day. `pyproject.toml` stays at its current package version `0.2.0` (D-021), so the lockfile and the recorded environments do not change.

## Release notes (draft)

- Figures: the first-rank-share heat map FIG-004 (EXP-003) is kept as a checksummed generated result; its cell labels are small in the PDFs (vector SVG, legible when zoomed) and it would be regenerated only for print (owner, 2026-11-26, decision sheet, B11).
- Tools: external build and check tools (pandoc, GPL-2.0-or-later; the `typst` Python package; Node 22; Google Chrome for the accessibility check; MPL-2.0 lightningcss and hypothesis as development tools), as listed in `research/publication/dependency_licences.md`, are used but not redistributed by this repository (owner, 2026-11-26, decision sheet, B13).
- Sources: the reading labels of the cited sources (metadata-only, abstract-only or cited statement checked in the full text) are accepted as stated in the manuscript (owner, 2026-11-26, decision sheet, B14).
- Demo: hosted as Cloudflare Workers static assets on the free plan at https://memory-spaced-repetition.kefimohamedbechir.workers.dev, deployed by the lab coordinator (B2).
