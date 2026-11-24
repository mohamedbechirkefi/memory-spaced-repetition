# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""CAL-002 (exploratory): diagnose the forgetting-model misfit (protocol 16.1, rule (a)).

Reads the processed DS01 calibration subset written by scripts/calibrate_duolingo.py
(data/processed/DS01_first_review_subset.npz, git-ignored), compares the exponential
and power-law curves with a constant predictor by held-out log-loss on split V, and
writes aggregate values only to results/exploratory/CAL-002/model_comparison.json.
No simulation is run and no schedule arm is evaluated.

Usage: python scripts/diagnose_forgetting_fit.py
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from memory_research.duolingo import Processed, compare_models
from memory_research.environment import environment

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed" / "DS01_first_review_subset.npz"
OUT = ROOT / "results" / "exploratory" / "CAL-002" / "model_comparison.json"
FROZEN = ROOT / "research" / "experiments" / "EXP-001" / "config.json"


def main() -> int:
    sha = hashlib.sha256(PROCESSED.read_bytes()).hexdigest()
    z = np.load(PROCESSED, allow_pickle=False)
    data = Processed(list(z["lexemes"]), z["lexeme"], z["split_c"], z["delta_days"], z["trials"], z["successes"])
    base = json.loads(FROZEN.read_text())["base"]
    t0 = time.perf_counter()
    res = compare_models(data, base["h0_days"], base["lognormal_sigma"], base["omega_per_day"])
    dt = time.perf_counter() - t0
    doc = {
        "id": "CAL-002",
        "kind": "exploratory",
        "label": "EXPLORATORY diagnosis of the forgetting-model fit on DS01; no schedule arm, no contrast.",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {"dataset_id": "DS01", "processed_file": str(PROCESSED.relative_to(ROOT)), "processed_sha256": sha,
                 "written_by": "scripts/calibrate_duolingo.py (CAL-001)"},
        "comparison": res,
        "runtime_s": dt,
        "environment": environment(ROOT),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"holdout_log_loss_per_trial": res["holdout_log_loss_per_trial"],
                      "family_best": res["family_best"], "better_family": res["better_family"],
                      "neither_beats_constant": res["neither_beats_constant"]}, indent=1))
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
