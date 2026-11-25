# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Export the published results for the static demo (M5).

Writes ``demo/public/data/results.json`` in the shared template's schema
(``lab-demo-results`` 1.0.0) from committed files only: the frozen analyses
of EXP-001 to EXP-003, the run manifests, the exploratory SENS-001 and
CAL-002 outputs, the frozen EXP-001 configuration, the claims register and
the artifact manifest. Nothing is recomputed except formatting and the
deterministic schedule calendar (the committed engine applied to the frozen
EXP-001 configuration; a design property, not an outcome).

Every ``display`` and ``interval_display`` string is formatted at the
precision the manuscript prints; ``tests/test_demo_export.py`` checks that
each string appears verbatim in ``research/paper/manuscript.md`` and that the
committed file equals a fresh export. No timestamp is written.

Usage: ``.venv/bin/python scripts/export_demo_data.py [--check]``
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from memory_research.config import SimConfig
from memory_research.environment import repo_root
from memory_research.schedules import PLAN_BUILDERS, daily_capacity

ROOT = repo_root()
OUT = Path("demo/public/data/results.json")

SRC = {
    "exp001": "results/confirmatory/EXP-001/analysis/frozen_analysis.json",
    "exp002": "results/confirmatory/EXP-002/analysis/frozen_analysis.json",
    "exp003": "results/confirmatory/EXP-003/analysis/frozen_analysis.json",
    "man001": "results/confirmatory/EXP-001/run_manifest.json",
    "man002": "results/confirmatory/EXP-002/run_manifest.json",
    "man003": "results/confirmatory/EXP-003/run_manifest.json",
    "sens": "results/exploratory/SENS-001/sensitivity.json",
    "cal1": "results/exploratory/CAL-001/calibration.json",
    "cal2": "results/exploratory/CAL-002/model_comparison.json",
    "config001": "research/experiments/EXP-001/config.json",
    "config002": "research/experiments/EXP-002/config.json",
    "claims": "research/claims_register.csv",
    "manifest": "research/publication/artifact_manifest.json",
}

ARMS5 = ("greedy", "expanding", "uniform", "leitner", "massed")


class ExportError(RuntimeError):
    pass


def f4(x: float) -> str:
    """Four decimals, as the manuscript prints probabilities and differences."""
    return f"{x:.4f}"


def ftab(x: float) -> str:
    """Formatter of scripts/build_experiment_records.py (EXP-003 results tables)."""
    return f"{x:.2e}" if (x != 0 and abs(x) < 1e-4) else f"{x:.4f}"


def interval(lo: float, hi: float, fmt=f4) -> str:
    return f"[{fmt(lo)}, {fmt(hi)}]"


def est(label: str, mean: float, lo: float | None, hi: float | None, rule: str | None,
        unit: str = "probability", display: str | None = None, interval_display: str | None = None,
        ci_level: float | None = 0.95) -> dict[str, Any]:
    if lo is None:
        ci_level = None
    return {
        "label": label,
        "estimate": mean,
        "ci_low": lo,
        "ci_high": hi,
        "ci_level": ci_level,
        "unit": unit,
        "display": display if display is not None else f4(mean),
        "interval_display": interval_display if interval_display is not None else (
            interval(lo, hi) if lo is not None else None),
        "rule": rule,
    }


def contrast(c: dict[str, Any], label: str, with_rule: bool = True) -> dict[str, Any]:
    """A contrast row; the frozen rule label is shown only where the manuscript prints it."""
    return est(label, c["mean_diff"], c["boot_ci_low"], c["boot_ci_high"], c["verdict_rule"] if with_rule else None)


def sens_contrast(c: dict[str, Any], label: str) -> dict[str, Any]:
    return est(label, c["mean_diff"], c["boot_ci"][0], c["boot_ci"][1], c["rule"])


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def by_arm(rows: list[dict[str, Any]], arm: str, metric: str = "recall_mean") -> dict[str, Any]:
    hits = [r for r in rows if r["arm"] == arm and r.get("metric", "recall_mean") == metric]
    if len(hits) != 1:
        raise ExportError(f"expected one row for arm {arm!r} metric {metric!r}, found {len(hits)}")
    return hits[0]


def claims_for(result_id: str) -> list[str]:
    out = []
    with (ROOT / SRC["claims"]).open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            ids = [s.strip() for s in row["result_id"].split(";")]
            if result_id in ids:
                out.append(row["claim_id"])
    return out


