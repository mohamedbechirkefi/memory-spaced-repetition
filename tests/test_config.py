# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Configuration validation and hashing."""

import pytest

from memory_research.config import ConfigError, SimConfig, config_hash


def test_central_setting_matches_protocol(central):
    assert (central.n_items, central.window_days, central.retention_interval_days, central.reviews_per_item) == (50, 28, 7, 4)
    assert central.budget == 200
    assert central.n_review_sessions == 27
    assert central.test_time_days == 34  # D - 1 + RI


@pytest.mark.parametrize("override", [
    {"n_items": 0}, {"window_days": 1}, {"retention_interval_days": -1}, {"reviews_per_item": 0},
    {"reviews_per_item": 28},  # more than D - 1 sessions
    {"n_items": 2.5}, {"n_items": True}, {"h0_days": 0.0}, {"h0_days": float("inf")},
    {"alpha": 1.0}, {"beta": -0.5}, {"omega_per_day": 0.0}, {"true_model": "linear"},
    {"item_distribution": "uniform"}, {"lognormal_sigma": -1.0},
])
def test_invalid_configs_are_rejected(override):
    with pytest.raises(ConfigError):
        SimConfig(**override)


def test_unknown_key_rejected():
    with pytest.raises(ConfigError):
        SimConfig.from_dict({"n_items": 5, "budget": 3})


def test_hash_is_stable_and_order_independent():
    a = {"x": 1, "y": [1, 2]}
    b = {"y": [1, 2], "x": 1}
    assert config_hash(a) == config_hash(b)
    assert config_hash(SimConfig()) == config_hash(SimConfig().to_dict())
    assert config_hash(SimConfig()) != config_hash(SimConfig(n_items=49))
