# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Frozen analysis (M3): decision rules, Holm families, rank shares, E1/E2,
and run-time provenance fields."""

import copy

import numpy as np
import pytest

from memory_research.environment import repo_root
from memory_research.frozen_analysis import _rank_first_share, analyse_exp001, analyse_exp002, analyse_exp003, contrast
from memory_research.runner import run_matrix, write_outputs
from memory_research.schema import validate_manifest

ROOT = repo_root()


def _matrix(arms, base=None, factors=None, seeds=None, eid="SMOKE-910"):
    m = {"config_schema": "memory-matrix-config/1.0.0", "experiment_id": eid, "kind": "exploratory",
         "description": "test", "base": {"n_items": 6, "window_days": 8, "reviews_per_item": 2, **(base or {})},
         "arms": arms, "baseline": "uniform", "seeds": seeds or {"start": 1, "count": 6}}
    if factors:
        m["factors"] = factors
    return m


@pytest.fixture(scope="module")
def doc1():
    return run_matrix(_matrix(["uniform", "expanding", "massed", "leitner", "greedy"]), ROOT)


def _set_diff(doc, arm, diffs, metric="recall_mean"):
    """Overwrite metric values so that arm - uniform equals the given per-seed differences."""
    d = copy.deepcopy(doc)
    base = {r["seed"]: r["metrics"][metric] for r in d["runs"] if r["arm"] == "uniform"}
    seeds = sorted(base)
    for r in d["runs"]:
        if r["arm"] == arm:
            r["metrics"][metric] = base[r["seed"]] + diffs[seeds.index(r["seed"])]
    return d


def test_runs_carry_start_end_and_data_manifest(doc1, tmp_path):
    r = doc1["runs"][0]
    assert r["start_utc"].endswith("Z") and r["end_utc"] >= r["start_utc"]
    assert doc1["environment"]["data_manifest_sha256"] is None or len(doc1["environment"]["data_manifest_sha256"]) == 64
    _, man = write_outputs(doc1, tmp_path / "exploratory" / "x", ROOT)
    import json
    m = json.loads(man.read_text())
    validate_manifest(m)
    assert "start_utc" in m["runs"][0] and "end_utc" in m["runs"][0]


def test_contrast_matches_hand_values(doc1):
    d = _set_diff(doc1, "greedy", [0.01, 0.02, 0.03, 0.01, 0.02, 0.03])
    c = contrast(d, d["cells"][0]["cell_id"], "greedy", "uniform")
    assert c["n_pairs"] == 6 and c["mean_diff"] == pytest.approx(0.02, abs=1e-12)
    assert c["verdict_rule"] == "above zero"


@pytest.mark.parametrize("diffs,rule", [
    ([0.01, 0.02, 0.03, 0.01, 0.02, 0.03], "above zero"),
    ([-0.01, -0.02, -0.03, -0.01, -0.02, -0.03], "below zero"),
    ([0.001, -0.001, 0.002, -0.002, 0.0, 0.001], "equivalent within delta"),
    ([0.2, -0.2, 0.1, -0.1, 0.15, -0.15], "inconclusive"),
])
def test_exp001_primary_rule(doc1, diffs, rule):
    res = analyse_exp001(_set_diff(doc1, "greedy", diffs))
    assert res["primary"]["verdict_rule"] == rule
    assert len(res["secondary_contrasts_holm4"]) == 4
    ps = [c["p_holm"] for c in res["secondary_contrasts_holm4"]]
    assert all(p is None or 0 <= p <= 1 for p in ps)


def test_exp001_metric_sensitivity_sign(doc1):
    d = _set_diff(doc1, "greedy", [0.01] * 6)
    d = _set_diff(d, "greedy", [-0.01] * 6, metric="recall_min")
    res = analyse_exp001(d)
    rm = next(s for s in res["sensitivity_metric_choice"] if s["metric"] == "recall_min")
    assert rm["same_sign_as_primary"] is False and res["conclusion_restricted_to_mean"] is True


@pytest.fixture(scope="module")
def doc2():
    return run_matrix(_matrix(["uniform", "expanding", "massed", "leitner", "greedy-power", "greedy-exp"],
                              base={"true_model": "power"}, eid="SMOKE-911"), ROOT)


def test_exp002_rule_dependent_when_greedy_exp_below_zero(doc2):
    d = _set_diff(doc2, "greedy-exp", [-0.01, -0.02, -0.03, -0.01, -0.02, -0.03])
    res = analyse_exp002(d, {"primary": {"verdict_rule": "above zero"}})
    assert [p["arm"] for p in res["primary_contrasts_holm2"]] == ["greedy-power", "greedy-exp"]
    assert res["interpretation_rule"]["exp001_advantage_dependent_on_model_knowledge"] is True


def test_exp002_rule_not_applicable_without_positive_exp001(doc2):
    res = analyse_exp002(doc2, {"primary": {"verdict_rule": "below zero"}})
    assert res["interpretation_rule"]["applicable"] is False
    assert res["interpretation_rule"]["exp001_advantage_dependent_on_model_knowledge"] is None


def test_exp002_rule_not_dependent_when_greedy_exp_clearly_positive(doc2):
    d = _set_diff(doc2, "greedy-exp", [0.05, 0.06, 0.07, 0.05, 0.06, 0.07])
    res = analyse_exp002(d, {"primary": {"verdict_rule": "above zero"}})
    assert res["interpretation_rule"]["exp001_advantage_dependent_on_model_knowledge"] is False


def test_rank_first_share_splits_ties(doc1):
    d = copy.deepcopy(doc1)
    for r in d["runs"]:
        r["metrics"]["recall_mean"] = 0.5 if r["arm"] in ("uniform", "greedy") else 0.1
    sh = _rank_first_share(d, d["cells"][0]["cell_id"], d["matrix_config"]["arms"])
    assert sh["uniform"] == pytest.approx(0.5) and sh["greedy"] == pytest.approx(0.5)
    assert sh["_seeds_with_tie"] == 6 and sh["massed"] == 0.0


def test_exp003_structure_and_expectations():
    m = _matrix(["uniform", "expanding", "massed", "leitner", "greedy"],
                factors={"true_model": ["exponential", "power"], "retention_interval_days": [1, 7],
                         "item_distribution": ["homogeneous", "lognormal", "bimodal"]},
                seeds={"start": 1, "count": 4, "block_by": {"factor": "retention_interval_days", "step": 100}},
                eid="SMOKE-912")
    doc = run_matrix(m, ROOT)
    ref = {"primary": {"mean_diff": 0.01}, "arm_summary": [{"arm": a, "recall_mean_mean": v} for a, v in
                                                          zip(m["arms"], [0.5, 0.4, 0.3, 0.6, 0.7])]}
    res = analyse_exp003(doc, ref)
    assert len(res["cells"]) == 12
    assert res["exp001_rank_order"] == ["greedy", "leitner", "uniform", "expanding", "massed"]
    assert res["e1_massed_improves_as_ri_decreases"]["of"] == 6
    assert all(c["reviews_per_item"] == 2 for c in res["cells"])
    assert res["e2_greedy_advantage_smallest_homogeneous"]["of"] == 4
    for c in res["cells"]:
        s = sum(v for k, v in c["first_rank_share"].items() if not k.startswith("_"))
        assert s == pytest.approx(1.0)
        assert np.isfinite(c["diff_greedy"])