def calendar(config_rel: str) -> dict[str, Any]:
    """Daily review load of each arm at the frozen EXP-001 setting (schedule definition)."""
    cfg = load(config_rel)
    sc = SimConfig.from_dict(cfg["base"])
    days = list(range(1, sc.n_review_sessions + 1))
    loads: dict[str, list[int]] = {}
    for arm in cfg["arms"]:
        if arm in PLAN_BUILDERS:
            plan = PLAN_BUILDERS[arm](sc)
            load_ = [0] * len(days)
            for sessions in plan:
                for s in sessions:
                    load_[s - 1] += 1
            loads[arm] = load_
        else:
            loads[arm] = [int(x) for x in daily_capacity(sc)]
    for arm, ld in loads.items():
        if sum(ld) != sc.budget:
            raise ExportError(f"calendar for {arm} does not spend the budget")
    return {"days": days, "budget": sc.budget, "n_items": sc.n_items, "loads": loads}


def build() -> dict[str, Any]:
    a1, a2, a3 = load(SRC["exp001"]), load(SRC["exp002"]), load(SRC["exp003"])
    m1, m2, m3 = load(SRC["man001"]), load(SRC["man002"]), load(SRC["man003"])
    sens, cal1, cal2 = load(SRC["sens"]), load(SRC["cal1"]), load(SRC["cal2"])
    cfg1, cfg2 = load(SRC["config001"]), load(SRC["config002"])
    manifest = load(SRC["manifest"])
    if not manifest.get("claims_register", {}).get("claims"):
        raise ExportError("artifact manifest lists no claims")

    revs = {m["environment"]["git_revision"] for m in (m1, m2, m3)}
    if len(revs) != 1 or any(m["environment"].get("git_dirty") for m in (m1, m2, m3)):
        raise ExportError(f"confirmatory runs do not share one clean revision: {revs}")
    run_rev = revs.pop()
    for a, m in ((a1, m1), (a2, m2), (a3, m3)):
        if a["result_sha256"] != m["result_sha256"]:
            raise ExportError(f"{a['experiment_id']}: analysis and run manifest disagree on the result hash")
        c = a["counts"]
        if c["n_failed"] or c["n_excluded"] or c["n_ok"] != c["n_runs"]:
            raise ExportError(f"{a['experiment_id']}: incomplete matrix")

    # ---------------------------------------------------------------- EXP-001
    p1 = a1["primary"]
    sec1 = a1["secondary_contrasts_holm4"]
    met1 = a1["sensitivity_metric_choice"]
    exp001 = {
        "id": "EXP-001",
        "title": "Schedule comparison under exponential forgetting (central setting)",
        "status": "confirmatory, complete (250 of 250 runs, 0 excluded, 0 failed)",
        "kind": "confirmatory",
        "verdict": "Greedy minus uniform: interval entirely above 0, so the difference is above zero and the "
                   "directional prediction is supported. The conclusion is restricted to mean recall, because "
                   "mastery share reverses sign.",
        "estimates": [
            contrast(p1, "greedy minus uniform, mean R (primary)"),
            contrast(by_arm(sec1, "expanding"), "expanding minus uniform, mean R"),
            contrast(by_arm(sec1, "leitner"), "leitner minus uniform, mean R"),
            contrast(by_arm(sec1, "massed"), "massed minus uniform, mean R"),
            contrast(by_arm(met1, "greedy", "observed_recall"), "greedy minus uniform, observed recall", with_rule=False),
            contrast(by_arm(met1, "greedy", "recall_min"), "greedy minus uniform, minimum item recall", with_rule=False),
            contrast(by_arm(met1, "greedy", "recall_p10"), "greedy minus uniform, 10th-percentile item recall", with_rule=False),
            contrast(by_arm(met1, "greedy", "mastery_share"), "greedy minus uniform, mastery share", with_rule=False),
        ],
        "claim_ids": claims_for("EXP-001"),
        "report_path": "research/experiments/EXP-001/report.md",
        "notes": [
            "Differences are arm minus uniform over 50 paired simulated learners (seeds 1000 to 1049), with 95% "
            "percentile bootstrap intervals (10,000 resamples). The effect is small: 0.0162 on a baseline of "
            "0.5327, with standardized paired effect d_z 0.8674.",
            "The greedy scheduler is an oracle: it knows the true model and each item's initial half-life.",
        ],
    }
    if f4(p1["baseline_mean"]) != "0.5327" or f4(p1["d_z"]) != "0.8674":
        raise ExportError("EXP-001 note numbers do not match the analysis")

    # ---------------------------------------------------------------- EXP-002
    pr2 = a2["primary_contrasts_holm2"]
    sec2 = a2["secondary_contrasts_holm_all"]
    rule2 = a2["interpretation_rule"]
    if not rule2["exp001_advantage_dependent_on_model_knowledge"]:
        raise ExportError("EXP-002 interpretation rule outcome changed")
    exp002 = {
        "id": "EXP-002",
        "title": "Oracle advantage and model misspecification under power-law forgetting",
        "status": "confirmatory, complete (300 of 300 runs, 0 excluded, 0 failed)",
        "kind": "confirmatory",
        "verdict": "H0a rejected (greedy with the true power-law model beats uniform). H0b not rejected and its "
                   "interval lies inside ±0.02 (greedy with a misspecified exponential model is classified as "
                   "practically equivalent to uniform). Under the frozen interpretation rule, the EXP-001 greedy "
                   "advantage is declared dependent on model knowledge.",
        "estimates": [
            contrast(by_arm(pr2, "greedy-power"), "greedy-power minus uniform (primary)"),
            contrast(by_arm(pr2, "greedy-exp"), "greedy-exp minus uniform (primary, misspecified model)"),
            contrast(by_arm(sec2, "massed"), "massed minus uniform"),
            contrast(by_arm(sec2, "expanding"), "expanding minus uniform"),
            contrast(by_arm(sec2, "leitner"), "leitner minus uniform"),
        ],
        "claim_ids": claims_for("EXP-002"),
        "report_path": "research/experiments/EXP-002/report.md",
        "notes": [
            "The equivalence classification is fragile (exploratory checks, SENS-001 below): the paired t "
            "interval of greedy-exp reaches 0.0201, and on independent seeds the contrast is above 0. The "
            "stable finding is the size of the drop, from 0.0347 to 0.0085 (about three quarters).",
            "Both greedy arms still receive each item's true initial half-life.",
        ],
    }
    if f4(by_arm(pr2, "greedy-exp")["t_ci_high"]) != "0.0201":
        raise ExportError("EXP-002 note number does not match the analysis")

    exp002_omega = {
        "id": "EXP-002 ω check",
        "title": "Optional descriptive check of EXP-002 with ω in {0.3, 3}",
        "status": "not run (owner decision, 2026-11-25, D-017)",
        "kind": "not run",
        "verdict": "Not evaluated: the check had no frozen configuration, so it was not run. Sensitivity of every "
                   "result to the power-law time scale ω is untested.",
        "estimates": [],
        "claim_ids": [],
        "report_path": "research/experiments/EXP-002/report.md",
        "notes": [
            "Recorded as not run in research/freeze.json (post_freeze_record.not_run), the registry, the "
            "limitations and the manuscript (section 5.2).",
        ],
    }

    # ---------------------------------------------------------------- EXP-003
    e1, e2 = a3["e1_massed_improves_as_ri_decreases"], a3["e2_greedy_advantage_smallest_homogeneous"]
    n_cells = len(a3["cells"])
    below = sum(1 for c in a3["cells"] if c["ci_greedy"][1] < 0)
    above = sum(1 for c in a3["cells"] if c["ci_greedy"][0] > 0)

    def count(label: str, value: int, display: str) -> dict[str, Any]:
        return est(label, value, None, None, None, unit="cells", display=display, interval_display=None)

    exp003 = {
        "id": "EXP-003",
        "title": "Robustness sweep over models, budgets, retention intervals and item distributions",
        "status": "confirmatory run of a descriptive experiment, complete (18,000 of 18,000 runs, 0 excluded, 0 failed)",
        "kind": "descriptive",
        "verdict": "Descriptive, no hypothesis test. The EXP-001 ranking is not stable: 70 of 72 cells reverse at "
                   "least one pair of arms, so EXP-001 does not generalize across the sweep.",
        "estimates": [
            count("cells with at least one pairwise rank reversal against EXP-001",
                  a3["cells_with_any_reversal_vs_exp001"], f"{a3['cells_with_any_reversal_vs_exp001']} of {n_cells}"),
            count("cells whose top arm is not greedy", a3["cells_with_top_arm_change_vs_exp001"],
                  str(a3["cells_with_top_arm_change_vs_exp001"])),
            count("cells where greedy minus uniform has the opposite sign to EXP-001",
                  a3["cells_with_greedy_sign_change_vs_exp001"], str(a3["cells_with_greedy_sign_change_vs_exp001"])),
            count("cells where the greedy minus uniform interval lies entirely above 0 / below 0", above,
                  f"{above} / {below}"),
            count("E1 holds (groups)", e1["holds_in"], f"{e1['holds_in']} of {e1['of']}"),
            count("E2 holds (groups)", e2["holds_in"], f"{e2['holds_in']} of {e2['of']}"),
        ],
        "claim_ids": claims_for("EXP-003"),
        "report_path": "research/experiments/EXP-003/report.md",
        "notes": [
            "Counts use point estimates; per-cell intervals are unadjusted 95% percentile bootstrap intervals "
            "and no single cell supports a confirmatory statement. Counts have no interval.",
        ],
    }

    # ---------------------------------------------------------------- SENS-001 (exploratory)
    sa = sens["A_recall_at_other_ri_and_item_spread"]
    sb = sens["B_exp003_resolved_reversals"]
    sc = sens["C_independent_seed_replication_and_mechanism"]
    c044 = next(c for c in a3["cells"] if c["cell_id"] == "C044")
    sens001 = {
        "id": "SENS-001",
        "title": "Exploratory, post hoc sensitivity checks of the three experiments",
        "status": "exploratory, post hoc (specified after the confirmatory results were seen)",
        "kind": "exploratory",
        "verdict": "Changes no frozen verdict. The EXP-001 direction replicates; the EXP-002 equivalence "
                   "classification is fragile; the EXP-003 instability survives a resolved-difference criterion.",
        "estimates": [
            sens_contrast(sc["EXP-001-setting"]["contrasts_vs_uniform"]["greedy"],
                          "EXP-001 setting, greedy minus uniform, independent seeds 5000 to 5049"),
            est("EXP-001 setting, greedy minus uniform, EXP-003 cell C044 (seeds 3300 to 3349)",
                c044["diff_greedy"], c044["ci_greedy"][0], c044["ci_greedy"][1], None),
            sens_contrast(sc["EXP-002-setting"]["contrasts_vs_uniform"]["greedy-exp"],
                          "EXP-002 setting, greedy-exp minus uniform, independent seeds 5000 to 5049"),
            sens_contrast(sa["EXP-002"]["recall_at_ri"]["7"]["greedy-exp"],
                          "EXP-002 learners, greedy-exp minus uniform at RI 7 days"),
            sens_contrast(sa["EXP-002"]["recall_at_ri"]["30"]["greedy-exp"],
                          "EXP-002 learners, greedy-exp minus uniform at RI 30 days"),
            sens_contrast(sa["EXP-001"]["recall_at_ri"]["1"]["greedy"],
                          "EXP-001 learners, greedy minus uniform at RI 1 day"),
            sens_contrast(sa["EXP-001"]["recall_at_ri"]["7"]["greedy"],
                          "EXP-001 learners, greedy minus uniform at RI 7 days"),
            sens_contrast(sa["EXP-001"]["recall_at_ri"]["30"]["greedy"],
                          "EXP-001 learners, greedy minus uniform at RI 30 days"),
            count("EXP-003 cells with a resolved reversal (interval excludes 0)",
                  sb["all_cells"]["cells_with_resolved_reversal"],
                  f"{sb['all_cells']['cells_with_resolved_reversal']} of {sb['all_cells']['cells']}"),
            count("the same, without the 16 ceiling cells", sb["non_ceiling_cells"]["cells_with_resolved_reversal"],
                  f"{sb['non_ceiling_cells']['cells_with_resolved_reversal']} of {sb['non_ceiling_cells']['cells']}"),
        ],
        "claim_ids": claims_for("SENS-001"),
        "report_path": "research/paper/supplementary.md",
        "notes": [
            "Exploratory and post hoc: it uses committed raw outputs and new exploratory seeds 5000 to 5049, and "
            "never replaces a frozen verdict. The C044 row is a confirmatory EXP-003 cell, listed here because "
            "the manuscript uses it as an independent-seed replication.",
        ],
    }
    if len(sb["ceiling_cell_ids"]) != 16:
        raise ExportError("ceiling cell count changed")

    # ---------------------------------------------------------------- CAL-002 (exploratory design input)
    ll = cal2["comparison"]["holdout_log_loss_per_trial"]
    fb = cal2["comparison"]["family_best"]
    if not cal2["comparison"]["neither_beats_constant"]:
        raise ExportError("CAL-002 outcome changed")
    unit_ll = "log-loss per trial (lower is better)"
    cal002 = {
        "id": "CAL-002",
        "title": "Do the forgetting models predict real first-review recall? (Duolingo traces, held out)",
        "status": "exploratory design input (negative result)",
        "kind": "exploratory",
        "verdict": "No. Neither forgetting model predicts held-out first-review recall better than a constant, so "
                   "every simulated result is conditional on the assumed memory model.",
        "estimates": [
            est("constant predictor", ll["constant"], None, None, None, unit=unit_ll, display=f"{ll['constant']:.3f}"),
            est("best exponential curve", fb["exponential"]["log_loss"], None, None, None, unit=unit_ll,
                display=f"{fb['exponential']['log_loss']:.3f}"),
            est("best power-law curve", fb["power"]["log_loss"], None, None, None, unit=unit_ll,
                display=f"{fb['power']['log_loss']:.3f}"),
        ],
        "claim_ids": claims_for("CAL-002"),
        "report_path": "research/paper/manuscript.md",
        "notes": [
            "Held-out trials: 427,005. No interval was computed for these log-loss values.",
        ],
    }
    if cal2["comparison"]["n_trials_V"] != 427005:
        raise ExportError("CAL-002 trial count changed")

    # ---------------------------------------------------------------- assumptions
    b1 = cfg1["base"]
    fit = cal1["calibration"]["fit_split_C"]
    if f"{fit['h0_days']:.1f}" != f"{b1['h0_days']:.1f}" or f"{fit['lognormal_sigma']:.3f}" != f"{b1['lognormal_sigma']:.3f}":
        raise ExportError("frozen configuration does not match CAL-001")
    cfg_src = SRC["config001"]
    assumptions = [
        {"name": "Items per learner, N", "value": f"{b1['n_items']}", "source": f"frozen configuration ({cfg_src})", "kind": "design"},
        {"name": "Study window, D", "value": f"{b1['window_days']} days (review sessions on days 1 to {b1['window_days'] - 1})", "source": "frozen configuration", "kind": "design"},
        {"name": "Budget", "value": f"{b1['reviews_per_item']} reviews per item, B = {b1['reviews_per_item'] * b1['n_items']} reviews", "source": "frozen configuration", "kind": "design"},
        {"name": "Retention interval, RI", "value": f"{b1['retention_interval_days']} days after the last session", "source": "chosen by a pre-stated rule from the uniform arm alone (RI-001); a design choice, not a typical use case", "kind": "design"},
        {"name": "Initial half-life, h0", "value": f"{b1['h0_days']:.1f} days", "source": "calibrated to public Duolingo traces (CAL-001)", "kind": "calibrated"},
        {"name": "Item spread, σ (lognormal)", "value": f"{b1['lognormal_sigma']}", "source": "calibrated to public Duolingo traces (CAL-001)", "kind": "calibrated"},
        {"name": "Success update, α", "value": f"{b1['alpha']}", "source": "planning value, not an estimate", "kind": "assumption"},
        {"name": "Failure update, β", "value": f"{b1['beta']}", "source": "planning value, not an estimate", "kind": "assumption"},
        {"name": "Power-law time scale, ω", "value": f"{b1['omega_per_day']:g} per day", "source": "planning value, not an estimate; sensitivity untested (D-017)", "kind": "assumption"},
        {"name": "Scheduler knowledge", "value": "the greedy arms know each item's true initial half-life; EXP-001 greedy also knows the true model", "source": "protocol (information advantage)", "kind": "assumption"},
        {"name": "Equivalence margin", "value": "±0.02 in recall probability", "source": "frozen decision rule", "kind": "design"},
    ]

    limitations = [
        "Simulation only: recall is a model probability, never a human measurement. No claim of human learning gains.",
        "Neither forgetting model beats a constant predictor of held-out real first-review recall (CAL-002); the calibration fixes the time scale of the items, not the shape of forgetting.",
        "The retrieval update ignores the gap since the last review, so the models contain no spacing effect in the psychological sense.",
        "Both greedy arms know each item's true initial half-life; EXP-001's greedy also knows the true model.",
        "Load confound: expanding and massed concentrate all reviews on 4 sessions (peak 50 per session); the other arms use 27 sessions (peak 8).",
        "The central retention interval (281 days) is a design choice; α, β and ω are planning values, and robustness to ω is untested (D-017).",
        "The EXP-002 \"equivalent within 0.02\" classification sits on the margin and does not replicate on independent seeds or shorter retention intervals (exploratory).",
        "Draft-setting contrasts with the opposite sign were seen before the freeze (disclosed in the freeze record).",
        "EXP-003 has 288 unadjusted arm-versus-uniform intervals; no single cell supports a confirmatory statement. SENS-001 is post hoc.",
        "The calibration data are Duolingo learners and words from 2013; they represent no other population.",
    ]

    # ---------------------------------------------------------------- extensions
    sweep = []
    for c in a3["cells"]:
        sweep.append({
            "cell_id": c["cell_id"],
            "true_model": c["true_model"],
            "reviews_per_item": c["reviews_per_item"],
            "retention_interval_days": c["retention_interval_days"],
            "item_distribution": c["item_distribution"],
            "means": {a: c["means"][a] for a in ARMS5},
            "means_display": {a: ftab(c["means"][a]) for a in ARMS5},
            "greedy_minus_uniform": {
                "estimate": c["diff_greedy"],
                "ci_low": c["ci_greedy"][0],
                "ci_high": c["ci_greedy"][1],
                "display": ftab(c["diff_greedy"]),
                "interval_display": interval(c["ci_greedy"][0], c["ci_greedy"][1], ftab),
            },
            "rank_order": list(c["rank_order"]),
        })

    cal = calendar(SRC["config001"])
    measured = {r["arm"]: r for r in a1["arm_summary"]}
    for arm, ld in cal["loads"].items():
        if max(ld) != measured[arm]["peak_daily_load_mean"] or sum(1 for x in ld if x) != measured[arm]["sessions_used_mean"]:
            raise ExportError(f"calendar for {arm} disagrees with the measured peak load or sessions used")
    cal["measured"] = {arm: {"peak_daily_load": int(measured[arm]["peak_daily_load_mean"]),
                             "sessions_used": int(measured[arm]["sessions_used_mean"]),
                             "mean_R": measured[arm]["recall_mean_mean"],
                             "mean_R_display": f4(measured[arm]["recall_mean_mean"]),
                             "ci_low": measured[arm]["recall_mean_boot_ci_low"],
                             "ci_high": measured[arm]["recall_mean_boot_ci_high"],
                             "mean_R_interval_display": interval(measured[arm]["recall_mean_boot_ci_low"],
                                                                 measured[arm]["recall_mean_boot_ci_high"])}
                       for arm in cal["loads"]}
    cal["note"] = ("Schedule definition at the frozen EXP-001 setting: the fixed arms' plans and the adaptive arms' "
                   "daily capacity, computed by the committed engine. Which items the adaptive arms review varies "
                   "by learner. The peak load and sessions used agree with the measured runs.")

    b2 = cfg2["base"]
    sandbox_scenarios = [
        {"id": "exp001", "label": "EXP-001 setting (exponential forgetting)", "config": b1, "arms": cfg1["arms"]},
        {"id": "exp002", "label": "EXP-002 setting (power-law forgetting, matched and misspecified greedy)", "config": b2, "arms": cfg2["arms"]},
        {"id": "small-budget", "label": "Small budget (k = 2, RI 281 days, exponential)", "config": {**b1, "reviews_per_item": 2}, "arms": cfg1["arms"]},
        {"id": "short-ri", "label": "Short retention interval (RI 7 days, exponential)", "config": {**b1, "retention_interval_days": 7}, "arms": cfg1["arms"]},
    ]

    sources = [{"path": rel, "sha256": hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()} for rel in SRC.values()]

    return {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "MEMORY",
        "question": "Which review schedule maximizes modelled delayed recall of a set of synthetic items under a "
                    "fixed study budget (a fixed total number of review events within a fixed study window)?",
        "status_label": "Simulation study. Independent research manuscript / preprint draft, not peer-reviewed. "
                        "Simulated learners, not human participants.",
        "code_revision": run_rev,
        "sources": sources,
        "experiments": [exp001, exp002, exp002_omega, exp003, sens001, cal002],
        "assumptions": assumptions,
        "limitations": limitations,
        "sweep": sweep,
        "calendar": cal,
        "sandbox_scenarios": sandbox_scenarios,
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="compare with the committed file instead of writing")
    args = ap.parse_args(argv)
    text = render(build())
    path = ROOT / OUT
    if args.check:
        same = path.is_file() and path.read_text(encoding="utf-8") == text
        print("EXPORT-CHECK " + ("PASS" if same else "FAIL"))
        return 0 if same else 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
