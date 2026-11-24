# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Report generator: tables, figures and a Markdown report (optionally PDF)
built only from a validated result file. Numbers are never typed by hand."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from .runner import load_result
from .stats import bootstrap_mean_ci, equivalence_verdict, holm, paired_t, t_quantile

SEED_SD_THRESHOLD = 0.07  # protocol section 6: 50 seeds give half-width < delta when s < 0.07
PLANNED_SEEDS = 50
DELTA = 0.02
DEFAULT_PANDOC = "/Users/bechir/research/labs/.tools/pandoc"
DEFAULT_TYPST_PYTHON = "/Users/bechir/research/labs/.tools/py/bin/python"


def _fmt(x: Any, nd: int = 4) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float):
        if math.isnan(x):
            return "n/a"
        return f"{x:.{nd}f}"
    return str(x)


def _md_table(header: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(_fmt(v) for v in row) + " |" for row in rows]
    return "\n".join(out)


def analyse(doc: dict[str, Any], metric: str = "recall_mean") -> dict[str, Any]:
    """Per-cell, per-arm summaries and paired contrasts versus the baseline."""
    baseline = doc["matrix_config"].get("baseline", "uniform")
    arms = doc["matrix_config"]["arms"]
    by: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for r in doc["runs"]:
        if r["status"] == "ok":
            by[(r["cell_id"], r["arm"])][r["seed"]] = r["metrics"][metric]
    summary, contrasts = [], []
    for cell in doc["cells"]:
        cid = cell["cell_id"]
        for arm in arms:
            vals = np.array(list(by[(cid, arm)].values()), dtype=float)
            summary.append({
                "cell_id": cid, **{f"factor_{k}": v for k, v in cell["factors"].items()}, "arm": arm,
                "n_ok": int(vals.size),
                "mean": float(vals.mean()) if vals.size else None,
                "sd": float(vals.std(ddof=1)) if vals.size > 1 else None,
                "median": float(np.median(vals)) if vals.size else None,
                "min": float(vals.min()) if vals.size else None,
                "max": float(vals.max()) if vals.size else None,
            })
        base = by[(cid, baseline)]
        rows = []
        for arm in arms:
            if arm == baseline:
                continue
            other = by[(cid, arm)]
            seeds = sorted(set(base) & set(other))
            if not seeds:
                rows.append({"cell_id": cid, "arm": arm, "n_pairs": 0})
                continue
            diff = np.array([other[s] - base[s] for s in seeds])
            t = paired_t(diff)
            lo, hi = bootstrap_mean_ci(diff)
            base_mean = float(np.mean([base[s] for s in seeds]))
            rows.append({
                "cell_id": cid, **{f"factor_{k}": v for k, v in cell["factors"].items()}, "arm": arm,
                "baseline": baseline, "n_pairs": len(seeds), "mean_diff": t["mean"], "sd_diff": t["sd"],
                "boot_ci_low": lo, "boot_ci_high": hi, "t_ci_low": t["ci_low"], "t_ci_high": t["ci_high"],
                "p_value": t["p_value"], "d_z": t["d_z"],
                "relative_change": t["mean"] / base_mean if base_mean > 0 else None,
                "projected_half_width_50": (t_quantile(0.975, PLANNED_SEEDS - 1) * t["sd"] / math.sqrt(PLANNED_SEEDS)) if t["sd"] is not None else None,
                "verdict_rule": equivalence_verdict(lo, hi, DELTA),
            })
        adj = holm([r.get("p_value") for r in rows])
        for r, a in zip(rows, adj):
            r["p_holm"] = a
        contrasts += rows
    return {"baseline": baseline, "metric": metric, "summary": summary, "contrasts": contrasts}


def runtime_summary(doc: dict[str, Any]) -> dict[str, Any]:
    rt = defaultdict(list)
    for r in doc["runs"]:
        rt[r["arm"]].append(r["runtime_s"])
    allrt = [r["runtime_s"] for r in doc["runs"]]
    return {
        "per_arm_mean_s": {a: float(np.mean(v)) for a, v in rt.items()},
        "mean_s": float(np.mean(allrt)) if allrt else None,
        "median_s": float(np.median(allrt)) if allrt else None,
        "max_s": float(np.max(allrt)) if allrt else None,
        "wall_clock_s": doc["summary"]["wall_clock_s"],
        "peak_rss_bytes": max((r["peak_rss_bytes"] or 0) for r in doc["runs"]) if doc["runs"] else None,
    }


