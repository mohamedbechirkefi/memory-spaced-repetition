# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""M4 confounder and sensitivity checks (EXPLORATORY; journal id SENS-001).

Never changes or replaces a frozen verdict. Three parts:

A. From the committed raw results of EXP-001 and EXP-002 (no new simulation):
   every arm minus uniform on the recorded secondary metric "recall at RI"
   (RI 1, 7 and 30 days; the schedules do not depend on RI), and how
   unevenly each arm spreads reviews over items (min and max reviews per item).
B. From the raw EXP-003 results (git-ignored, SHA-256 checked against the
   committed SHA256SUMS; no new simulation): pairwise paired bootstrap
   intervals for all 10 arm pairs in all 72 cells, counting rank reversals
   against the EXP-001 order only where the reversed difference is resolved
   (95% interval excludes 0), and repeating the counts without ceiling cells.
   The ceiling threshold (uniform mean R above 0.95) is chosen after seeing
   the M3 results and is therefore post hoc.
C. New simulation on exploratory seeds 5000 to 5049 (disjoint from every
   confirmatory and earlier exploratory seed) at the frozen EXP-001 and
   EXP-002 central settings: replication of the primary contrasts on
   independent learners, and mechanism diagnostics (where reviews fall in
   time and on which items).

  .venv/bin/python scripts/m4_sensitivity.py
Writes results/exploratory/SENS-001/sensitivity.json.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from pathlib import Path

import numpy as np

from memory_research.config import SimConfig
from memory_research.environment import environment, repo_root
from memory_research.items import draw_common_random_numbers
from memory_research.simulate import simulate
from memory_research.stats import bootstrap_mean_ci, equivalence_verdict, paired_t

ROOT = repo_root()
OUT = ROOT / "results" / "exploratory" / "SENS-001"
EXP001_ORDER = ["greedy", "expanding", "uniform", "leitner", "massed"]
CEILING = 0.95
NEW_SEEDS = list(range(5000, 5050))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(exp: str) -> dict:
    p = ROOT / "results" / "confirmatory" / exp / "results.json"
    sums = (ROOT / "results" / "confirmatory" / exp / "SHA256SUMS").read_text().split("\n")
    want = [ln.split()[0] for ln in sums if ln.endswith(" results.json")]
    got = sha256(p)
    if want and want[0] != got:
        raise SystemExit(f"{exp}: results.json SHA-256 {got} differs from SHA256SUMS {want[0]}")
    doc = json.loads(p.read_text())
    doc["_sha256"] = got
    return doc


def summarise(d: np.ndarray) -> dict:
    t = paired_t(d)
    lo, hi = bootstrap_mean_ci(d)
    return {"n": int(d.size), "mean_diff": t["mean"], "boot_ci": [lo, hi], "t_ci": [t["ci_low"], t["ci_high"]],
            "rule": equivalence_verdict(lo, hi)}


def per_seed(doc: dict, cell: str, key, arms) -> dict[str, dict[int, float]]:
    out: dict[str, dict[int, float]] = {a: {} for a in arms}
    for r in doc["runs"]:
        if r["cell_id"] == cell and r["status"] == "ok" and r["arm"] in out:
            out[r["arm"]][r["seed"]] = float(key(r["metrics"]))
    return out


def part_a() -> dict:
    res = {}
    for exp in ("EXP-001", "EXP-002"):
        doc = load(exp)
        arms = doc["matrix_config"]["arms"]
        entry = {"result_sha256": doc["_sha256"], "recall_at_ri": {}, "reviews_per_item": {}}
        for ri in ("1", "7", "30"):
            ps = per_seed(doc, "C000", lambda m, ri=ri: m["recall_mean_at_ri"][ri], arms)
            seeds = sorted(ps["uniform"])
            row = {"uniform_mean": float(np.mean([ps["uniform"][s] for s in seeds]))}
            for a in arms:
                if a != "uniform":
                    row[a] = summarise(np.array([ps[a][s] - ps["uniform"][s] for s in seeds]))
            entry["recall_at_ri"][ri] = row
        for a in arms:
            mx = per_seed(doc, "C000", lambda m: m["max_reviews_per_item"], [a])[a]
            mn = per_seed(doc, "C000", lambda m: m["min_reviews_per_item"], [a])[a]
            entry["reviews_per_item"][a] = {"mean_max": float(np.mean(list(mx.values()))),
                                             "mean_min": float(np.mean(list(mn.values())))}
        res[exp] = entry
    return res


