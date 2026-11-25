<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# EXP-001 reproduction

**Status: run (confirmatory, 2026-11-25), 250 of 250 runs ok.** Protocol FROZEN v1.1; configuration canonical SHA-256 `841629fa27db8c9652746f7dde5887afc8f8a6c8b538bb0234cddba3ca1818ce`; provenance revision `d4a793df271ec2dc1963d00715e3a6525a07863f`.

1. `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` (uv 0.9.5; lock in `uv.lock`).
2. `.venv/bin/python -m pytest` (234 tests passed at the M3 revisions).
3. `.venv/bin/python -m memory_research run --config research/experiments/EXP-001/config.json --report --pdf`. The guard accepts only the frozen configuration. Any edit to `config.json`, `research/protocol.md` or this experiment's protocol makes it exit with status 3.
4. `.venv/bin/python scripts/analyse_confirmatory.py --exp EXP-001 --results results/confirmatory/EXP-001/results.json`
5. `.venv/bin/python scripts/build_experiment_records.py EXP-001` (writes `results_tables.md`, `metrics.csv` and `figures/` in this folder).

**Outputs.**
- `results/confirmatory/EXP-001/results.json`: schema `memory-result/1.0.0`, SHA-256 `8662acfb1b6af627c22f58cf65b1463b11f73805b59ca3c95172e79a42694f88`.
- `run_manifest.json`: schema `memory-run-manifest/1.0.0`, with per-run start and end times.
- `report/`: generated tables, figures, report and PDF.
- `analysis/`: frozen analysis, CSV tables and figures.
- `SHA256SUMS`: checksums of all the above.

**Tolerance.** Reruns are bit-identical on the same platform except the timing and memory fields; this was checked for this experiment on 2026-11-25. Across platforms, metric values are expected to agree to about 1e-12 relative.

**History.** Written in M2 before the freeze. After the v1.0 freeze (2026-11-24, round 2) and the v1.1 re-freeze (round 3), the guard accepted the frozen configuration only. The earlier "not run" statements are superseded.
