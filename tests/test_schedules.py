# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Schedules: hand-computed plans, budgets, capacity and adaptive selection rules."""

import numpy as np
import pytest
from hypothesis import given

from conftest import configs, make_crn
from memory_research.config import SimConfig
from memory_research.schedules import (
    ARMS, ScheduleError, daily_capacity, expanding_sessions, make_scheduler, massed_plan, uniform_plan,
)
from memory_research.simulate import simulate


def test_uniform_plan_hand_example():
    c = SimConfig(n_items=4, window_days=9, reviews_per_item=2)
    # g = 8/2 = 4, phi_i = 4 (i+1)/4 = i+1
    assert uniform_plan(c) == [[1, 5], [2, 6], [3, 7], [4, 8]]


def test_uniform_last_item_is_exactly_equally_spaced(central):
    plan = uniform_plan(central)
    # g = 27/4 = 6.75: ceil(6.75), ceil(13.5), ceil(20.25), 27
    assert plan[-1] == [7, 14, 21, 27]


@pytest.mark.parametrize("k, s_max, expected", [
    (4, 27, [2, 5, 13, 27]),   # targets 1.8, 5.4, 12.6, 27
    (2, 27, [9, 27]),          # targets 9, 27
    (8, 27, [1, 2, 3, 4, 5, 7, 13, 27]),
    (1, 27, [27]),
    (3, 3, [1, 2, 3]),
])
def test_expanding_sessions_hand_examples(k, s_max, expected):
    assert expanding_sessions(k, s_max) == expected


def test_expanding_rejects_too_many_reviews():
    with pytest.raises(ScheduleError):
        expanding_sessions(5, 4)


def test_massed_plan_is_last_k_sessions(central):
    assert massed_plan(central)[0] == [24, 25, 26, 27]


def test_daily_capacity_central(central):
    cap = daily_capacity(central)
    assert cap.sum() == 200 and cap.size == 27
    assert set(cap.tolist()) == {7, 8}  # 200/27 = 7.41 with exact carry


@given(configs())
def test_fixed_plans_respect_budget_and_window(c):
    from memory_research.schedules import PLAN_BUILDERS
    for name, build in PLAN_BUILDERS.items():
        plan = build(c)
        assert len(plan) == c.n_items
        for sessions in plan:
            assert len(sessions) == c.reviews_per_item
            assert len(set(sessions)) == c.reviews_per_item, name
            assert all(1 <= s <= c.n_review_sessions for s in sessions), name
            assert sessions == sorted(sessions)


@given(configs())
def test_uniform_gaps_differ_by_at_most_one_day(c):
    g = c.n_review_sessions / c.reviews_per_item
    for sessions in uniform_plan(c):
        gaps = np.diff(sessions)
        assert np.all((gaps >= np.floor(g)) & (gaps <= np.ceil(g)))


@given(configs())
def test_capacity_sums_to_budget_and_fits(c):
    cap = daily_capacity(c)
    assert cap.sum() == c.budget
    assert cap.max() <= c.n_items
    assert cap.max() - cap.min() <= 1


def _leitner_case():
    # N = 3, sessions 1..3, B = 3, capacity 1 per session
    return SimConfig(n_items=3, window_days=4, reviews_per_item=1, true_model="exponential", item_distribution="homogeneous")


def test_leitner_hand_example():
    c = _leitner_case()
    # u = 0 always succeeds (m > 0); u = 1 always fails (m <= 1)
    ru = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]])
    tr = simulate(c, "leitner", make_crn(c, [1.0, 1.0, 1.0], ru))
    # s1: all due, box 1 -> item 0 (success: box 2, due 3)
    # s2: items 1, 2 due (box 1) -> item 1 (failure: box 1, due 3)
    # s3: items 0 (box 2), 1 (box 1), 2 (box 1) due -> lowest box, then index -> item 1
    assert tr.event_item.tolist() == [0, 1, 1]
    assert tr.event_session.tolist() == [1, 2, 3]


def test_leitner_uses_spare_capacity_on_lowest_box():
    c = SimConfig(n_items=2, window_days=4, reviews_per_item=3, item_distribution="homogeneous")
    tr = simulate(c, "leitner", make_crn(c, [1.0, 1.0]))
    # capacity 2 per session: both items reviewed every session, due or not
    assert tr.event_session.size == 6


def test_greedy_picks_lowest_predicted_recall_with_index_ties():
    c = SimConfig(n_items=4, window_days=3, reviews_per_item=1, item_distribution="lognormal")
    # half-lives: items 1 and 3 equally hard, item 0 easy, item 2 medium; capacity: s1 -> 2, s2 -> 2
    crn = make_crn(c, [10.0, 0.5, 2.0, 0.5])
    tr = simulate(c, "greedy", crn)
    assert tr.event_item[:2].tolist() == [1, 3]


def test_oracle_greedy_prediction_equals_truth():
    c = SimConfig(n_items=6, window_days=8, reviews_per_item=2)
    from memory_research.items import draw_common_random_numbers
    tr = simulate(c, "greedy", draw_common_random_numbers(c, 7))
    np.testing.assert_allclose(tr.event_predicted, tr.event_recall_prob, rtol=0, atol=1e-15)


def test_misspecified_greedy_prediction_differs_under_power_law():
    c = SimConfig(n_items=6, window_days=8, reviews_per_item=2, true_model="power")
    from memory_research.items import draw_common_random_numbers
    tr = simulate(c, "greedy-exp", draw_common_random_numbers(c, 7))
    assert np.max(np.abs(tr.event_predicted - tr.event_recall_prob)) > 1e-3


def test_unknown_arm_rejected(central):
    with pytest.raises(ScheduleError):
        make_scheduler("random", central, np.ones(central.n_items))


def test_all_registered_arms_build(central):
    for arm in ARMS:
        make_scheduler(arm, central, np.ones(central.n_items))