def degenerate_flags(doc: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    """Automatic planning diagnostics: floor, ceiling, zero variance, starved items."""
    flags = []
    for s in analysis["summary"]:
        if s["n_ok"] == 0:
            flags.append(f"{s['cell_id']} {s['arm']}: no valid run")
        elif s["max"] is not None and s["max"] < 0.05:
            flags.append(f"{s['cell_id']} {s['arm']}: floor (every seed has mean recall < 0.05)")
        elif s["min"] is not None and s["min"] > 0.95:
            flags.append(f"{s['cell_id']} {s['arm']}: ceiling (every seed has mean recall > 0.95)")
        elif s["mean"] is not None and s["mean"] < 0.10:
            flags.append(f"{s['cell_id']} {s['arm']}: near floor (mean recall {s['mean']:.4f} < 0.10)")
    for c in analysis["contrasts"]:
        if c.get("sd_diff") == 0.0:
            flags.append(f"{c['cell_id']} {c['arm']}: zero variance of paired differences (deterministic contrast)")
    starved: dict[tuple[str, str], list[int]] = defaultdict(list)
    for r in doc["runs"]:
        if r["status"] == "ok":
            starved[(r["cell_id"], r["arm"])].append(r["metrics"]["items_never_reviewed"])
    n_items = {c["cell_id"]: c["config"]["n_items"] for c in doc["cells"]}
    for (cid, arm), v in starved.items():
        if any(v):
            flags.append(f"{cid} {arm}: items never reviewed in {sum(1 for x in v if x)}/{len(v)} runs "
                         f"(mean {np.mean(v):.1f} of {n_items[cid]} items)")
    return flags


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in keys})


def make_figures(doc: dict[str, Any], analysis: dict[str, Any], fig_dir: Path, metric: str = "recall_mean") -> list[dict[str, str]]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"svg.hashsalt": "memory", "font.size": 9})
    fig_dir.mkdir(parents=True, exist_ok=True)
    baseline = analysis["baseline"]
    figs = []
    cells = doc["cells"]
    exploratory = doc["kind"] == "exploratory"
    tag = "EXPLORATORY" if exploratory else "CONFIRMATORY"
    note = "Exploratory; not a finding." if exploratory else "Confirmatory run against the frozen protocol."
    arms = [a for a in doc["matrix_config"]["arms"] if a != baseline]
    if len(cells) <= 4:
        for cell in cells:
            cid = cell["cell_id"]
            base = {r["seed"]: r["metrics"][metric] for r in doc["runs"] if r["cell_id"] == cid and r["arm"] == baseline and r["status"] == "ok"}
            fig, ax = plt.subplots(figsize=(6.0, 3.2))
            for k, arm in enumerate(arms):
                d = [r["metrics"][metric] - base[r["seed"]] for r in doc["runs"]
                     if r["cell_id"] == cid and r["arm"] == arm and r["status"] == "ok" and r["seed"] in base]
                x = np.full(len(d), k) + np.linspace(-0.15, 0.15, len(d)) if d else []
                ax.plot(x, d, "o", ms=3.5, alpha=0.7, color="0.25")
                if d:
                    ax.plot([k - 0.25, k + 0.25], [np.mean(d)] * 2, "-", color="tab:red", lw=2)
            ax.axhline(0, color="0.5", lw=0.8)
            ax.set_xticks(range(len(arms)), arms)
            ax.set_ylabel(f"{metric} minus {baseline}\n(probability units)")
            ax.set_title(f"{doc['experiment_id']} {cid}: paired differences per seed ({tag})")
            fig.tight_layout()
            name = f"paired_diff_{cid}"
            fig.savefig(fig_dir / f"{name}.svg")
            fig.savefig(fig_dir / f"{name}.png", dpi=150)
            plt.close(fig)
            n = len(base)
            figs.append({"file": f"{name}.svg", "caption": (
                f"Paired difference in {metric} (arm minus {baseline}) for each seed, cell {cid}; dots are seeds "
                f"(n = {n} baseline runs), red bars are means. {note}"),
                "alt": f"Strip plot of per-seed paired differences against {baseline} for {len(arms)} arms in cell {cid}."})
    elif arms:
        fig, ax = plt.subplots(figsize=(7.0, 0.18 * len(cells) + 1.2))
        cmap = plt.get_cmap("tab10")
        for k, arm in enumerate(arms):
            rows = [c for c in analysis["contrasts"] if c["arm"] == arm and c.get("n_pairs")]
            y = np.array([int(c["cell_id"][1:]) for c in rows]) + (k - len(arms) / 2) * 0.12
            ax.errorbar([c["mean_diff"] for c in rows], y,
                        xerr=[[c["mean_diff"] - c["boot_ci_low"] for c in rows], [c["boot_ci_high"] - c["mean_diff"] for c in rows]],
                        fmt="o", ms=2.5, lw=0.8, color=cmap(k), label=arm)
        ax.axvline(0, color="0.5", lw=0.8)
        ax.set_yticks(range(len(cells)), [c["cell_id"] for c in cells], fontsize=5)
        ax.invert_yaxis()
        ax.set_xlabel(f"mean paired difference in {metric} versus {baseline} (probability units), 95% bootstrap interval")
        ax.legend(fontsize=7, loc="lower right")
        ax.set_title(f"{doc['experiment_id']}: all cells ({tag})")
        fig.tight_layout()
        fig.savefig(fig_dir / "cells_overview.svg")
        fig.savefig(fig_dir / "cells_overview.png", dpi=150)
        plt.close(fig)
        figs.append({"file": "cells_overview.svg", "caption": (
            f"Mean paired difference versus {baseline} per cell and arm with 95% percentile bootstrap intervals over seeds. "
            f"Cell factor levels are listed in contrasts.csv. {note}"),
            "alt": f"Dot plot with interval bars of mean differences against {baseline} for {len(cells)} cells."})
    return figs