def part_b() -> dict:
    doc = load("EXP-003")
    arms = EXP001_ORDER
    rank = {a: i for i, a in enumerate(EXP001_ORDER)}
    cells = []
    for cell in doc["cells"]:
        cid = cell["cell_id"]
        ps = per_seed(doc, cid, lambda m: m["recall_mean"], arms)
        seeds = sorted(ps["uniform"])
        means = {a: float(np.mean([ps[a][s] for s in seeds])) for a in arms}
        resolved, point = [], []
        better = {a: set() for a in arms}  # a resolved-better than b
        for a, b in itertools.combinations(arms, 2):
            hi_a, lo_a = (a, b) if rank[a] < rank[b] else (b, a)  # EXP-001: hi_a above lo_a
            d = np.array([ps[lo_a][s] - ps[hi_a][s] for s in seeds])
            lo, hi = bootstrap_mean_ci(d)
            if d.mean() > 0:
                point.append(f"{lo_a}>{hi_a}")
            if lo > 0:
                resolved.append(f"{lo_a}>{hi_a}")
                better[lo_a].add(hi_a)
            elif hi < 0:
                better[hi_a].add(lo_a)
        top = max(arms, key=lambda a: means[a])
        top_resolved = len(better[top]) == len(arms) - 1
        c = cell["config"]
        cells.append({"cell_id": cid, "true_model": c["true_model"], "k": c["reviews_per_item"],
                      "ri": c["retention_interval_days"], "items": c["item_distribution"],
                      "uniform_mean": means["uniform"], "ceiling": means["uniform"] > CEILING,
                      "point_reversals": point, "resolved_reversals": resolved,
                      "top_arm": top, "top_arm_resolved": top_resolved})

    def counts(sel):
        tops = {a: 0 for a in arms}
        tops_res = {a: 0 for a in arms}
        for c in sel:
            tops[c["top_arm"]] += 1
            if c["top_arm_resolved"]:
                tops_res[c["top_arm"]] += 1
        return {"cells": len(sel),
                "cells_with_point_reversal": sum(bool(c["point_reversals"]) for c in sel),
                "cells_with_resolved_reversal": sum(bool(c["resolved_reversals"]) for c in sel),
                "top_arm_counts": tops, "top_arm_resolved_counts": tops_res,
                "cells_top_arm_resolved": sum(c["top_arm_resolved"] for c in sel)}

    non_ceiling = [c for c in cells if not c["ceiling"]]
    return {"result_sha256": doc["_sha256"], "ceiling_threshold_uniform_mean": CEILING,
            "all_cells": counts(cells), "non_ceiling_cells": counts(non_ceiling),
            "ceiling_cell_ids": [c["cell_id"] for c in cells if c["ceiling"]],
            "by_model": {m: counts([c for c in cells if c["true_model"] == m]) for m in ("exponential", "power")},
            "cells": cells}


def part_c() -> dict:
    base_exp = json.loads((ROOT / "research/experiments/EXP-001/config.json").read_text())
    base_pow = json.loads((ROOT / "research/experiments/EXP-002/config.json").read_text())
    out = {"seeds": [NEW_SEEDS[0], NEW_SEEDS[-1]]}
    for exp, matrix in (("EXP-001-setting", base_exp), ("EXP-002-setting", base_pow)):
        cfg = SimConfig.from_dict(matrix["base"])
        arms = matrix["arms"]
        R = {a: [] for a in arms}
        diag = {a: {"mean_last_review_day": [], "mean_review_day": [], "hard_third_reviews": [],
                    "easy_third_reviews": [], "items_reviewed_once_or_less": []} for a in arms}
        for seed in NEW_SEEDS:
            crn = draw_common_random_numbers(cfg, seed)
            order = np.argsort(crn.half_lives_days)
            third = cfg.n_items // 3
            hard, easy = order[:third], order[-third:]
            for a in arms:
                tr = simulate(cfg, a, crn)
                R[a].append(float(tr.test_recall_prob.mean()))
                cnt = np.bincount(tr.event_item, minlength=cfg.n_items)
                d = diag[a]
                d["mean_last_review_day"].append(float(tr.last_review_day.mean()))
                d["mean_review_day"].append(float(tr.event_session.mean()))
                d["hard_third_reviews"].append(float(cnt[hard].mean()))
                d["easy_third_reviews"].append(float(cnt[easy].mean()))
                d["items_reviewed_once_or_less"].append(float((cnt <= 1).mean()))
        u = np.array(R["uniform"])
        entry = {"config_hash_source": matrix.get("experiment_id"), "true_model": cfg.true_model,
                 "arm_mean_R": {a: float(np.mean(R[a])) for a in arms},
                 "contrasts_vs_uniform": {a: summarise(np.array(R[a]) - u) for a in arms if a != "uniform"},
                 "diagnostics": {a: {k: float(np.mean(v)) for k, v in diag[a].items()} for a in arms}}
        out[exp] = entry
    return out


def main() -> None:
    t0 = time.perf_counter()
    doc = {"journal_id": "SENS-001", "kind": "exploratory",
           "label": "EXPLORATORY M4 sensitivity check. Never changes or replaces a frozen confirmatory verdict.",
           "environment": environment(ROOT)}
    doc["A_recall_at_other_ri_and_item_spread"] = part_a()
    doc["B_exp003_resolved_reversals"] = part_b()
    doc["C_independent_seed_replication_and_mechanism"] = part_c()
    doc["wall_clock_s"] = time.perf_counter() - t0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sensitivity.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"SENS-001 [exploratory]: wrote {OUT / 'sensitivity.json'} in {doc['wall_clock_s']:.1f} s")


if __name__ == "__main__":
    main()
