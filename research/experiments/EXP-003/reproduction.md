<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# EXP-003 reproduction

**Status: run (confirmatory, descriptive, 2026-11-25), 18,000 of 18,000 runs ok.** Protocol FROZEN v1.1; configuration canonical SHA-256 `7c886211f6f949112a8ff1193b6d1b073f776c391df94f4d0e542e89b264b2c8`; provenance revision `d4a793df271ec2dc1963d00715e3a6525a07863f`.

1. `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` (uv 0.9.5; lock in `uv.lock`).
2. `.venv/bin/python -m pytest` (234 tests passed at the M3 revisions).
3. `nice -n 10 .venv/bin/python -m memory_research run --config research/experiments/EXP-003/config.json --report --pdf`. Only the frozen configuration is accepted. About 36 s of simulation on an Apple M1 Pro.
4. `.venv/bin/python scripts/analyse_confirmatory.py --exp EXP-003 --results results/confirmatory/EXP-003/results.json --exp001 results/confirmatory/EXP-001/analysis/frozen_analysis.json`
5. `.venv/bin/python scripts/build_experiment_records.py EXP-003`

**Outputs.**
- `results/confirmatory/EXP-003/results.json`: 15.5 MB, git-ignored because the outputs exceed the 20 MB limit. Regenerate it with step 3. The original's SHA-256 is `22c56bdb9bdb06b6e438e37f2cc8c41e04bce1b613fcc66325febcb71bd78038`, but `results.json` also holds timing fields and creation time, so a regenerated file has a different hash. Compare per-run metrics instead.
- Committed: `run_manifest.json`, `report/`, `analysis/` and `SHA256SUMS`.

**Tolerance.** As for EXP-001. Seed blocks per `RI` level: 3000, 3100, 3200 and 3300, each followed by 49 consecutive seeds.

**History.** Written in M2 before the freeze. The earlier "not run" statements are superseded.

=== END OF FILES ===
