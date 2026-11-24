# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Experiment runner: expands a matrix configuration into cells, runs every
(cell, seed, arm) with common random numbers per (cell, seed), validates each
run, and serializes results and a run manifest (both schema-validated)."""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import SimConfig, canonical_json, config_hash
from .environment import environment, peak_rss_bytes, repo_root
from .guard import freeze_status, require_frozen
from .items import draw_common_random_numbers
from .metrics import compute_metrics, validate_trace
from .schema import (
    MANIFEST_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    validate_manifest,
    validate_matrix_config,
    validate_result,
)
from .simulate import simulate

EXPLORATORY_LABEL = "EXPLORATORY: not a confirmatory result; protocol not frozen; never to be presented as a finding."


def load_matrix_config(path: Path) -> dict[str, Any]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_matrix_config(doc)
    return doc


def seed_list(spec: Any) -> list[int]:
    if isinstance(spec, dict):
        return list(range(spec["start"], spec["start"] + spec["count"]))
    return list(spec)


def cell_seeds(matrix: dict[str, Any], cell: dict[str, Any]) -> list[int]:
    """Seeds of one cell. With ``seeds.block_by`` each level of the named factor
    gets its own disjoint block, so cells at different levels share no run."""
    spec = matrix["seeds"]
    if not (isinstance(spec, dict) and "block_by" in spec):
        return seed_list(spec)
    factor, step = spec["block_by"]["factor"], spec["block_by"]["step"]
    levels = matrix.get("factors", {}).get(factor)
    if levels is None:
        raise ValueError(f"seeds.block_by names {factor!r}, which is not a factor of the matrix")
    if step < spec["count"]:
        raise ValueError("seeds.block_by.step must be at least seeds.count so that blocks are disjoint")
    start = spec["start"] + step * levels.index(cell["factors"][factor])
    return list(range(start, start + spec["count"]))


def expand_cells(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    factors = matrix.get("factors", {})
    names = sorted(factors)
    cells = []
    for k, combo in enumerate(itertools.product(*(factors[n] for n in names))):
        overrides = dict(zip(names, combo))
        cfg = SimConfig.from_dict({**matrix["base"], **overrides})
        cells.append({"cell_id": f"C{k:03d}", "factors": overrides, "config": cfg.to_dict(), "config_hash": config_hash(cfg)})
    return cells


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def run_one(cfg: SimConfig, arm: str, crn, run_id: str, cell_id: str) -> dict[str, Any]:
    start_utc = _utc_now()
    t0 = time.perf_counter()
    status, reasons, metrics = "ok", [], None
    try:
        trace = simulate(cfg, arm, crn)
        reasons = validate_trace(cfg, trace)
        if reasons:
            status = "excluded"
        else:
            metrics = compute_metrics(cfg, trace, crn)
    except Exception as exc:  # recorded, never silently dropped
        status, reasons = "failed", [f"{type(exc).__name__}: {exc}"]
    runtime = time.perf_counter() - t0
    end_utc = _utc_now()
    return {"run_id": run_id, "cell_id": cell_id, "arm": arm, "seed": crn.seed, "status": status,
            "reasons": reasons, "metrics": metrics, "runtime_s": runtime, "peak_rss_bytes": peak_rss_bytes(),
            "start_utc": start_utc, "end_utc": end_utc}


def run_matrix(matrix: dict[str, Any], root: Path | None = None, allow_confirmatory: bool = False) -> dict[str, Any]:
    """Run the whole matrix. Confirmatory matrices require a frozen protocol."""
    validate_matrix_config(matrix)
    root = root or repo_root()
    exp_id = matrix["experiment_id"]
    if matrix["kind"] == "confirmatory":
        if not allow_confirmatory:
            raise PermissionError("confirmatory matrices are run only through the guarded CLI path")
        fs = require_frozen(root, exp_id, matrix.get("protocol_path"), matrix)
    else:
        fs = freeze_status(root, exp_id, matrix.get("protocol_path"))
    cells = expand_cells(matrix)
    for cell in cells:
        cell["seeds"] = cell_seeds(matrix, cell)
    runs = []
    wall0 = time.perf_counter()
    for cell in cells:
        cfg = SimConfig.from_dict(cell["config"])
        for seed in cell["seeds"]:
            crn = draw_common_random_numbers(cfg, seed)
            for arm in matrix["arms"]:
                run_id = f"{exp_id}/{cell['cell_id']}/{arm}/s{seed}"
                runs.append(run_one(cfg, arm, crn, run_id, cell["cell_id"]))
    wall = time.perf_counter() - wall0
    doc = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "experiment_id": exp_id,
        "kind": matrix["kind"],
        "label": EXPLORATORY_LABEL if matrix["kind"] == "exploratory" else "CONFIRMATORY run against a frozen protocol.",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "matrix_config": matrix,
        "matrix_config_hash": config_hash(matrix),
        "protocol": {"path": matrix.get("protocol_path"), "sha256": fs.sha256, "frozen": fs.frozen},
        "environment": environment(root),
        "cells": cells,
        "runs": runs,
        "summary": {
            "n_runs": len(runs),
            "n_ok": sum(r["status"] == "ok" for r in runs),
            "n_excluded": sum(r["status"] == "excluded" for r in runs),
            "n_failed": sum(r["status"] == "failed" for r in runs),
            "wall_clock_s": wall,
        },
    }
    validate_result(doc)
    return doc


def write_outputs(doc: dict[str, Any], out_dir: Path, root: Path | None = None) -> tuple[Path, Path]:
    """Write results.json and run_manifest.json (both validated) into out_dir."""
    validate_result(doc)
    root = root or repo_root()
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "results.json"
    text = json.dumps(doc, indent=1, sort_keys=True) + "\n"
    result_path.write_text(text, encoding="utf-8")
    try:
        rel = str(result_path.resolve().relative_to(root.resolve()))
    except ValueError:
        rel = str(result_path)
    cfg_hash = {c["cell_id"]: c["config_hash"] for c in doc["cells"]}
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "experiment_id": doc["experiment_id"],
        "kind": doc["kind"],
        "matrix_config_hash": doc["matrix_config_hash"],
        "result_path": rel,
        "result_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "environment": doc["environment"],
        "runs": [
            {"run_id": r["run_id"], "seed": r["seed"], "arm": r["arm"], "config_hash": cfg_hash[r["cell_id"]],
             "status": r["status"], "runtime_s": r["runtime_s"], "peak_rss_bytes": r["peak_rss_bytes"],
             **{k: r[k] for k in ("start_utc", "end_utc") if k in r}}
            for r in doc["runs"]
        ],
        "wall_clock_s": doc["summary"]["wall_clock_s"],
        "peak_rss_bytes": peak_rss_bytes(),
    }
    validate_manifest(manifest)
    manifest_path = out_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return result_path, manifest_path


def load_result(path: Path) -> dict[str, Any]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_result(doc)
    return doc


__all__ = ["run_matrix", "write_outputs", "load_result", "load_matrix_config", "expand_cells", "seed_list", "cell_seeds", "canonical_json"]
