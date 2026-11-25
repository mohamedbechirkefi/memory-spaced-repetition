<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Owner review checklist (M6)

- [ ] Authorship and metadata approved by the owner (no invented affiliation, funding or endorsement).
- [ ] AI-assistance disclosure reviewed: the AI is a disclosed research and development assistant, not an author.
- [ ] Frozen protocol hashes and approval dates verified.
- [ ] Each experiment report read and approved.
- [ ] Manuscript, reports, demo and articles use identical results and scope.
- [ ] Licence wording checked: "source-available, non-commercial", not "open source".
- [ ] Publication approved (G-PUBLIC). Not approved at M0.

No box above was ticked by an agent at any milestone; all seven are unticked as of M6 (checked 2026-11-25). Only the owner ticks them.

## Prepared for the owner (M6, 2026-11-25)

### What to read for each box

1. **Authorship and metadata.** `research/paper/manuscript.md` lines 1 to 8 (YAML title, author, status, AI disclosure) and section 11; `CITATION.cff` (authors, version `0.2.0-rc1`, the preferred citation and the two commented placeholders); `README.md` sections "Citation" and "Licence"; `articles/medium.md` line 6 (byline placeholder). The PDF metadata of `research/paper/manuscript.pdf` carries the title and the author name.
2. **AI-assistance disclosure.** `research/paper/manuscript.md` section 11 (approved wording, D-019) and the YAML `ai_disclosure`; the same sentence in `README.md` ("Citation"), `CITATION.cff` (`message`) and each report's "Author" line.
3. **Frozen protocol hashes and approval dates.** `research/freeze.json`; `research/paper/supplementary.md` section S3 (every hash) and S6 (decisions D-010 to D-018); `research/decision_log.md` D-010 to D-015; the guard (`src/memory_research/guard.py`) refuses any configuration whose hash differs.
4. **Each experiment report.** `research/experiments/EXP-001/report.pdf` (7 pages), `EXP-002/report.pdf` (7), `EXP-003/report.pdf` (10), each generated from its `report.md`; M4 corrections and addenda are marked in the text.
5. **Identical results and scope.** `research/publication/evidence_audit.md` (sections 2 to 6), `research/publication/number_audit.json` (`AUDIT: 0 unmatched` after M6 edits), `tests/test_demo_export.py` (demo, README, citation and articles use the manuscript's numbers), the demo built from `demo/` (`A11Y-CHECK PASS`).
6. **Licence wording.** `README.md` section "Licence", the comment at the top of `CITATION.cff`, `research/publication/dependency_licences.md` (no third-party licence flagged), `LICENSE` and `NOTICE.md` (unchanged).
7. **Publication.** `research/publication/release_checklist.md` and `research/publication/reproducibility_report.md` (what was verified at M6 and what remains).

The manuscript PDF (`research/paper/manuscript.pdf`, 15 pages) and the supplement (`research/paper/supplementary.pdf`, 5 pages) are the easiest full-text reading copies; Markdown remains canonical.

### Open decisions for this repository

From `labs/_shared/owner-approvals-2026-11-25e.md`, `progress.md` and `research/decision_log.md`:

1. Whether and when to publish anything (push, release, tag, public repository, demo hosting, articles) remains the owner's decision under G-PUBLIC; M6 released nothing.
2. The owner signs off this checklist; no box has been ticked by an agent.
3. The repository URL is an owner-only fact to supply at a release decision.
4. The demo URL is an owner-only fact to supply if the page is hosted.
5. The affiliation (README, `CITATION.cff`) is an owner-only fact to supply or confirm.
6. The author line and affiliation of the Medium article draft are for the owner to confirm.
7. The two article drafts (`articles/medium.md`, `articles/linkedin.md`) have not yet been read by the owner and are unpublished.
8. `date-released` was removed from `CITATION.cff` under the coordinator default of owner-approvals-2026-11-25e; re-adding it, and choosing the final version number in place of `0.2.0-rc1`, are part of the owner's publication step.
9. The preferred citation added to `CITATION.cff` uses the owner-approved manuscript title with status "in-preparation"; the owner may change or remove it.
10. Funding and competing interests are already approved (D-019); the owner confirms they still hold at publication.
11. The untested `ω` sensitivity (EXP-002 optional check not run, D-017) stays disclosed as a limitation unless the owner decides otherwise.
12. Absolute home-directory paths with the local user name remain in `CLAUDE.md`, `research/feasibility.md` and the append-only logs; whether to scrub them before any publication is for the owner (release checklist, secret and identifier item).
13. The FIG-004 heat map has small cell labels in the PDFs (legible when zoomed); regenerating the figure with a larger layout would be a presentation change for the owner to approve.

### Remaining owner placeholders (file and line, at the M6 commit)

| file | line | placeholder |
|---|---|---|
| `CITATION.cff` | 14 | `<REPOSITORY URL: unpublished>` (comment) |
| `CITATION.cff` | 15 | `<AFFILIATION: to be supplied or confirmed by the owner>` (comment) |
| `README.md` | 41 | `<DEMO URL: unpublished>` |
| `README.md` | 75 | `<REPOSITORY URL: unpublished>`, `<AFFILIATION: to be supplied or confirmed by the owner>` |
| `articles/linkedin.md` | 14 | `<REPOSITORY URL: unpublished>` |
| `articles/linkedin.md` | 15 | `<DEMO URL: unpublished>` |
| `articles/medium.md` | 6 | `<AUTHOR LINE AND AFFILIATION: to be confirmed by the owner>` |
| `articles/medium.md` | 50 | `<REPOSITORY URL: unpublished>`, `<DEMO URL: unpublished>` |
| `demo/README.md` | 31 | `<DEMO URL: unpublished>` |
| `research/paper/manuscript.md` | 274 | `<REPOSITORY URL: unpublished>` (section 10) |
