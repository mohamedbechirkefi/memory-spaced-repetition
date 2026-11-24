# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Apply the frozen analysis to a result file and write tables, figures and a
SHA-256 manifest. Committed before any confirmatory output existed (M3).

  .venv/bin/python scripts/analyse_confirmatory.py --exp EXP-001 \
      --results results/confirmatory/EXP-001/results.json [--exp001 PATH] [--out DIR]

`--exp` selects the frozen analysis (EXP-001, EXP-002 or EXP-003); the result
file may be exploratory (rehearsal) or confirmatory, and the output says which.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from memory_research.environment import environment
from memory_research.frozen_analysis import analyse_exp001, analyse_exp002, analyse_exp003
from memory_research.report import DELTA
from memory_research.runner import load_result


def _csv(rows: list[dict], path: Path) -> None:
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else (json.dumps(r[k]) if isinstance(r.get(k), (list, dict)) else r[k])) for k in keys})


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"svg.hashsalt": "memory", "font.size": 9})
    return plt


def _forest(rows: list[dict], title: str, path: Path, tag: str) -> None:
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.6, 0.45 * len(rows) + 1.5))
    for i, r in enumerate(rows):
        ax.errorbar([r["mean_diff"]], [i], xerr=[[r["mean_diff"] - r["boot_ci_low"]], [r["boot_ci_high"] - r["mean_diff"]]],
                    fmt="o", color="black", capsize=3)
    ax.axvline(0, color="0.4", lw=0.8)
    ax.axvspan(-DELTA, DELTA, color="0.85", zorder=0, label="equivalence band +/-0.02")
    ax.set_yticks(range(len(rows)), [f"{r['arm']} - {r['baseline']}" for r in rows])
    ax.invert_yaxis()
    ax.set_xlabel("mean paired difference in R (probability units)\n95% percentile bootstrap interval over seeds")
    ax.set_title(f"{title} ({tag})", fontsize=9)
    ax.legend(fontsize=7, loc="best")
    fig.tight_layout()
    fig.savefig(path.with_suffix(".svg"))
    fig.savefig(path.with_suffix(".png"), dpi=150)
    plt.close(fig)


def _arm_means(rows: list[dict], title: str, path: Path, tag: str) -> None:
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.6, 0.45 * len(rows) + 1.5))
    for i, r in enumerate(rows):
        m = r["recall_mean_mean"]
        ax.errorbar([m], [i], xerr=[[m - r["recall_mean_boot_ci_low"]], [r["recall_mean_boot_ci_high"] - m]],
                    fmt="s", color="tab:blue", capsize=3)
    ax.set_yticks(range(len(rows)), [r["arm"] for r in rows])
    ax.invert_yaxis()
    ax.set_xlabel("mean delayed modelled recall R\n95% percentile bootstrap interval over seeds")
    ax.set_title(f"{title} ({tag})", fontsize=9)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".svg"))
    fig.savefig(path.with_suffix(".png"), dpi=150)
    plt.close(fig)


