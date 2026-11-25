<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# EXP-002 reproduction

**Status: run (confirmatory, 2026-11-25), 300 of 300 runs ok.** Protocol FROZEN v1.1; configuration canonical SHA-256 `930b73f2b673f44b4b066c3c9990c26a671dced9b8287a91bd892983d5c3c44d`; provenance revision `d4a793df271ec2dc1963d00715e3a6525a07863f`.

1. `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` (uv 0.9.5; lock in `uv.lock`).
2. `.venv/bin/python -m pytest` (234 tests passed at the M3 revisions).
3. `.venv/bin/python -m memory_research run --config research/experiments/EXP-002/config.json --report --pdf`. Only the frozen configuration is accepted; any change exits with status 3.
4. `.venv/bin/python scripts/analyse_confirmatory.py --exp EXP-002 --results results/confirmatory/EXP-002/results.json --exp001 results/confirmatory/EXP-001/analysis/frozen_analysis.json`. EXP-001 must be analysed first, because the interpretation rule reads its result.
5. `.venv/bin/python scripts/build_experiment_records.py EXP-002`

**Outputs.** `results/confirmatory/EXP-002/results.json` (SHA-256 `9d58dd0aabc4ba620d41574c856134b6909213d47671f0884c1dceb2cc22c78c`), plus `run_manifest.json`, `report/`, `analysis/` and `SHA256SUMS`.

**Tolerance.** As for EXP-001.

**Not run.** The `ω ∈ {0.3, 3}` descriptive check of protocol section 16 has no frozen configuration. It is not run, by the owner's decision of 2026-11-25 (D-017).

**History.** Written in M2 before the freeze. The earlier "not run" statements are superseded.
