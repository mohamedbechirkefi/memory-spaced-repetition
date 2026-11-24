# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
from __future__ import annotations

import numpy as np
import pytest
from hypothesis import strategies as st

from memory_research.config import SimConfig
from memory_research.items import CommonRandomNumbers


def make_crn(config: SimConfig, half_lives, review_u=None, test_u=None, seed: int = 0) -> CommonRandomNumbers:
    n, s = config.n_items, config.n_review_sessions
    h = np.asarray(half_lives, dtype=float)
    ru = np.zeros((n, s)) if review_u is None else np.asarray(review_u, dtype=float)
    tu = np.full(n, 0.5) if test_u is None else np.asarray(test_u, dtype=float)
    return CommonRandomNumbers(seed, h, ru, tu)


@st.composite
def configs(draw, max_items: int = 12, max_window: int = 15):
    d = draw(st.integers(2, max_window))
    return SimConfig(
        n_items=draw(st.integers(1, max_items)),
        window_days=d,
        retention_interval_days=draw(st.integers(0, 40)),
        reviews_per_item=draw(st.integers(1, min(4, d - 1))),
        h0_days=draw(st.floats(0.05, 50.0)),
        alpha=draw(st.floats(0.01, 0.99)),
        beta=draw(st.floats(0.0, 3.0)),
        omega_per_day=draw(st.floats(0.1, 5.0)),
        true_model=draw(st.sampled_from(["exponential", "power"])),
        item_distribution=draw(st.sampled_from(["homogeneous", "lognormal", "bimodal"])),
    )


@pytest.fixture
def central() -> SimConfig:
    return SimConfig()

# No on-disk example database: runs leave no untracked state in the repository.
from hypothesis import settings as _settings

_settings.register_profile("memory", database=None, print_blob=True)
_settings.load_profile("memory")