def build_report(result_path: Path, out_dir: Path, pdf: bool = False, metric: str = "recall_mean") -> dict[str, Path]:
    result_path = Path(result_path)
    doc = load_result(result_path)  # fail closed on malformed input
    result_sha = hashlib.sha256(result_path.read_bytes()).hexdigest()
    out_dir.mkdir(parents=True, exist_ok=True)
    analysis = analyse(doc, metric)
    rt = runtime_summary(doc)
    flags = degenerate_flags(doc, analysis)
    _write_csv(analysis["summary"], out_dir / "summary.csv")
    _write_csv(analysis["contrasts"], out_dir / "contrasts.csv")
    figs = make_figures(doc, analysis, out_dir / "figures", metric)
    env = doc["environment"]
    from .environment import environment as _env
    gen = _env()
    generator = f"memory_research.report {gen['package_version']} at `{gen['git_revision']}` (dirty: {gen['git_dirty']})"
    exploratory = doc["kind"] == "exploratory"
    lines = [
        "<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->",
        f"# {doc['experiment_id']} {'exploratory ' if exploratory else ''}report (generated)",
        "",
        f"**{doc['label']}**" if exploratory else f"**{doc['label']}**",
        "",
        f"Generated by `memory_research.report` from `{result_path.name}` (SHA-256 `{result_sha}`). "
        "Every number below is computed from that file; none is typed by hand. Simulated learners only; "
        "no claim about human learning.",
        "",
        "## Provenance",
        "",
        "\n".join(f"- {k}: {v}" for k, v in [
            ["experiment", doc["experiment_id"]], ["kind", doc["kind"]], ["created (UTC)", doc["created_utc"]],
            ["matrix config SHA-256", f"`{doc['matrix_config_hash']}`"],
            ["protocol", f"{doc['protocol']['path']} (frozen: {doc['protocol']['frozen']})"],
            ["code revision of the run", f"`{env['git_revision']}` (dirty: {env['git_dirty']})"],
            ["report generator", generator],
            ["python / numpy", f"{env['python']} / {env['packages'].get('numpy')}"],
            ["OS", env["os"]], ["CPU", env["cpu"]],
        ]),
        "",
        "## Runs",
        "",
        _md_table(["runs", "ok", "excluded", "failed"], [[doc["summary"][k] for k in ("n_runs", "n_ok", "n_excluded", "n_failed")]]),
        "",
    ]
    bad = [r for r in doc["runs"] if r["status"] != "ok"]
    if bad:
        lines += ["Non-ok runs (kept, with reasons):", ""] + [f"- `{r['run_id']}` {r['status']}: {'; '.join(r['reasons'])}" for r in bad] + [""]
    lines += [
        "## Runtime",
        "",
        _md_table(["quantity", "value"], [
            ["mean runtime per run (s)", rt["mean_s"]], ["median runtime per run (s)", rt["median_s"]],
            ["max runtime per run (s)", rt["max_s"]], ["wall clock, whole matrix (s)", rt["wall_clock_s"]],
            ["process peak RSS (MiB)", (rt["peak_rss_bytes"] or 0) / 2**20],
        ] + [[f"mean runtime per run, {a} (s)", v] for a, v in rt["per_arm_mean_s"].items()]),
        "",
        "## Cells",
        "",
        _md_table(["cell", "factors", "config SHA-256 (first 12)"],
                  [[c["cell_id"], json.dumps(c["factors"], sort_keys=True) or "{}", c["config_hash"][:12]] for c in doc["cells"]]),
        "",
        f"## Primary metric `{metric}` per arm",
        "",
        _md_table(["cell", "arm", "n", "mean", "SD", "median", "min", "max"],
                  [[s["cell_id"], s["arm"], s["n_ok"], s["mean"], s["sd"], s["median"], s["min"], s["max"]] for s in analysis["summary"]]),
        "",
        f"## Paired differences versus `{analysis['baseline']}`",
        "",
        "Mean difference over seeds, SD of the paired differences (`s`), 95% percentile bootstrap interval "
        "(10,000 resamples, seed 20261124), paired t interval, Holm-adjusted p within the cell, standardized "
        "effect `d_z`, and the projected 95% half-width with 50 seeds (`t(0.975, 49) s / sqrt(50)`). "
        f"The protocol (section 6) treats 50 seeds as adequate when `s < {SEED_SD_THRESHOLD}`.",
        "",
        _md_table(["cell", "arm", "pairs", "mean diff", "s", "d_z", "p (Holm)", "half-width, 50 seeds"],
                  [[c["cell_id"], c["arm"], c.get("n_pairs"), c.get("mean_diff"), c.get("sd_diff"), c.get("d_z"),
                    c.get("p_holm"), c.get("projected_half_width_50")] for c in analysis["contrasts"]]),
        "",
        _md_table(["cell", "arm", "bootstrap 95% CI", "paired t 95% CI", "section 4 rule"],
                  [[c["cell_id"], c["arm"], f"[{_fmt(c.get('boot_ci_low'))}, {_fmt(c.get('boot_ci_high'))}]",
                    f"[{_fmt(c.get('t_ci_low'))}, {_fmt(c.get('t_ci_high'))}]", c.get("verdict_rule", "n/a")]
                   for c in analysis["contrasts"]]),
        "",
    ]
    if exploratory:
        lines += ["The `rule` column applies the protocol's section 4 decision rule mechanically. In an exploratory "
                  "run it is a planning diagnostic only and is not a test of any hypothesis.", ""]
    lines += ["## Degenerate-case flags", ""] + ([f"- {f}" for f in flags] if flags else ["None detected by the automatic checks."]) + [""]
    lines += ["## Figures", ""] + ([] if figs else ["No figure: the matrix has no arm other than the baseline.", ""])
    for k, f in enumerate(figs, 1):
        lines += [f"![{f['alt']}](figures/{f['file']})", "", f"*Figure {k}.* {f['caption']}", ""]
    lines += ["## Tables", "", "`summary.csv` (per cell and arm) and `contrasts.csv` (paired contrasts) are written next to this report.", ""]
    md_path = out_dir / "report.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    (out_dir / "analysis.json").write_text(json.dumps({"result_sha256": result_sha, "generator": generator, "runtime": rt, "flags": flags, **analysis},
                                                      indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    outputs = {"markdown": md_path, "summary": out_dir / "summary.csv", "contrasts": out_dir / "contrasts.csv"}
    if pdf:
        outputs["pdf"] = build_pdf(md_path)
    return outputs


def build_pdf(md_path: Path) -> Path:
    """Markdown -> Typst (pandoc, Libertinus Serif) -> PDF (typst Python package). Decision D-002."""
    pandoc = os.environ.get("MEMORY_PANDOC", DEFAULT_PANDOC)
    py = os.environ.get("MEMORY_TYPST_PYTHON", DEFAULT_TYPST_PYTHON)
    if not (shutil.which(pandoc) or Path(pandoc).is_file()) or not Path(py).is_file():
        raise FileNotFoundError("pandoc or the Typst Python interpreter is not available; set MEMORY_PANDOC / MEMORY_TYPST_PYTHON")
    md_path = md_path.resolve()
    typ = md_path.with_suffix(".typ")
    pdf = md_path.with_suffix(".pdf")
    subprocess.run([pandoc, md_path.name, "-s", "-f", "markdown-implicit_figures-citations", "-V", "mainfont=Libertinus Serif",
                    "-V", "papersize=a4", "-o", typ.name], cwd=md_path.parent, check=True)
    subprocess.run([py, "-I", "-c", "import sys, typst; typst.compile(sys.argv[1], output=sys.argv[2], root=sys.argv[3])",
                    str(typ), str(pdf), str(md_path.parent)], check=True)
    return pdf
