# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Simulation: hand-computed examples, invariants (bounds, budget, event ordering,
time window, monotone decay), determinism, common random numbers, extreme
parameters, and differential tests against the naive reference simulator."""

import dataclasses
import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from conftest import configs, make_crn
from memory_research.config import SimConfig
from memory_research.items import draw_common_random_numbers
from memory_research.metrics import compute_metrics, validate_trace
from memory_research.reference import ref_simulate
from memory_research.schedules import ARMS
from memory_research.simulate import recall_at, simulate

FIVE = ("uniform", "expanding", "massed", "leitner", "greedy")


def _arms_for(c: SimConfig):
    return ARMS  # greedy-exp and greedy-power are valid under either true model


# ---- hand-computed single-item examples
def _one_item(model="exponential"):
    return SimConfig(n_items=1, window_days=2, retention_interval_days=1, reviews_per_item=1, h0_days=1.0,
                     alpha=0.4, beta=0.6, omega_per_day=1.0, true_model=model, item_distribution="homogeneous")


@pytest.mark.parametrize("model", ["exponential", "power"])
@pytest.mark.parametrize("u, success, expected", [
    (0.3, True, 2 ** -0.6),   # review at day 1: m = 0.5 (half-life 1 day); success -> rate x 0.6; test 1 day later
    (0.7, False, 2 ** -1.6),  # failure -> rate x 1.6
])
def test_single_item_hand_example(model, u, success, expected):
    c = _one_item(model)
    tr = simulate(c, "uniform", make_crn(c, [1.0], [[u]], [0.0]))
    assert tr.event_session.tolist() == [1]
    assert tr.event_recall_prob[0] == pytest.approx(0.5, abs=1e-15)
    assert bool(tr.event_success[0]) is success
    # exponential: 2^(-0.6) after 1 day; power (omega = 1, rate 1): (1+1)^(-0.6) = 2^(-0.6); same for failure
    assert tr.test_recall_prob[0] == pytest.approx(expected, abs=1e-15)


def test_hand_example_two_reviews_exponential():
    # D = 5 (sessions 1..4), k = 2, N = 1: uniform g = 2, phi = 2 -> sessions 2, 4
    c = SimConfig(n_items=1, window_days=5, retention_interval_days=3, reviews_per_item=2, h0_days=2.0,
                  alpha=0.5, beta=1.0, item_distribution="homogeneous")
    tr = simulate(c, "uniform", make_crn(c, [2.0], [[0.0, 1.0, 0.0, 0.0]], [0.0]))
    n0 = math.log(2) / 2.0
    # day 2: m = 2^(-1) = 0.5, success (u = 0) -> n = n0 / 2 (half-life 4)
    # day 4: m = 2^(-2/4) = 0.7071, failure (u = 1) -> n = n0 (half-life 2)
    # test at day 4 + 3 = 7: m = 2^(-3/2) = 0.35355
    assert tr.event_session.tolist() == [2, 4]
    np.testing.assert_allclose(tr.event_recall_prob, [0.5, 2 ** -0.5], atol=1e-15)
    assert tr.event_success.tolist() == [True, False]
    assert tr.final_rate[0] == pytest.approx(n0, rel=1e-15)
    assert tr.test_recall_prob[0] == pytest.approx(2 ** -1.5, abs=1e-15)


def test_known_curve_without_reviews_matches_closed_form():
    c = SimConfig(n_items=1, window_days=2, reviews_per_item=1, retention_interval_days=0, item_distribution="homogeneous")
    tr = simulate(c, "uniform", make_crn(c, [1.0], [[1.0]], [0.0]))
    # failure at day 1 then test at day 1: delta 0 -> recall 1
    assert tr.test_recall_prob[0] == 1.0


# ---- invariants over random configurations
@settings(max_examples=60, deadline=None)
@given(c=configs(), seed=st.integers(0, 2**31 - 1))
def test_every_arm_passes_validation(c, seed):
    crn = draw_common_random_numbers(c, seed)
    for arm in _arms_for(c):
        tr = simulate(c, arm, crn)
        assert validate_trace(c, tr) == [], arm
        assert tr.event_session.size == c.budget  # exact budget
        assert np.all(np.diff(tr.event_session) >= 0)  # event ordering
        for s in np.unique(tr.event_session):  # ascending item order within a session
            items = tr.event_item[tr.event_session == s]
            assert np.all(np.diff(items) > 0)
        assert np.all((tr.event_recall_prob >= 0) & (tr.event_recall_prob <= 1))
        assert np.all((tr.test_recall_prob >= 0) & (tr.test_recall_prob <= 1))
        assert np.all(tr.last_review_day <= c.n_review_sessions)
        assert np.all(c.test_time_days - tr.last_review_day >= c.retention_interval_days)


@settings(max_examples=40, deadline=None)
@given(c=configs(), seed=st.integers(0, 2**31 - 1))
def test_recall_decays_monotonically_after_last_review(c, seed):
    crn = draw_common_random_numbers(c, seed)
    for arm in FIVE:
        tr = simulate(c, arm, crn)
        prev = None
        for ri in (0, 1, 2, 5, 10, 30, 100):
            cur = recall_at(c, tr, ri)
            if prev is not None:
                assert np.all(cur <= prev)
            prev = cur


@settings(max_examples=30, deadline=None)
@given(c=configs(), seed=st.integers(0, 2**31 - 1))
def test_determinism_same_seed_same_trace(c, seed):
    for arm in FIVE:
        a = simulate(c, arm, draw_common_random_numbers(c, seed))
        b = simulate(c, arm, draw_common_random_numbers(c, seed))
        for f in dataclasses.fields(a):
            x, y = getattr(a, f.name), getattr(b, f.name)
            if isinstance(x, np.ndarray):
                np.testing.assert_array_equal(x, y)
            else:
                assert x == y


def test_common_random_numbers_shared_and_independent_of_arm(central):
    crn = draw_common_random_numbers(central, 1000)
    again = draw_common_random_numbers(central, 1000)
    np.testing.assert_array_equal(crn.half_lives_days, again.half_lives_days)
    np.testing.assert_array_equal(crn.review_uniforms, again.review_uniforms)
    other = draw_common_random_numbers(central, 1001)
    assert not np.array_equal(crn.half_lives_days, other.half_lives_days)


def test_fixed_schedule_does_not_depend_on_outcomes(central):
    a = simulate(central, "uniform", draw_common_random_numbers(central, 1))
    b = simulate(central, "uniform", draw_common_random_numbers(central, 2))
    np.testing.assert_array_equal(a.event_session, b.event_session)
    np.testing.assert_array_equal(a.event_item, b.event_item)


def test_crn_shapes_checked(central):
    small = SimConfig(n_items=3)
    with pytest.raises(ValueError):
        simulate(central, "uniform", draw_common_random_numbers(small, 1))


@pytest.mark.parametrize("seed", [-1, 1.5, True])
def test_invalid_seed_rejected(central, seed):
    with pytest.raises(ValueError):
        draw_common_random_numbers(central, seed)


# ---- validation catches violations
def _bad(tr, **changes):
    return dataclasses.replace(tr, **changes)


def test_validation_detects_each_violation():
    c = SimConfig(n_items=3, window_days=6, reviews_per_item=2)
    tr = simulate(c, "uniform", draw_common_random_numbers(c, 3))
    assert validate_trace(c, tr) == []
    probs = tr.event_recall_prob.copy()
    probs[0] = 1.5
    assert any("probability" in p for p in validate_trace(c, _bad(tr, event_recall_prob=probs)))
    nan = tr.test_recall_prob.copy()
    nan[0] = np.nan
    assert any("NaN" in p for p in validate_trace(c, _bad(tr, test_recall_prob=nan)))
    short = {f: getattr(tr, f)[:-1] for f in ("event_session", "event_item", "event_recall_prob", "event_success", "event_predicted")}
    assert any("budget" in p for p in validate_trace(c, _bad(tr, **short)))
    sess = tr.event_session.copy()
    sess[-1] = c.window_days  # outside 1..D-1
    assert any("window" in p for p in validate_trace(c, _bad(tr, event_session=sess)))
    rev = tr.event_session[::-1].copy()
    assert any("ordering" in p for p in validate_trace(c, _bad(tr, event_session=rev)))
    dup_s = np.ones_like(tr.event_session)
    dup_i = np.zeros_like(tr.event_item)
    assert any("more than once" in p for p in validate_trace(c, _bad(tr, event_session=dup_s, event_item=dup_i)))


# ---- extreme parameters
@pytest.mark.parametrize("override", [
    dict(n_items=1, window_days=2, reviews_per_item=1),
    dict(window_days=6, reviews_per_item=5),  # every session used
    dict(alpha=0.999, beta=0.0),
    dict(h0_days=1e6),  # ceiling
    dict(h0_days=1e-3),  # floor and underflow
    dict(retention_interval_days=10_000),
    dict(true_model="power", omega_per_day=100.0),
    dict(true_model="power", omega_per_day=1e-3),
    dict(item_distribution="bimodal", bimodal_factor=1000.0),
])
def test_extreme_parameters_stay_valid(override):
    c = SimConfig(n_items=12, **override) if "n_items" not in override else SimConfig(**override)
    crn = draw_common_random_numbers(c, 11)
    for arm in ARMS:
        tr = simulate(c, arm, crn)
        assert validate_trace(c, tr) == [], (arm, override)
        m = compute_metrics(c, tr, crn)
        assert 0.0 <= m["recall_mean"] <= 1.0


def test_ceiling_and_floor_values():
    hi = SimConfig(n_items=5, h0_days=1e9)
    lo = SimConfig(n_items=5, h0_days=1e-4)
    for c, expect in ((hi, 1.0), (lo, 0.0)):
        crn = draw_common_random_numbers(c, 5)
        m = compute_metrics(c, simulate(c, "uniform", crn), crn)
        assert m["recall_mean"] == pytest.approx(expect, abs=1e-6)


# ---- differential tests against the naive reference implementation
@settings(max_examples=40, deadline=None)
@given(c=configs(max_items=8, max_window=10), seed=st.integers(0, 2**31 - 1))
def test_engine_matches_reference(c, seed):
    crn = draw_common_random_numbers(c, seed)
    for arm in ARMS:
        tr = simulate(c, arm, crn)
        events, test = ref_simulate(c, arm, crn.half_lives_days, crn.review_uniforms)
        assert [(e[0], e[1]) for e in events] == list(zip(tr.event_session.tolist(), tr.event_item.tolist())), arm
        np.testing.assert_allclose([e[2] for e in events], tr.event_recall_prob, rtol=1e-9, atol=1e-300)  # power law: log1p form vs direct power
        assert [e[3] for e in events] == tr.event_success.tolist()
        np.testing.assert_allclose(test, tr.test_recall_prob, rtol=1e-9, atol=1e-300)


@pytest.mark.parametrize("arm", ARMS)
@pytest.mark.parametrize("model", ["exponential", "power"])
def test_engine_matches_reference_at_central_setting(arm, model):
    c = SimConfig(true_model=model)
    for seed in (1, 2, 3):
        crn = draw_common_random_numbers(c, seed)
        tr = simulate(c, arm, crn)
        events, test = ref_simulate(c, arm, crn.half_lives_days, crn.review_uniforms)
        assert [(e[0], e[1]) for e in events] == list(zip(tr.event_session.tolist(), tr.event_item.tolist()))
        np.testing.assert_allclose(test, tr.test_recall_prob, rtol=1e-9, atol=1e-300)


# ---- metrics
def test_metrics_hand_example():
    c = SimConfig(n_items=2, window_days=2, retention_interval_days=1, reviews_per_item=1, item_distribution="homogeneous")
    crn = make_crn(c, [1.0, 1.0], [[0.0], [1.0]], [0.5, 0.1])
    m = compute_metrics(c, simulate(c, "uniform", crn), crn)
    r = [2 ** -0.6, 2 ** -1.6]  # 0.6598, 0.3299
    assert m["recall_mean"] == pytest.approx(sum(r) / 2, abs=1e-15)
    assert m["observed_recall"] == 1.0  # 0.5 < 0.6598 and 0.1 < 0.3299
    assert m["mastery_share"] == 0.0
    assert m["recall_min"] == pytest.approx(r[1], abs=1e-15)
    assert m["calibration_mae"] is None
    assert m["peak_daily_load"] == 2 and m["sessions_used"] == 1 and m["review_events"] == 2
    assert m["recall_mean_at_ri"]["1"] == pytest.approx(m["recall_mean"], abs=1e-15)
