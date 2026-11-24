<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# EXP-001 reproduction (draft, written in M2 before the freeze)

**Status: not run. The protocol is DRAFT v0.1 and not frozen; the command below is refused until the owner freezes it (G-FREEZE).**

1. `uv sync --frozen` (uv 0.9.5; lock in `uv.lock`).
2. `uv run python -m memory_research test` (whole test suite).
3. `uv run python -m memory_research run --config research/experiments/EXP-001/config.json --report --pdf`

While the protocol is unfrozen, step 3 exits with status 3 and a message such as "refusing confirmatory run of EXP-001: research/protocol.md is marked NOT FROZEN; registry protocol_hash for EXP-001 is 'none (not frozen)', not a SHA-256". After the freeze it writes `results/confirmatory/EXP-001/results.json` (schema `memory-result/1.0.0`), `run_manifest.json` (schema `memory-run-manifest/1.0.0`) and `report/` (tables, figures, generated report, PDF).

Tolerance: reruns are bit-identical on the same platform except the timing and memory fields; across platforms, metric values are expected to agree to about 1e-12 relative (floating-point library differences).

Note: `config.json` mirrors the draft protocol. If the owner accepts amendments (`research/amendment_proposals.md`), it must be updated before the freeze.

## Update at the freeze (2026-11-24, round 2)

The protocol is FROZEN v1.0 and `config.json` holds the amended, calibrated values (study protocol section 15). Step 3 is now accepted by the guard for the frozen configuration only; any edit to `config.json`, to `research/protocol.md` or to this experiment's protocol makes it exit with status 3. The statements above about the draft state are historical.
