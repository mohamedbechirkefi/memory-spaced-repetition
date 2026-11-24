# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Forgetting curves: known values, probability bounds, monotone decay, invalid inputs."""

import math

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from memory_research.models import ModelError, initial_rate, recall_probability, update_rate

LN2 = math.log(2)


# ---- golden (hand-computed) curve values
@pytest.mark.parametrize("delta, expected", [(0.0, 1.0), (1.0, 0.5), (2.0, 0.25), (3.0, 0.125)])
def test_exponential_half_life_one_day(delta, expected):
    assert recall_probability("exponential", LN2, delta) == pytest.approx(expected, abs=1e-15)


def test_exponential_known_value_e_inverse():
    assert recall_probability("exponential", 0.5, 2.0) == pytest.approx(math.exp(-1.0), abs=1e-15)


@pytest.mark.parametrize("delta, expected", [(0.0, 1.0), (1.0, 0.5), (3.0, 0.25), (7.0, 0.125)])
def test_power_law_rate_one_omega_one(delta, expected):
    # (1 + delta)^(-1)
    assert recall_probability("power", 1.0, delta, omega=1.0) == pytest.approx(expected, abs=1e-15)


def test_power_law_known_value_omega_two():
    # (1 + 2*1.5)^(-0.5) = 4^(-0.5) = 0.5
    assert recall_probability("power", 0.5, 1.5, omega=2.0) == pytest.approx(0.5, abs=1e-15)


@pytest.mark.parametrize("model", ["exponential", "power"])
@pytest.mark.parametrize("h", [0.01, 0.5, 1.0, 3.0, 30.0])
@pytest.mark.parametrize("omega", [0.3, 1.0, 3.0])
def test_initial_rate_gives_stated_half_life(model, h, omega):
    n = initial_rate(model, h, omega)
    assert recall_probability(model, n, h, omega) == pytest.approx(0.5, rel=1e-12)


def test_retrieval_update_hand_values():
    out = update_rate([1.0, 1.0], [True, False], alpha=0.4, beta=0.6)
    np.testing.assert_allclose(out, [0.6, 1.6], rtol=0, atol=1e-15)


def test_retrieval_update_beta_zero_keeps_rate_on_failure():
    assert update_rate(2.0, False, alpha=0.4, beta=0.0) == 2.0


# ---- invalid inputs
@pytest.mark.parametrize("bad", [
    dict(model="linear", rate=1.0, delta=1.0),
    dict(model="exponential", rate=0.0, delta=1.0),
    dict(model="exponential", rate=-1.0, delta=1.0),
    dict(model="exponential", rate=float("nan"), delta=1.0),
    dict(model="exponential", rate=1.0, delta=-0.1),
    dict(model="exponential", rate=1.0, delta=float("inf")),
    dict(model="power", rate=1.0, delta=1.0, omega=0.0),
    dict(model="power", rate=1.0, delta=1.0, omega=float("nan")),
])
def test_recall_rejects_invalid_inputs(bad):
    with pytest.raises(ModelError):
        recall_probability(bad["model"], bad["rate"], bad["delta"], bad.get("omega", 1.0))


@pytest.mark.parametrize("h", [0.0, -1.0, float("nan"), float("inf")])
def test_initial_rate_rejects_invalid_half_life(h):
    with pytest.raises(ModelError):
        initial_rate("exponential", h)


@pytest.mark.parametrize("alpha, beta", [(0.0, 0.5), (1.0, 0.5), (-0.1, 0.5), (0.5, -0.1), (0.5, float("nan"))])
def test_update_rejects_invalid_parameters(alpha, beta):
    with pytest.raises(ModelError):
        update_rate(1.0, True, alpha, beta)


# ---- properties
rates = st.floats(1e-6, 1e3)
deltas = st.floats(0.0, 1e4)
omegas = st.floats(1e-3, 1e2)


@given(model=st.sampled_from(["exponential", "power"]), rate=rates, d=deltas, omega=omegas)
def test_probability_bounds(model, rate, d, omega):
    m = float(recall_probability(model, rate, d, omega))
    assert 0.0 <= m <= 1.0


@given(model=st.sampled_from(["exponential", "power"]), rate=rates, d1=deltas, d2=deltas, omega=omegas)
def test_monotone_non_increasing_in_delay(model, rate, d1, d2, omega):
    lo, hi = sorted((d1, d2))
    assert recall_probability(model, rate, hi, omega) <= recall_probability(model, rate, lo, omega)


@given(model=st.sampled_from(["exponential", "power"]), rate=rates, omega=omegas)
def test_full_recall_at_zero_delay(model, rate, omega):
    assert recall_probability(model, rate, 0.0, omega) == 1.0


@given(r1=rates, r2=rates, d=st.floats(0.0, 1e3), omega=omegas, model=st.sampled_from(["exponential", "power"]))
def test_higher_rate_never_recalls_better(r1, r2, d, omega, model):
    lo, hi = sorted((r1, r2))
    assert recall_probability(model, hi, d, omega) <= recall_probability(model, lo, d, omega)


@given(rate=st.floats(1e-3, 50.0), d=st.floats(0.0, 1e3), omega=st.floats(1e-2, 10.0))
def test_power_stable_form_matches_direct_form(rate, d, omega):
    direct = (1.0 + omega * d) ** (-rate)
    assert float(recall_probability("power", rate, d, omega)) == pytest.approx(direct, rel=1e-9, abs=1e-300)


def test_underflow_is_reported_not_clipped():
    assert recall_probability("exponential", 1e3, 1e3) == 0.0
