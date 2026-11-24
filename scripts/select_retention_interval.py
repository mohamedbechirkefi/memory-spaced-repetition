# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""RI-001 (exploratory): rule (b) of protocol 16.2, baseline arm only.

Simulates only the uniform arm at the EXP-001 central setting on exploratory seeds
1 to 30, computes its mean R for RI = 1..365 days, and selects RI* by the rule of
protocol 16.2.2. Also records the power-law baseline at RI* (16.2.6, descriptive).
No other arm and no contrast is computed. Writes results/exploratory/RI-001/selection.json.

Usage: python scripts/select_retention_interval.py
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from memory_research.config import SimConfig
from memory_research.design import (
    BASELINE_ARM, EXPLORATORY_SEEDS, RI_CANDIDATES_DAYS, TARGET_MIDPOINT, TARGET_RANGE,
    baseline_recall_by_ri, select_ri, selection_summary,
)
from memory_research.environment import environment

ROOT = Path(__file__).resolve().parents[1]
FROZEN_V1 = ROOT / "research" / "experiments" / "EXP-001" / "config.json"
OUT = ROOT / "results" / "exploratory" / "RI-001" / "selection.json"


def main() -> int:
    base = json.loads(FROZEN_V1.read_text())["base"]
    cfg = SimConfig.from_dict(base)
    t0 = time.perf_counter()
    curve = baseline_recall_by_ri(cfg, EXPLORATORY_SEEDS, RI_CANDIDATES_DAYS)
    chosen = select_ri(curve)
    power = None
    if chosen is not None:
        pcfg = SimConfig.from_dict({**base, "true_model": "power"})
        power = baseline_recall_by_ri(pcfg, EXPLORATORY_SEEDS, [chosen])[chosen]
    dt = time.perf_counter() - t0
    doc = {
        "id": "RI-001",
        "kind": "exploratory",
        "label": "EXPLORATORY baseline-only selection of the central RI (protocol 16.2); uniform arm only, no contrast.",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule": {"section": "research/protocol.md 16.2", "arm": BASELINE_ARM, "seeds": [EXPLORATORY_SEEDS[0], EXPLORATORY_SEEDS[-1]],
                 "candidates_days": [RI_CANDIDATES_DAYS[0], RI_CANDIDATES_DAYS[-1]], "target_range": list(TARGET_RANGE),
                 "target_midpoint": TARGET_MIDPOINT, "step": 1},
        "central_cell_v1": base,
        "summary": selection_summary(curve, chosen),
        "power_law_baseline_R_at_chosen": power,
        "baseline_R_by_ri": {str(k): v for k, v in curve.items()},
        "runtime_s": dt,
        "environment": environment(ROOT),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": doc["summary"], "power_law_baseline_R_at_chosen": power}, indent=1))
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
