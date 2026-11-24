# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Uncertainty methods against textbook values."""

import numpy as np
import pytest

from memory_research.stats import (
    bootstrap_mean_ci, equivalence_verdict, holm, paired_t, regularized_beta, t_cdf, t_quantile,
)


@pytest.mark.parametrize("df, q", [(1, 12.706204736), (4, 2.776445105), (10, 2.228138852), (49, 2.009575237), (1000, 1.962339081)])
def test_t_quantile_textbook(df, q):
    assert t_quantile(0.975, df) == pytest.approx(q, abs=1e-6)


def test_t_cdf_symmetry_and_centre():
    assert t_cdf(0.0, 7) == pytest.approx(0.5, abs=1e-15)
    assert t_cdf(-1.3, 7) == pytest.approx(1 - t_cdf(1.3, 7), abs=1e-14)
    assert t_quantile(0.025, 4) == pytest.approx(-2.776445105, abs=1e-6)


def test_regularized_beta_known_value():
    # I_0.5(2, 3) = 11/16
    assert regularized_beta(2, 3, 0.5) == pytest.approx(0.6875, abs=1e-13)
    assert regularized_beta(1, 1, 0.3) == pytest.approx(0.3, abs=1e-14)


def test_paired_t_hand_example():
    r = paired_t([1.0, 2.0, 3.0])
    assert r["mean"] == 2.0 and r["sd"] == pytest.approx(1.0)
    half = 4.302652730 / np.sqrt(3)
    assert r["ci_low"] == pytest.approx(2 - half, abs=1e-6)
    assert r["ci_high"] == pytest.approx(2 + half, abs=1e-6)
    assert r["d_z"] == pytest.approx(2.0)


def test_paired_t_degenerate_cases():
    assert paired_t([0.5])["sd"] is None
    r = paired_t([0.25, 0.25, 0.25])
    assert r["sd"] == 0.0 and r["ci_low"] == r["ci_high"] == 0.25


def test_holm_textbook_example():
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5, None]) == [0.5, None]


def test_bootstrap_is_deterministic_and_brackets_mean():
    x = np.linspace(-1, 1, 21) ** 3 + 0.2
    a = bootstrap_mean_ci(x)
    b = bootstrap_mean_ci(x)
    assert a == b
    assert a[0] < x.mean() < a[1]
    assert bootstrap_mean_ci(np.full(10, 0.3)) == pytest.approx((0.3, 0.3))


@pytest.mark.parametrize("bad", [[], [np.nan, 1.0], [[1.0, 2.0]]])
def test_bootstrap_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        bootstrap_mean_ci(bad)


@pytest.mark.parametrize("lo, hi, verdict", [
    (-0.05, -0.01, "below zero"), (0.01, 0.05, "above zero"), (-0.01, 0.015, "practically equivalent"), (-0.03, 0.01, "inconclusive"),
])
def test_equivalence_rule(lo, hi, verdict):
    assert equivalence_verdict(lo, hi).startswith(verdict)
