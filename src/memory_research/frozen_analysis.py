# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Frozen analyses of EXP-001 to EXP-003 (protocol sections 4, 7 and 10;
experiment protocols sections 4, 13 and 16).

Written and committed before any confirmatory output existed (M3). It only
applies the frozen rules to a validated result file; nothing here is tuned
to results. Implementation choices that the protocols leave implicit are
fixed here and recorded in the decision log (D-015):

* "statement of difference" (Holm): Holm-adjusted paired t p-value < 0.05;
* EXP-001 "shows a positive difference": its primary 95% bootstrap interval
  lies entirely above 0 (section 4 rule "above zero");
* EXP-002 "H0b is not rejected": Holm-adjusted (over the two primary
  contrasts) paired t p-value >= 0.05;
* EXP-003 "share of seeds where each arm ranks first": per seed, the arm(s)
  with the highest R; ties (exact equality) share the credit equally;
* EXP-003 "rank reversal relative to EXP-001": a pair of arms whose order of
  cell means differs from their order of EXP-001 means.
"""

from __future__ import annotations

import itertools
from collections import defaultdict
from typing import Any

import numpy as np

from .report import DELTA, analyse
from .stats import bootstrap_mean_ci, equivalence_verdict, holm, paired_t

ALPHA_TEST = 0.05
SENSITIVITY_METRICS = ("observed_recall", "recall_min", "recall_p10", "mastery_share")
DESCRIPTIVE_METRICS = ("recall_mean", "observed_recall", "mastery_share", "recall_min", "recall_p10",
                       "calibration_mae", "peak_daily_load", "sessions_used", "review_success_rate")


def _per_seed(doc: dict[str, Any], cell_id: str, metric: str) -> dict[str, dict[int, float]]:
    out: dict[str, dict[int, float]] = defaultdict(dict)
    for r in doc["runs"]:
        if r["cell_id"] == cell_id and r["status"] == "ok":
            v = r["metrics"][metric]
            if v is not None:
                out[r["arm"]][r["seed"]] = float(v)
    return out


def contrast(doc: dict[str, Any], cell_id: str, arm: str, baseline: str, metric: str = "recall_mean") -> dict[str, Any]:
    """Paired contrast arm minus baseline over seeds, with every interval of section 7."""
    ps = _per_seed(doc, cell_id, metric)
    seeds = sorted(set(ps[arm]) & set(ps[baseline]))
    if not seeds:
        return {"arm": arm, "metric": metric, "n_pairs": 0}
    d = np.array([ps[arm][s] - ps[baseline][s] for s in seeds])
    t = paired_t(d)
    lo, hi = bootstrap_mean_ci(d)
    base = float(np.mean([ps[baseline][s] for s in seeds]))
    return {
        "arm": arm, "baseline": baseline, "metric": metric, "n_pairs": len(seeds),
        "mean_diff": t["mean"], "sd_diff": t["sd"], "boot_ci_low": lo, "boot_ci_high": hi,
        "boot_half_width": (hi - lo) / 2, "t_ci_low": t["ci_low"], "t_ci_high": t["ci_high"],
        "p_value": t["p_value"], "d_z": t["d_z"], "baseline_mean": base,
        "relative_change": t["mean"] / base if base > 0 else None,
        "verdict_rule": equivalence_verdict(lo, hi, DELTA),
    }


def arm_summary(doc: dict[str, Any], cell_id: str, arms: list[str]) -> list[dict[str, Any]]:
    rows = []
    for arm in arms:
        row: dict[str, Any] = {"cell_id": cell_id, "arm": arm}
        for m in DESCRIPTIVE_METRICS:
            vals = np.array(list(_per_seed(doc, cell_id, m).get(arm, {}).values()), dtype=float)
            row[f"{m}_n"] = int(vals.size)
            row[f"{m}_mean"] = float(vals.mean()) if vals.size else None
            if m == "recall_mean" and vals.size:
                lo, hi = bootstrap_mean_ci(vals)
                row.update({"recall_mean_sd": float(vals.std(ddof=1)) if vals.size > 1 else None,
                            "recall_mean_boot_ci_low": lo, "recall_mean_boot_ci_high": hi})
        rows.append(row)
    return rows


def _holm_family(rows: list[dict[str, Any]], key: str) -> None:
    adj = holm([r.get("p_value") for r in rows])
    for r, a in zip(rows, adj):
        r[key] = a
        r[key.replace("p_holm", "difference_stated")] = (a is not None and a < ALPHA_TEST)


def _counts(doc: dict[str, Any]) -> dict[str, int]:
    return {k: doc["summary"][k] for k in ("n_runs", "n_ok", "n_excluded", "n_failed")}


def analyse_exp001(doc: dict[str, Any]) -> dict[str, Any]:
    """EXP-001: primary greedy - uniform (section 4 rule), Holm over the four
    secondary contrasts, metric-choice sensitivity (protocol 10.3, EXP-001 16)."""
    cell = doc["cells"][0]["cell_id"]
    base = doc["matrix_config"]["baseline"]
    arms = doc["matrix_config"]["arms"]
    others = [a for a in arms if a != base]
    secondary = [contrast(doc, cell, a, base) for a in others]
    _holm_family(secondary, "p_holm")
    primary = next(dict(c) for c in secondary if c["arm"] == "greedy")
    primary["verdict"] = {
        "above zero": "difference above zero (directional prediction supported)",
        "below zero": "prediction contradicted (interval entirely below 0)",
        "equivalent within delta": "practically equivalent within +/-0.02",
        "inconclusive": "inconclusive (interval contains 0 and extends beyond +/-0.02)",
    }[primary["verdict_rule"]]
    sens = [contrast(doc, cell, "greedy", base, m) for m in SENSITIVITY_METRICS]
    for s in sens:
        s["same_sign_as_primary"] = bool(np.sign(s["mean_diff"]) == np.sign(primary["mean_diff"])) if s.get("n_pairs") else None
    return {
        "experiment_id": doc["experiment_id"], "kind": doc["kind"], "counts": _counts(doc), "cell_id": cell,
        "primary": primary, "secondary_contrasts_holm4": secondary,
        "sensitivity_metric_choice": sens,
        "conclusion_restricted_to_mean": any(s.get("same_sign_as_primary") is False for s in sens),
        "arm_summary": arm_summary(doc, cell, arms),
    }


def analyse_exp002(doc: dict[str, Any], exp001: dict[str, Any] | None) -> dict[str, Any]:
    """EXP-002: two primary contrasts with Holm over two, the interpretation
    rule of EXP-002 section 4, and descriptive secondary contrasts (Holm over
    every non-baseline arm, study protocol 7)."""
    cell = doc["cells"][0]["cell_id"]
    base = doc["matrix_config"]["baseline"]
    arms = doc["matrix_config"]["arms"]
    primary = [contrast(doc, cell, a, base) for a in ("greedy-power", "greedy-exp")]
    _holm_family(primary, "p_holm")
    for p in primary:
        p["h0_rejected"] = p["difference_stated"]
    secondary = [contrast(doc, cell, a, base) for a in arms if a != base]
    _holm_family(secondary, "p_holm")
    b = primary[1]
    if exp001 is None:
        rule = {"applicable": None, "note": "EXP-001 analysis not available"}
    else:
        positive = exp001["primary"]["verdict_rule"] == "above zero"
        within = (-DELTA <= b["boot_ci_low"]) and (b["boot_ci_high"] <= DELTA)
        below = b["boot_ci_high"] < 0
        dependent = positive and ((not b["h0_rejected"] and within) or below)
        rule = {
            "applicable": positive,
            "exp001_primary_verdict_rule": exp001["primary"]["verdict_rule"],
            "greedy_exp_h0_rejected_holm2": b["h0_rejected"],
            "greedy_exp_interval_within_delta": within,
            "greedy_exp_interval_below_zero": below,
            "exp001_advantage_dependent_on_model_knowledge": dependent if positive else None,
            "note": ("EXP-001 shows a positive difference; rule evaluated." if positive else
                     "EXP-001 does not show a positive difference (interval not entirely above 0); "
                     "the rule's premise fails, so it declares nothing."),
        }
    return {
        "experiment_id": doc["experiment_id"], "kind": doc["kind"], "counts": _counts(doc), "cell_id": cell,
        "primary_contrasts_holm2": primary, "interpretation_rule": rule,
        "secondary_contrasts_holm_all": secondary, "arm_summary": arm_summary(doc, cell, arms),
    }


def _rank_first_share(doc: dict[str, Any], cell_id: str, arms: list[str]) -> dict[str, float]:
    ps = _per_seed(doc, cell_id, "recall_mean")
    seeds = sorted(set.intersection(*(set(ps[a]) for a in arms))) if all(ps.get(a) for a in arms) else []
    share = {a: 0.0 for a in arms}
    ties = 0
    for s in seeds:
        vals = np.array([ps[a][s] for a in arms])
        best = np.flatnonzero(vals == vals.max())
        ties += best.size > 1
        for i in best:
            share[arms[i]] += 1.0 / best.size
    n = len(seeds)
    return {**{a: (v / n if n else None) for a, v in share.items()}, "_seeds": n, "_seeds_with_tie": ties}


def analyse_exp003(doc: dict[str, Any], exp001: dict[str, Any] | None) -> dict[str, Any]:
    """EXP-003 (descriptive): per-cell means and unadjusted bootstrap intervals,
    rank order, first-rank shares, rank reversals relative to EXP-001, and the
    pre-stated expectations E1 and E2 (not confirmatory)."""
    base = doc["matrix_config"]["baseline"]
    arms = doc["matrix_config"]["arms"]
    generic = analyse(doc)
    means = {(s["cell_id"], s["arm"]): s["mean"] for s in generic["summary"]}
    contrasts = {(c["cell_id"], c["arm"]): c for c in generic["contrasts"]}
    ref_order = None
    if exp001 is not None:
        ref = {r["arm"]: r["recall_mean_mean"] for r in exp001["arm_summary"]}
        ref_order = sorted(ref, key=lambda a: -ref[a])
    cells = []
    for cell in doc["cells"]:
        cid = cell["cell_id"]
        m = {a: means[(cid, a)] for a in arms}
        order = sorted(arms, key=lambda a: -m[a])
        setting = {f: cell["config"][f] for f in ("true_model", "reviews_per_item", "retention_interval_days", "item_distribution")}
        row: dict[str, Any] = {"cell_id": cid, **setting, "rank_order": order,
                               "first_rank_share": _rank_first_share(doc, cid, arms),
                               "means": m}
        for a in arms:
            if a == base:
                continue
            c = contrasts[(cid, a)]
            row[f"diff_{a}"] = c.get("mean_diff")
            row[f"ci_{a}"] = [c.get("boot_ci_low"), c.get("boot_ci_high")]
        if ref_order is not None:
            rev = [f"{a}>{b}" for a, b in itertools.combinations(ref_order, 2) if m[b] > m[a]]
            row["pairwise_reversals_vs_exp001"] = rev
            row["top_arm_differs_from_exp001"] = order[0] != ref_order[0]
            row["greedy_sign_differs_from_exp001"] = (
                np.sign(row["diff_greedy"]) != np.sign(exp001["primary"]["mean_diff"]))
        cells.append(row)
    # E1: massed improves relative to uniform as RI decreases (per model, k, distribution).
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for r in cells:
        groups[(r["true_model"], r["reviews_per_item"], r["item_distribution"])].append(r)
    e1 = []
    for key, rs in sorted(groups.items()):
        rs = sorted(rs, key=lambda r: r["retention_interval_days"])
        d = [r["diff_massed"] for r in rs]
        e1.append({"true_model": key[0], "reviews_per_item": key[1], "item_distribution": key[2],
                   "ri_levels": [r["retention_interval_days"] for r in rs], "massed_minus_uniform": d,
                   "non_increasing_in_ri": all(x >= y for x, y in zip(d, d[1:]))})
    # E2: greedy advantage smallest for homogeneous items (per model, k, RI).
    g2: dict[tuple, dict[str, float]] = defaultdict(dict)
    for r in cells:
        g2[(r["true_model"], r["reviews_per_item"], r["retention_interval_days"])][r["item_distribution"]] = r["diff_greedy"]
    e2 = []
    for key, dd in sorted(g2.items()):
        e2.append({"true_model": key[0], "reviews_per_item": key[1], "retention_interval_days": key[2],
                   "greedy_minus_uniform": dd, "homogeneous_smallest": dd["homogeneous"] <= min(dd.values())})
    return {
        "experiment_id": doc["experiment_id"], "kind": doc["kind"], "counts": _counts(doc),
        "label": "Descriptive (no hypothesis tests); intervals are unadjusted 95% percentile bootstrap intervals.",
        "exp001_rank_order": ref_order, "cells": cells,
        "e1_massed_improves_as_ri_decreases": {"holds_in": sum(x["non_increasing_in_ri"] for x in e1), "of": len(e1), "groups": e1},
        "e2_greedy_advantage_smallest_homogeneous": {"holds_in": sum(x["homogeneous_smallest"] for x in e2), "of": len(e2), "groups": e2},
        "cells_with_any_reversal_vs_exp001": (sum(bool(r.get("pairwise_reversals_vs_exp001")) for r in cells)
                                              if ref_order is not None else None),
        "cells_with_top_arm_change_vs_exp001": (sum(bool(r.get("top_arm_differs_from_exp001")) for r in cells)
                                                if ref_order is not None else None),
        "cells_with_greedy_sign_change_vs_exp001": (sum(bool(r.get("greedy_sign_differs_from_exp001")) for r in cells)
                                                    if ref_order is not None else None),
    }
