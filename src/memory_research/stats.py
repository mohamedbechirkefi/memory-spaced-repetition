# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Uncertainty methods of protocol section 7, without SciPy.

Student t distribution via the regularized incomplete beta function
(continued fraction, Lentz's method), quantiles by bisection.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike

BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20261124


def _betacf(a: float, b: float, x: float) -> float:
    tiny, eps = 1e-300, 1e-15
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 500):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def regularized_beta(a: float, b: float, x: float) -> float:
    if not (a > 0 and b > 0):
        raise ValueError("a and b must be > 0")
    if not (0.0 <= x <= 1.0):
        raise ValueError("x must lie in [0, 1]")
    if x in (0.0, 1.0):
        return x
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    front = math.exp(lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_cdf(t: float, df: float) -> float:
    if df <= 0:
        raise ValueError("degrees of freedom must be > 0")
    x = df / (df + t * t)
    tail = 0.5 * regularized_beta(df / 2.0, 0.5, x)
    return 1.0 - tail if t >= 0 else tail


def t_quantile(p: float, df: float) -> float:
    if not (0.0 < p < 1.0):
        raise ValueError("p must lie in (0, 1)")
    if p == 0.5:
        return 0.0
    if p < 0.5:
        return -t_quantile(1.0 - p, df)
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return 0.5 * (lo + hi)


def _as_1d(x: ArrayLike) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    if a.ndim != 1 or a.size == 0 or not np.all(np.isfinite(a)):
        raise ValueError("need a non-empty one-dimensional array of finite values")
    return a


def bootstrap_mean_ci(
    x: ArrayLike, level: float = 0.95, resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED
) -> tuple[float, float]:
    """Percentile bootstrap interval of the mean over independent units (seeds)."""
    a = _as_1d(x)
    rng = np.random.Generator(np.random.PCG64(seed))
    idx = rng.integers(0, a.size, size=(resamples, a.size))
    means = a[idx].mean(axis=1)
    lo, hi = np.quantile(means, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(lo), float(hi)


def paired_t(diff: ArrayLike, level: float = 0.95) -> dict[str, float | None]:
    """Mean, SD, t interval, two-sided p-value and d_z of paired differences."""
    a = _as_1d(diff)
    n = a.size
    mean = float(a.mean())
    if n < 2:
        return {"n": n, "mean": mean, "sd": None, "ci_low": None, "ci_high": None, "p_value": None, "d_z": None}
    sd = float(a.std(ddof=1))
    if sd == 0.0:
        return {"n": n, "mean": mean, "sd": 0.0, "ci_low": mean, "ci_high": mean,
                "p_value": None if mean == 0 else 0.0, "d_z": None}
    se = sd / math.sqrt(n)
    q = t_quantile(1 - (1 - level) / 2, n - 1)
    t = mean / se
    p = 2.0 * (1.0 - t_cdf(abs(t), n - 1))
    return {"n": n, "mean": mean, "sd": sd, "ci_low": mean - q * se, "ci_high": mean + q * se,
            "p_value": p, "d_z": mean / sd}


def holm(p_values: Sequence[float | None]) -> list[float | None]:
    """Holm step-down adjusted p-values; None entries are passed through."""
    valid = [(p, i) for i, p in enumerate(p_values) if p is not None]
    m = len(valid)
    out: list[float | None] = [None] * len(p_values)
    running = 0.0
    for rank, (p, i) in enumerate(sorted(valid)):
        adj = min(1.0, (m - rank) * p)
        running = max(running, adj)
        out[i] = running
    return out


def equivalence_verdict(ci_low: float, ci_high: float, delta: float = 0.02) -> str:
    """Protocol section 4 rule, applied to a 95% interval of the paired difference."""
    if ci_high < 0:
        return "below zero (contradicts the directional prediction)"
    if ci_low > 0:
        return "above zero"
    if -delta <= ci_low and ci_high <= delta:
        return "practically equivalent within delta"
    return "inconclusive"
