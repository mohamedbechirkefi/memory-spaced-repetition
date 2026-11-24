# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Integration: config -> runner -> validated result and manifest -> report;
schema fail-closed behaviour; freeze guard and CLI refusal."""

import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest

from memory_research.cli import EXIT_REFUSED, main
from memory_research.environment import repo_root
from memory_research.guard import ProtocolNotFrozenError, freeze_status, require_frozen
from memory_research.report import build_report
from memory_research.runner import expand_cells, load_matrix_config, load_result, run_matrix, write_outputs
from memory_research.schema import SchemaError, validate_matrix_config, validate_result

ROOT = repo_root()


def small_matrix(**over):
    m = {
        "config_schema": "memory-matrix-config/1.0.0", "experiment_id": "SMOKE-900", "kind": "exploratory",
        "description": "test matrix", "base": {"n_items": 6, "window_days": 8, "reviews_per_item": 2},
        "arms": ["uniform", "expanding", "massed", "leitner", "greedy"], "baseline": "uniform", "seeds": [1, 2, 3],
    }
    m.update(over)
    return m


@pytest.fixture(scope="module")
def small_doc():
    return run_matrix(small_matrix(), ROOT)


def test_runner_produces_valid_complete_result(small_doc):
    validate_result(small_doc)
    assert small_doc["summary"]["n_runs"] == 15 and small_doc["summary"]["n_ok"] == 15
    assert small_doc["kind"] == "exploratory" and "EXPLORATORY" in small_doc["label"]
    assert small_doc["protocol"]["frozen"] is False


def test_runner_is_deterministic_apart_from_timing(small_doc):
    again = run_matrix(small_matrix(), ROOT)
    strip = lambda d: [(r["run_id"], r["status"], r["metrics"]) for r in d["runs"]]
    assert strip(again) == strip(small_doc)


@pytest.mark.parametrize("mutate", [
    lambda d: d["runs"][0]["metrics"].__setitem__("recall_mean", 1.2),
    lambda d: d["summary"].__setitem__("n_ok", 3),
    lambda d: d.pop("environment"),
    lambda d: d.__setitem__("schema_version", "memory-result/0.9"),
    lambda d: d["runs"][1].__setitem__("run_id", d["runs"][0]["run_id"]),
    lambda d: d["runs"][0].__setitem__("cell_id", "C999"),
    lambda d: d["runs"][0].update(status="failed"),  # failed run without a reason
])
def test_schema_fails_closed(small_doc, mutate):
    bad = copy.deepcopy(small_doc)
    mutate(bad)
    with pytest.raises(SchemaError):
        validate_result(bad)


def test_write_outputs_and_manifest(tmp_path, small_doc):
    res, man = write_outputs(small_doc, tmp_path / "exploratory" / "x", ROOT)
    manifest = json.loads(man.read_text())
    assert manifest["result_sha256"] == hashlib.sha256(res.read_bytes()).hexdigest()
    assert len(manifest["runs"]) == 15
    for r in manifest["runs"]:
        assert len(r["config_hash"]) == 64 and r["runtime_s"] >= 0
    assert manifest["environment"]["cpu"]
    assert load_result(res)["experiment_id"] == "SMOKE-900"


def test_report_built_from_results_only(tmp_path, small_doc):
    res, _ = write_outputs(small_doc, tmp_path / "exploratory", ROOT)
    out = build_report(res, tmp_path / "exploratory" / "report")
    text = out["markdown"].read_text()
    assert "EXPLORATORY" in text and "SHA-256" in text
    with out["summary"].open() as fh:
        rows = {r["arm"]: r for r in csv.DictReader(fh)}
    vals = [r["metrics"]["recall_mean"] for r in small_doc["runs"] if r["arm"] == "greedy"]
    assert float(rows["greedy"]["mean"]) == pytest.approx(sum(vals) / len(vals), abs=1e-12)
    assert (tmp_path / "exploratory" / "report" / "figures" / "paired_diff_C000.svg").is_file()


def test_report_refuses_malformed_results(tmp_path, small_doc):
    bad = copy.deepcopy(small_doc)
    bad["runs"][0]["metrics"]["recall_mean"] = -0.1
    p = tmp_path / "results.json"
    p.write_text(json.dumps(bad))
    with pytest.raises(SchemaError):
        build_report(p, tmp_path / "r")
    assert main(["report", "--results", str(p), "--out", str(tmp_path / "r")]) == 2


def test_failed_and_excluded_runs_are_kept(monkeypatch):
    import memory_research.runner as runner

    def boom(*a, **k):
        raise FloatingPointError("injected")

    monkeypatch.setattr(runner, "simulate", boom)
    doc = run_matrix(small_matrix(seeds=[1]), ROOT)
    assert doc["summary"]["n_failed"] == 5 and all(r["reasons"] for r in doc["runs"])
    monkeypatch.undo()
    monkeypatch.setattr(runner, "validate_trace", lambda c, t: ["budget: injected"])
    doc = run_matrix(small_matrix(seeds=[1]), ROOT)
    assert doc["summary"]["n_excluded"] == 5


def test_draft_confirmatory_configs_validate_and_expand():
    sizes = {}
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        m = load_matrix_config(ROOT / "research" / "experiments" / exp / "config.json")
        assert m["kind"] == "confirmatory" and m["seeds"] == {"start": 1000, "count": 50}
        sizes[exp] = len(expand_cells(m)) * len(m["arms"]) * 50
    assert sizes == {"EXP-001": 250, "EXP-002": 300, "EXP-003": 13500}  # protocol section 9


@pytest.mark.parametrize("exp", ["EXP-001", "EXP-002", "EXP-003"])
def test_confirmatory_run_refused_while_unfrozen(exp, tmp_path):
    cfg = ROOT / "research" / "experiments" / exp / "config.json"
    m = load_matrix_config(cfg)
    with pytest.raises(ProtocolNotFrozenError):
        run_matrix(m, ROOT, allow_confirmatory=True)
    with pytest.raises(PermissionError):
        run_matrix(m, ROOT)
    assert main(["run", "--config", str(cfg), "--out", str(tmp_path / "confirmatory")]) == EXIT_REFUSED
    assert not (tmp_path / "confirmatory" / "results.json").exists()


def test_guard_accepts_a_properly_frozen_protocol(tmp_path):
    # A synthetic repository, not this one: shows what the owner's freeze must record.
    (tmp_path / "research" / "experiments" / "EXP-001").mkdir(parents=True)
    proto = tmp_path / "research" / "experiments" / "EXP-001" / "protocol.md"
    proto.write_text("frozen protocol v1.0\n")
    (tmp_path / "research" / "protocol.md").write_text("Status: FROZEN v1.0\n")
    sha = hashlib.sha256(proto.read_bytes()).hexdigest()
    reg = tmp_path / "research" / "experiment_registry.csv"
    reg.write_text(f"exp_id,protocol_hash\nEXP-001,{sha}\n")
    assert require_frozen(tmp_path, "EXP-001", "research/experiments/EXP-001/protocol.md").frozen
    proto.write_text("edited after the freeze\n")
    st = freeze_status(tmp_path, "EXP-001", "research/experiments/EXP-001/protocol.md")
    assert not st.frozen and any("does not match" in r for r in st.reasons)


def test_exploratory_output_must_be_labelled(tmp_path):
    cfg = tmp_path / "m.json"
    cfg.write_text(json.dumps(small_matrix()))
    with pytest.raises(SystemExit):
        main(["run", "--config", str(cfg), "--out", str(tmp_path / "plain")])
    assert main(["run", "--config", str(cfg), "--out", str(tmp_path / "exploratory")]) == 0


def test_matrix_config_rejects_unknown_fields():
    with pytest.raises(SchemaError):
        validate_matrix_config(small_matrix(budget=3))
    with pytest.raises(SchemaError):
        validate_matrix_config(small_matrix(arms=["uniform", "random"]))
