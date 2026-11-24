# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Synthetic item difficulty (protocol 2.4) and common random numbers (protocol 6)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .config import SimConfig


@dataclass(frozen=True)
class CommonRandomNumbers:
    """Everything random about one simulated learner, drawn before any arm runs.

    half_lives_days: (N,) initial half-lives.
    review_uniforms: (N, D-1) uniform draw for item i's j-th review (j = 0..D-2).
    test_uniforms:   (N,) uniform draw for the observed delayed test.
    """

    seed: int
    half_lives_days: NDArray[np.float64]
    review_uniforms: NDArray[np.float64]
    test_uniforms: NDArray[np.float64]


def sample_half_lives(config: SimConfig, rng: np.random.Generator) -> NDArray[np.float64]:
    n, h0 = config.n_items, config.h0_days
    dist = config.item_distribution
    if dist == "homogeneous":
        return np.full(n, h0, dtype=np.float64)
    if dist == "lognormal":
        return np.exp(rng.normal(np.log(h0), config.lognormal_sigma, size=n))
    if dist == "bimodal":
        hard = rng.random(n) < 0.5
        f = config.bimodal_factor
        return np.where(hard, h0 / f, h0 * f).astype(np.float64)
    raise ValueError(f"unknown item distribution {dist!r}")  # unreachable after config validation


def draw_common_random_numbers(config: SimConfig, seed: int) -> CommonRandomNumbers:
    """Deterministic in (config, seed). Three independent child streams."""
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError(f"seed must be a non-negative integer, got {seed!r}")
    ss = np.random.SeedSequence(seed)
    s_diff, s_rev, s_test = ss.spawn(3)
    half_lives = sample_half_lives(config, np.random.Generator(np.random.PCG64(s_diff)))
    review_u = np.random.Generator(np.random.PCG64(s_rev)).random((config.n_items, config.n_review_sessions))
    test_u = np.random.Generator(np.random.PCG64(s_test)).random(config.n_items)
    return CommonRandomNumbers(seed, half_lives, review_u, test_u)
