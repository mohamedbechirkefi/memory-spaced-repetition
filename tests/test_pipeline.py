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
from memory_research.runner import cell_seeds, expand_cells, load_matrix_config, load_result, run_matrix, write_outputs
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


def test_frozen_confirmatory_configs_validate_and_expand():
    sizes, seeds = {}, {}
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        m = load_matrix_config(ROOT / "research" / "experiments" / exp / "config.json")
        assert m["kind"] == "confirmatory" and m["seeds"]["count"] == 50  # amendment A3: 50 seeds
        cells = expand_cells(m)
        sizes[exp] = sum(len(cell_seeds(m, c)) for c in cells) * len(m["arms"])
        seeds[exp] = {c["cell_id"]: cell_seeds(m, c) for c in cells}
    assert sizes == {"EXP-001": 250, "EXP-002": 300, "EXP-003": 18000}  # protocol section 9, round 3 (16.3 B2)
    assert seeds["EXP-001"]["C000"] == list(range(1000, 1050)) == seeds["EXP-002"]["C000"]


def test_round3_central_retention_interval():
    # Protocol 16.3 B1: RI* = 281 days in EXP-001 and EXP-002; fitted values unchanged.
    for exp in ("EXP-001", "EXP-002"):
        b = load_matrix_config(ROOT / "research" / "experiments" / exp / "config.json")["base"]
        assert b["retention_interval_days"] == 281 and b["h0_days"] == 54.0 and b["lognormal_sigma"] == 0.759


def test_guard_refuses_superseded_v1_0_configs():
    # The v1.0 configurations (RI = 7 in EXP-001/EXP-002; RI levels 1, 7, 30 in EXP-003) are refused.
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        m = load_matrix_config(ROOT / "research" / "experiments" / exp / "config.json")
        old = copy.deepcopy(m)
        old["base"]["retention_interval_days"] = 7
        if "factors" in old:
            old["factors"]["retention_interval_days"] = [1, 7, 30]
        old["status_note"] = "FROZEN v1.0"
        st = freeze_status(ROOT, exp, m["protocol_path"], old)
        assert not st.frozen and any("differs from the frozen configuration" in r for r in st.reasons)


def test_exp003_retention_cells_use_disjoint_runs():
    # Amendment A5: EXP-003 cells at different retention intervals never share a seed (run).
    m = load_matrix_config(ROOT / "research" / "experiments" / "EXP-003" / "config.json")
    by_ri: dict = {}
    for c in expand_cells(m):
        by_ri.setdefault(c["factors"]["retention_interval_days"], set()).update(cell_seeds(m, c))
    assert sorted(by_ri) == [1, 7, 30, 281]  # round 3 (protocol 16.3 B2): RI* = 281 added
    assert sorted(by_ri[281]) == list(range(3300, 3350)) and sorted(by_ri[7]) == list(range(3100, 3150))
    blocks = list(by_ri.values())
    assert all(len(b) == 50 for b in blocks)
    assert all(not (a & b) for i, a in enumerate(blocks) for b in blocks[i + 1:])
    assert all(not (b & set(range(1000, 1050))) for b in blocks)  # nor with EXP-001/EXP-002 runs
    assert all(min(b) >= 1000 for b in blocks)  # disjoint from exploratory seeds 1 to 30


def test_seed_blocks_reject_overlap():
    m = small_matrix(factors={"retention_interval_days": [1, 7]}, seeds={"start": 10, "count": 5, "block_by": {"factor": "retention_interval_days", "step": 3}})
    validate_matrix_config(m)
    with pytest.raises(ValueError):
        cell_seeds(m, expand_cells(m)[0])


def test_unfrozen_protocol_refused(tmp_path):
    # A synthetic repository copy in the draft state: nothing is run.
    (tmp_path / "research" / "experiments" / "EXP-001").mkdir(parents=True)
    (tmp_path / "research" / "protocol.md").write_text("Status: DRAFT. NOT FROZEN.\n")
    (tmp_path / "research" / "experiments" / "EXP-001" / "protocol.md").write_text("draft\n")
    (tmp_path / "research" / "experiment_registry.csv").write_text("exp_id,protocol_hash\nEXP-001,none (not frozen)\n")
    m = load_matrix_config(ROOT / "research" / "experiments" / "EXP-001" / "config.json")
    with pytest.raises(ProtocolNotFrozenError):
        run_matrix(m, tmp_path, allow_confirmatory=True)


@pytest.mark.parametrize("exp", ["EXP-001", "EXP-002", "EXP-003"])
def test_guard_accepts_frozen_configs(exp):
    # Checks the guard only. Never call run_matrix with allow_confirmatory=True on a frozen
    # configuration in a test: that would be an unscheduled confirmatory run.
    m = load_matrix_config(ROOT / "research" / "experiments" / exp / "config.json")
    st = freeze_status(ROOT, exp, m["protocol_path"], m)
    assert st.frozen, st.reasons
    with pytest.raises(PermissionError):  # the library path still refuses without the CLI flag
        run_matrix(m, ROOT)


@pytest.mark.parametrize("exp", ["EXP-001", "EXP-002", "EXP-003"])
def test_guard_refuses_changed_configs(exp, tmp_path):
    m = load_matrix_config(ROOT / "research" / "experiments" / exp / "config.json")
    changed = copy.deepcopy(m)
    changed["base"]["h0_days"] = changed["base"]["h0_days"] * 2
    st = freeze_status(ROOT, exp, m["protocol_path"], changed)
    assert not st.frozen and any("differs from the frozen configuration" in r for r in st.reasons)
    with pytest.raises(ProtocolNotFrozenError):
        run_matrix(changed, ROOT, allow_confirmatory=True)
    cfg = tmp_path / "changed.json"
    cfg.write_text(json.dumps(changed))
    assert main(["run", "--config", str(cfg), "--out", str(tmp_path / "confirmatory")]) == EXIT_REFUSED
    assert not (tmp_path / "confirmatory" / "results.json").exists()
    more_seeds = copy.deepcopy(m)
    more_seeds["seeds"]["count"] = 51
    assert not freeze_status(ROOT, exp, m["protocol_path"], more_seeds).frozen


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
