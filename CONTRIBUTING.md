<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Contributing to MEMORY

MEMORY is an independent, source-available research project maintained by Mohamed Bechir Kefi: forgetting and learning schedules.

Technical suggestions, bug reports, reproducibility results, corrections and Pull Requests are welcome. The project is available for non-commercial research under the MEMORY Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE)); it is not OSI-approved open-source software.

## 1. Before you start

For major changes, open an Issue first. Read `master_prompt.md`, `research/protocol.md` and `research/claims_register.csv`: frozen protocols are never changed silently, and every reported number must trace to a result file.

## 2. Pull Request requirements

- Your contribution is original or appropriately licensed, and you have the right to submit it.
- No credentials, secrets, confidential information or personal data.
- Relevant tests are included and pass; you report what you actually ran.
- Third-party dependencies and data sources are identified with their licenses.
- New files carry the header `SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0` where the format allows.
- You accept the Contributor License Agreement before your contribution is merged.

## 3. Contributor License Agreement

A recorded acceptance of [CLA.md](CLA.md) is required before merging copyrightable contributions. When you open a Pull Request, the "CLA Assistant" check comments on it; read the CLA, then post this exact comment:

    I have read the MEMORY CLA v1.0 and I hereby sign it

The check records your public GitHub username and account ID, the date and the PR. You sign once. If the check does not update, comment `recheck`. Checking a box is not a signature; the comment is.

The CLA lets the maintainer use, modify, distribute, relicense and commercially exploit accepted contributions. You keep the copyright in your original contributions.

## 4. Governance

Mohamed Bechir Kefi is the project owner and lead maintainer, and the only person who can change the protected `main` branch. The maintainer decides the research direction, protocol freezes, claims, releases and licensing.

## 5. Privacy and disclosure

Never commit an e-mail address, a name or any other personal identifier in code, logs, fixtures or results. Report security issues privately through GitHub's private vulnerability reporting.

## 6. Development commands

Tools used by the project (free, local):

- Lock dependencies: `uv lock` (uv 0.9.5; `[tool.uv] exclude-newer` keeps every version at least two weeks old).
- Check the lock: `uv lock --check`.
- Install the locked environment: `uv sync --frozen`.
- Run tests (from M2): `uv run pytest`.
- Build a PDF from Markdown: `pandoc FILE.md -s -V mainfont="Libertinus Serif" -o FILE.typ`, then `python -c "import typst; typst.compile('FILE.typ', output='FILE.pdf')"`.
- Generate LaTeX source: `pandoc FILE.md -s -o FILE.tex`.

Experiment, smoke and report-export commands (M2):

- Run the tests: `uv run python -m memory_research test`.
- Exploratory smoke run and report: `uv run python -m memory_research smoke --pdf`.
- Run a matrix configuration: `uv run python -m memory_research run --config experiments/configs/probe_central.json --report`. Confirmatory configurations (`research/experiments/EXP-NNN/config.json`) are refused until their protocol is frozen.
- Rebuild a report from a result file: `uv run python -m memory_research report --results results/exploratory/SMOKE-001/results.json --pdf`.

Interactive page (M5):

- Regenerate the page data: `.venv/bin/python scripts/export_demo_data.py` (`--check` compares with the committed file).
- Regenerate the engine fixture: `.venv/bin/python scripts/export_engine_fixture.py` (`--check` likewise).
- Build and check the page: `cd demo && npm ci && npm test && npm run build && node tools/a11y_check.mjs dist`; serve it with `npm run preview`.
