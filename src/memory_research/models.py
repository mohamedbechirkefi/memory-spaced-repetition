# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Forgetting models and the retrieval update (protocol sections 2.2 to 2.4).

Units: time and delays in days, forgetting rates in 1/day for the exponential
model and dimensionless exponents for the power-law model, the power-law
time scale ``omega`` in 1/day. Every function is pure and validates its
inputs; invalid inputs raise :class:`ModelError`.
"""

from __future__ import annotations

import math
from typing import Final

import numpy as np
from numpy.typing import ArrayLike, NDArray

EXPONENTIAL: Final = "exponential"
POWER: Final = "power"
MODELS: Final = (EXPONENTIAL, POWER)

LN2: Final = math.log(2.0)


class ModelError(ValueError):
    """Raised on an invalid model name or parameter."""


def check_model(model: str) -> str:
    if model not in MODELS:
        raise ModelError(f"unknown forgetting model {model!r}; expected one of {MODELS}")
    return model


def _check_omega(model: str, omega: float) -> None:
    if model == POWER and not (math.isfinite(omega) and omega > 0.0):
        raise ModelError(f"power-law time scale omega must be finite and > 0, got {omega!r}")


def recall_probability(
    model: str, rate: ArrayLike, delta_days: ArrayLike, omega: float = 1.0
) -> NDArray[np.float64]:
    """Recall probability ``m`` after ``delta_days`` since the last review.

    exponential: ``m = exp(-rate * delta)``
    power:       ``m = (1 + omega * delta) ** (-rate)``, evaluated as
                 ``exp(-rate * log1p(omega * delta))`` for numerical stability.

    ``rate`` must be finite and > 0, ``delta_days`` finite and >= 0. The
    result lies in [0, 1] (values below the float range underflow to 0; they
    are not clipped).
    """
    check_model(model)
    _check_omega(model, omega)
    r = np.asarray(rate, dtype=np.float64)
    d = np.asarray(delta_days, dtype=np.float64)
    if not np.all(np.isfinite(r)) or np.any(r <= 0.0):
        raise ModelError("forgetting rate must be finite and > 0")
    if not np.all(np.isfinite(d)) or np.any(d < 0.0):
        raise ModelError("delay must be finite and >= 0 days")
    if model == EXPONENTIAL:
        return np.exp(-r * d)
    return np.exp(-r * np.log1p(omega * d))


def initial_rate(model: str, half_life_days: ArrayLike, omega: float = 1.0) -> NDArray[np.float64]:
    """Initial forgetting rate giving the stated initial half-life (protocol 2.4).

    exponential: ``n = ln 2 / h``; power: ``n = ln 2 / ln(1 + omega * h)``.
    Both curves then satisfy ``m(h) = 0.5``.
    """
    check_model(model)
    _check_omega(model, omega)
    h = np.asarray(half_life_days, dtype=np.float64)
    if not np.all(np.isfinite(h)) or np.any(h <= 0.0):
        raise ModelError("half-life must be finite and > 0 days")
    if model == EXPONENTIAL:
        return LN2 / h
    return LN2 / np.log1p(omega * h)


def update_rate(rate: ArrayLike, success: ArrayLike, alpha: float, beta: float) -> NDArray[np.float64]:
    """Multiplicative retrieval update (protocol 2.3).

    success: ``n <- (1 - alpha) n``; failure: ``n <- (1 + beta) n``.
    Requires ``0 < alpha < 1`` and ``beta >= 0``.
    """
    check_update_params(alpha, beta)
    r = np.asarray(rate, dtype=np.float64)
    if not np.all(np.isfinite(r)) or np.any(r <= 0.0):
        raise ModelError("forgetting rate must be finite and > 0")
    s = np.asarray(success, dtype=bool)
    return np.where(s, (1.0 - alpha) * r, (1.0 + beta) * r)


def check_update_params(alpha: float, beta: float) -> None:
    if not (math.isfinite(alpha) and 0.0 < alpha < 1.0):
        raise ModelError(f"alpha must satisfy 0 < alpha < 1, got {alpha!r}")
    if not (math.isfinite(beta) and beta >= 0.0):
        raise ModelError(f"beta must be finite and >= 0, got {beta!r}")