def _exp003_figures(res: dict, fig_dir: Path, tag: str) -> list[str]:
    plt = _plt()
    cells = res["cells"]
    arms = [k[5:] for k in cells[0] if k.startswith("diff_")]
    models = sorted({c["true_model"] for c in cells})
    dists = ["homogeneous", "lognormal", "bimodal"]
    ris = sorted({c["retention_interval_days"] for c in cells})
    ks = sorted({c["reviews_per_item"] for c in cells})
    out = []
    for arm in arms:
        fig, axes = plt.subplots(len(models), len(dists), figsize=(9.0, 5.2), sharey=True)
        for i, mo in enumerate(models):
            for j, di in enumerate(dists):
                ax = axes[i][j]
                for n, k in enumerate(ks):
                    pts = sorted((c for c in cells if c["true_model"] == mo and c["item_distribution"] == di
                                  and c["reviews_per_item"] == k), key=lambda c: c["retention_interval_days"])
                    x = np.arange(len(pts)) + (n - 1) * 0.15
                    y = np.array([c[f"diff_{arm}"] for c in pts])
                    lo = np.array([c[f"ci_{arm}"][0] for c in pts])
                    hi = np.array([c[f"ci_{arm}"][1] for c in pts])
                    ax.errorbar(x, y, yerr=[y - lo, hi - y], fmt="o-", ms=3, lw=0.8, capsize=2, label=f"k = {k}")
                ax.axhline(0, color="0.4", lw=0.8)
                ax.set_xticks(range(len(ris)), [str(r) for r in ris])
                ax.set_title(f"{mo}, {di}", fontsize=8)
                if i == len(models) - 1:
                    ax.set_xlabel("retention interval RI (days)")
                if j == 0:
                    ax.set_ylabel(f"R({arm}) - R(uniform)")
        axes[0][0].legend(fontsize=7)
        fig.suptitle(f"EXP-003: {arm} minus uniform per cell, 95% bootstrap intervals, unadjusted ({tag})", fontsize=9)
        fig.tight_layout()
        name = f"exp003_diff_{arm}"
        fig.savefig(fig_dir / f"{name}.svg")
        fig.savefig(fig_dir / f"{name}.png", dpi=150)
        plt.close(fig)
        out.append(name)
    all_arms = list(cells[0]["means"])
    mat = np.array([[c["first_rank_share"][a] for a in all_arms] for c in cells])
    fig, ax = plt.subplots(figsize=(5.5, 0.16 * len(cells) + 1.5))
    im = ax.imshow(mat, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(all_arms)), all_arms, rotation=30)
    ax.set_yticks(range(len(cells)), [f"{c['cell_id']} {c['true_model'][:3]} k{c['reviews_per_item']} RI{c['retention_interval_days']} {c['item_distribution'][:4]}" for c in cells], fontsize=4.5)
    fig.colorbar(im, ax=ax, label="share of seeds ranking first (ties shared)")
    ax.set_title(f"EXP-003: first-rank share per cell ({tag})", fontsize=9)
    fig.tight_layout()
    fig.savefig(fig_dir / "exp003_first_rank_share.svg")
    fig.savefig(fig_dir / "exp003_first_rank_share.png", dpi=150)
    plt.close(fig)
    out.append("exp003_first_rank_share")
    return out


def write_sha_manifest(root: Path) -> Path:
    lines = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS":
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root)}")
    out = root / "SHA256SUMS"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True, choices=["EXP-001", "EXP-002", "EXP-003"])
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--exp001", type=Path, help="frozen_analysis.json of EXP-001 (needed by EXP-002 and EXP-003)")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    doc = load_result(a.results)
    out = a.out or a.results.parent / "analysis"
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    tag = "EXPLORATORY" if doc["kind"] == "exploratory" else "CONFIRMATORY"
    e1 = json.loads(a.exp001.read_text(encoding="utf-8")) if a.exp001 else None
    if a.exp == "EXP-001":
        res = analyse_exp001(doc)
        _csv(res["secondary_contrasts_holm4"], out / "contrasts.csv")
        _csv(res["sensitivity_metric_choice"], out / "sensitivity_metric_choice.csv")
        _csv(res["arm_summary"], out / "arm_summary.csv")
        _forest(res["secondary_contrasts_holm4"], "EXP-001: arms minus uniform", fig_dir / "exp001_contrasts", tag)
        _arm_means(res["arm_summary"], "EXP-001: mean R per arm", fig_dir / "exp001_arm_means", tag)
    elif a.exp == "EXP-002":
        res = analyse_exp002(doc, e1)
        _csv(res["primary_contrasts_holm2"], out / "primary_contrasts.csv")
        _csv(res["secondary_contrasts_holm_all"], out / "contrasts.csv")
        _csv(res["arm_summary"], out / "arm_summary.csv")
        _forest(res["secondary_contrasts_holm_all"], "EXP-002: arms minus uniform (power-law learners)", fig_dir / "exp002_contrasts", tag)
        _arm_means(res["arm_summary"], "EXP-002: mean R per arm", fig_dir / "exp002_arm_means", tag)
    else:
        res = analyse_exp003(doc, e1)
        flat = [{k: v for k, v in c.items() if k not in ("means", "first_rank_share")}
                | {f"mean_{a}": m for a, m in c["means"].items()}
                | {f"first_share_{a}": s for a, s in c["first_rank_share"].items()} for c in res["cells"]]
        _csv(flat, out / "cells.csv")
        _exp003_figures(res, fig_dir, tag)
    res["result_file"] = str(a.results)
    res["result_sha256"] = hashlib.sha256(a.results.read_bytes()).hexdigest()
    env = environment()
    res["analysis_generator"] = {"script": "scripts/analyse_confirmatory.py", "module": "memory_research.frozen_analysis",
                                 "git_revision": env["git_revision"], "git_dirty": env["git_dirty"]}
    (out / "frozen_analysis.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n", encoding="utf-8")
    sums = write_sha_manifest(a.results.parent)
    print(f"{a.exp} [{doc['kind']}]: analysis written to {out}; manifest {sums}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
