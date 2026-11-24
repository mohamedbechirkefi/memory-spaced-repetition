# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Independent, deliberately naive reference simulator for differential tests.

Pure Python (``math`` and ``fractions`` only), one event at a time, with the
schedules re-derived from the protocol text rather than imported from
``schedules.py``. It is slow and is used only by the test suite.
"""

from __future__ import annotations

import math
from fractions import Fraction

from .config import SimConfig


def ref_recall(model: str, rate: float, delta: float, omega: float) -> float:
    if model == "exponential":
        return math.exp(-rate * delta)
    return (1.0 + omega * delta) ** (-rate)


def ref_initial_rate(model: str, h: float, omega: float) -> float:
    return math.log(2) / h if model == "exponential" else math.log(2) / math.log(1.0 + omega * h)


def ref_plan(arm: str, c: SimConfig) -> dict[int, list[int]]:
    """session -> items, for the fixed arms."""
    s_max, k, n = c.window_days - 1, c.reviews_per_item, c.n_items
    plan: dict[int, list[int]] = {s: [] for s in range(1, s_max + 1)}
    if arm == "uniform":
        g = Fraction(s_max, k)
        for i in range(n):
            phi = g * Fraction(i + 1, n)
            for j in range(k):
                plan[math.ceil(phi + j * g)].append(i)
    elif arm == "expanding":
        g = Fraction(s_max, 2**k - 1)
        prev = 0
        sessions = []
        for j in range(k):
            t = g * (2 ** (j + 1) - 1)
            r = math.floor(t + Fraction(1, 2))
            prev = max(r, prev + 1)
            sessions.append(prev)
        for s in sessions:
            plan[s].extend(range(n))
    elif arm == "massed":
        for s in range(s_max - k + 1, s_max + 1):
            plan[s].extend(range(n))
    else:
        raise ValueError(arm)
    return plan


def ref_capacity(c: SimConfig, s: int) -> int:
    b, s_max = c.budget, c.window_days - 1
    return (s * b) // s_max - ((s - 1) * b) // s_max


def ref_simulate(c: SimConfig, arm: str, half_lives, review_u, test_time: float | None = None):
    """Return (events, test_recall) where events = [(session, item, m, success, pred)]."""
    n, omega, model = c.n_items, c.omega_per_day, c.true_model
    rate = [ref_initial_rate(model, float(h), omega) for h in half_lives]
    last = [0.0] * n
    count = [0] * n
    # scheduler state
    box = [1] * n
    due = [1] * n
    intervals = [1, 2, 4, 8, 16]
    sched_model = {"greedy": model, "greedy-exp": "exponential", "greedy-power": "power"}.get(arm)
    if sched_model is not None:
        s_rate = [ref_initial_rate(sched_model, float(h), omega) for h in half_lives]
        s_last = [0.0] * n
    plan = ref_plan(arm, c) if arm in ("uniform", "expanding", "massed") else None

    events = []
    for s in range(1, c.window_days):
        if plan is not None:
            chosen = sorted(plan[s])
        elif arm == "leitner":
            order = sorted(range(n), key=lambda i: (0 if due[i] <= s else 1, box[i], i))
            chosen = sorted(order[: ref_capacity(c, s)])
        else:
            preds = {i: ref_recall(sched_model, s_rate[i], s - s_last[i], omega) for i in range(n)}
            order = sorted(range(n), key=lambda i: (preds[i], i))
            chosen = sorted(order[: ref_capacity(c, s)])
        for i in chosen:
            m = ref_recall(model, rate[i], s - last[i], omega)
            ok = bool(review_u[i][count[i]] < m)
            pred = None
            if sched_model is not None:
                pred = ref_recall(sched_model, s_rate[i], s - s_last[i], omega)
                s_rate[i] *= (1 - c.alpha) if ok else (1 + c.beta)
                s_last[i] = float(s)
            if arm == "leitner":
                box[i] = min(box[i] + 1, 5) if ok else 1
                due[i] = s + intervals[box[i] - 1]
            rate[i] *= (1 - c.alpha) if ok else (1 + c.beta)
            last[i] = float(s)
            count[i] += 1
            events.append((s, i, m, ok, pred))
    t = c.window_days - 1 + c.retention_interval_days if test_time is None else test_time
    test = [ref_recall(model, rate[i], t - last[i], omega) for i in range(n)]
    return events, test
