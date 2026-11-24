# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Rule (b) of protocol 16.2: baseline-only selection of the central retention interval."""

import numpy as np
import pytest

from memory_research.config import SimConfig
from memory_research.design import baseline_recall_by_ri, select_ri, selection_summary
from memory_research.items import draw_common_random_numbers
from memory_research.simulate import simulate


def test_select_ri_picks_closest_to_midpoint_with_ties_to_smaller():
    assert select_ri({1: 0.9, 2: 0.69, 3: 0.56, 4: 0.54, 5: 0.3}) == 3  # 0.56 and 0.54 tie, smaller wins
    assert select_ri({1: 0.9, 2: 0.8}) is None
    assert select_ri({1: 0.7, 2: 0.39}) == 1  # range is closed


def test_baseline_curve_matches_full_simulation_and_is_monotone():
    c = SimConfig(n_items=20, h0_days=5.0, retention_interval_days=7)
    curve = baseline_recall_by_ri(c, [1, 2, 3], [1, 7, 30, 90])
    direct = np.mean([np.mean(simulate(c, "uniform", draw_common_random_numbers(c, s)).test_recall_prob)
                      for s in (1, 2, 3)])
    assert curve[7] == pytest.approx(direct, rel=1e-12)
    assert selection_summary(curve, None)["monotone_non_increasing"]


def test_baseline_curve_does_not_depend_on_config_ri():
    # The schedule and the random numbers do not depend on RI, so any RI in the config gives the same curve.
    a = baseline_recall_by_ri(SimConfig(n_items=10, retention_interval_days=7), [4], [1, 50])
    b = baseline_recall_by_ri(SimConfig(n_items=10, retention_interval_days=200), [4], [1, 50])
    assert a == b
