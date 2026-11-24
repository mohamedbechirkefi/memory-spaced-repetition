# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""M3 metric validation on known cases (exploratory; no confirmatory seed).

Each metric of protocol section 5 is computed by the package on a case whose
value is known by hand, and compared with that value. The statistics of
section 7 are checked on small known inputs. Writes
results/exploratory/METRICVAL-001/validation.json and exits non-zero if any
check fails.

  .venv/bin/python scripts/validate_metrics.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

from memory_research.config import SimConfig
from memory_research.environment import environment, repo_root
from memory_research.items import CommonRandomNumbers, draw_common_random_numbers
from memory_research.metrics import compute_metrics
from memory_research.simulate import simulate
from memory_research.stats import bootstrap_mean_ci, equivalence_verdict, holm, paired_t

checks: list[dict] = []


def check(name: str, got, want, tol: float = 1e-12) -> None:
    ok = (got is None and want is None) or (got is not None and want is not None and abs(float(got) - float(want)) <= tol)
    checks.append({"check": name, "got": got, "expected": want, "tolerance": tol, "pass": bool(ok)})


def crn(c: SimConfig, h, ru, tu, seed=0) -> CommonRandomNumbers:
    return CommonRandomNumbers(seed, np.asarray(h, float), np.asarray(ru, float), np.asarray(tu, float))


# Case A: two homogeneous items, h = 10 days, D = 3, k = 1, massed (both reviewed at session 2),
# every review succeeds (u = 0); test at 2 + RI with RI = 5; alpha 0.4.
c = SimConfig(n_items=2, window_days=3, retention_interval_days=5, reviews_per_item=1, h0_days=10.0,
              item_distribution="homogeneous", true_model="exponential")
k = crn(c, [10.0, 10.0], [[0.0, 0.0], [0.0, 0.0]], [0.5, 0.9])
m = compute_metrics(c, simulate(c, "massed", k), k)
r = 2 ** (-0.6 * 5 / 10)  # n = 0.6 ln2 / 10 after one success; delta 5 days
check("A recall_mean (massed, exponential)", m["recall_mean"], r)
check("A observed_recall (u = 0.5, 0.9 vs m = 0.812)", m["observed_recall"], 0.5)
check("A mastery_share (m < 0.9)", m["mastery_share"], 0.0)
check("A recall_min", m["recall_min"], r)
check("A recall_p10", m["recall_p10"], r)
check("A recall at RI 1", m["recall_mean_at_ri"]["1"], 2 ** (-0.6 * 1 / 10))
check("A recall at RI 30", m["recall_mean_at_ri"]["30"], 2 ** (-0.6 * 30 / 10))
check("A peak_daily_load (both at session 2)", m["peak_daily_load"], 2)
check("A sessions_used", m["sessions_used"], 1)
check("A review_events = B", m["review_events"], 2)
check("A calibration_mae for a non-adaptive arm", m["calibration_mae"], None)

# Case B: two items with different half-lives (1 and 100 days), failure at the review of item 0.
c = SimConfig(n_items=2, window_days=2, retention_interval_days=2, reviews_per_item=1, h0_days=1.0,
              item_distribution="homogeneous", true_model="exponential", alpha=0.4, beta=0.6)
k = crn(c, [1.0, 100.0], [[1.0], [0.0]], [0.0, 0.0])
m = compute_metrics(c, simulate(c, "uniform", k), k)
r0 = 2 ** (-1.6 * 2 / 1.0)
r1 = 2 ** (-0.6 * 2 / 100.0)
check("B recall_mean (one failure, one success)", m["recall_mean"], (r0 + r1) / 2)
check("B mastery_share (item 1 >= 0.9 only)", m["mastery_share"], 0.5)
check("B recall_min", m["recall_min"], r0)
check("B recall_p10 (linear interpolation, numpy default)", m["recall_p10"], r0 + 0.1 * (r1 - r0))
check("B observed_recall (u = 0)", m["observed_recall"], 1.0)
check("B review_success_rate", m["review_success_rate"], 0.5)

# Case C: power law, one item, h = 5 days, omega 1, massed, success; test 1 + RI with RI = 3.
c = SimConfig(n_items=1, window_days=2, retention_interval_days=3, reviews_per_item=1, h0_days=5.0,
              item_distribution="homogeneous", true_model="power", omega_per_day=1.0)
k = crn(c, [5.0], [[0.0]], [0.5])
m = compute_metrics(c, simulate(c, "massed", k), k)
n0 = math.log(2) / math.log1p(5.0)
check("C recall_mean (power law)", m["recall_mean"], (1 + 3.0) ** (-0.6 * n0))

# Case D: the oracle greedy scheduler predicts the true recall exactly (calibration 0)
c = SimConfig(n_items=10, window_days=28, retention_interval_days=281, reviews_per_item=4, h0_days=54.0,
              lognormal_sigma=0.759)
for seed in (1, 2, 3):
    k = draw_common_random_numbers(c, seed)
    m = compute_metrics(c, simulate(c, "greedy", k), k)
    check(f"D greedy oracle calibration_mae = 0 (seed {seed})", m["calibration_mae"], 0.0, tol=1e-12)
    mg = compute_metrics(c, simulate(c, "leitner", k), k)
    check(f"D leitner calibration_mae is not reported (model-free, seed {seed})", mg["calibration_mae"], None)

# Statistics of section 7 on known inputs.
d = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
t = paired_t(d)
check("S paired t mean", t["mean"], 3.0)
check("S paired t sd", t["sd"], math.sqrt(2.5))
check("S paired t 95% half-width (t(0.975,4) = 2.7764451)", t["ci_high"] - 3.0, 2.7764451052 * math.sqrt(2.5) / math.sqrt(5), tol=1e-8)
check("S d_z", t["d_z"], 3.0 / math.sqrt(2.5))
lo, hi = bootstrap_mean_ci(np.full(50, 0.3))
check("S bootstrap of a constant: low", lo, 0.3)
check("S bootstrap of a constant: high", hi, 0.3)
h = holm([0.01, 0.04, 0.03, 0.2])
for got, want, lab in zip(h, [0.04, 0.09, 0.09, 0.2], "abcd"):
    check(f"S holm {lab}", got, want)
for lo_, hi_, want in [(0.001, 0.01, "above zero"), (-0.01, -0.001, "below zero"), (-0.01, 0.015, "equivalent within delta"),
                       (-0.03, 0.01, "inconclusive")]:
    checks.append({"check": f"S verdict [{lo_}, {hi_}]", "got": equivalence_verdict(lo_, hi_), "expected": want,
                   "pass": equivalence_verdict(lo_, hi_) == want})

root = repo_root()
out = root / "results" / "exploratory" / "METRICVAL-001"
out.mkdir(parents=True, exist_ok=True)
n_fail = sum(not c_["pass"] for c_ in checks)
doc = {"id": "METRICVAL-001", "label": "EXPLORATORY metric validation on hand-computed cases; no confirmatory seed.",
       "environment": environment(root), "n_checks": len(checks), "n_failed": n_fail, "checks": checks}
(out / "validation.json").write_text(json.dumps(doc, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
print(f"METRICVAL-001: {len(checks)} checks, {n_fail} failed")
for c_ in checks:
    if not c_["pass"]:
        print("FAIL", c_)
sys.exit(1 if n_fail else 0)
