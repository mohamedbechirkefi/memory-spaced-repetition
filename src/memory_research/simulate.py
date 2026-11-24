# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Session-by-session simulation of one simulated learner under one arm.

Event ordering (protocol 2.3): sessions in increasing day order; within a
session the selected items are processed in ascending item index. Item
outcomes in a session are drawn from the common random numbers
``review_uniforms[i, j]`` (item i, its j-th review): success iff u < m.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .config import SimConfig
from .items import CommonRandomNumbers
from .models import initial_rate, recall_probability, update_rate
from .schedules import ScheduleError, make_scheduler


@dataclass(frozen=True)
class Trace:
    """Full record of one run. Event arrays are aligned and in processing order."""

    arm: str
    seed: int
    event_session: NDArray[np.int64]
    event_item: NDArray[np.int64]
    event_recall_prob: NDArray[np.float64]  # true m at review time
    event_success: NDArray[np.bool_]
    event_predicted: NDArray[np.float64]  # scheduler's prediction, NaN when none
    final_rate: NDArray[np.float64]
    last_review_day: NDArray[np.float64]
    test_recall_prob: NDArray[np.float64]  # true m_i(T_test)


def simulate(config: SimConfig, arm: str, crn: CommonRandomNumbers) -> Trace:
    n = config.n_items
    if crn.half_lives_days.shape != (n,) or crn.review_uniforms.shape != (n, config.n_review_sessions):
        raise ValueError("common random numbers do not match the configuration")
    sched = make_scheduler(arm, config, crn.half_lives_days)
    omega = config.omega_per_day
    rate = initial_rate(config.true_model, crn.half_lives_days, omega)
    last = np.zeros(n, dtype=np.float64)  # encoding at day 0
    count = np.zeros(n, dtype=np.int64)

    ev_s: list[NDArray[np.int64]] = []
    ev_i: list[NDArray[np.int64]] = []
    ev_m: list[NDArray[np.float64]] = []
    ev_ok: list[NDArray[np.bool_]] = []
    ev_p: list[NDArray[np.float64]] = []

    for s in range(1, config.n_review_sessions + 1):
        items = np.sort(np.asarray(sched.select(s), dtype=np.int64))
        if items.size == 0:
            continue
        if items[0] < 0 or items[-1] >= n:
            raise ScheduleError(f"{arm}: item index out of range in session {s}")
        if np.any(np.diff(items) == 0):
            raise ScheduleError(f"{arm}: item reviewed twice in session {s}")
        pred = sched.predicted_recall(s, items)
        m = recall_probability(config.true_model, rate[items], s - last[items], omega)
        u = crn.review_uniforms[items, count[items]]
        success = u < m
        rate[items] = update_rate(rate[items], success, config.alpha, config.beta)
        last[items] = float(s)
        count[items] += 1
        sched.observe(s, items, success)
        ev_s.append(np.full(items.size, s, dtype=np.int64))
        ev_i.append(items)
        ev_m.append(m)
        ev_ok.append(success)
        ev_p.append(np.full(items.size, np.nan) if pred is None else np.asarray(pred, dtype=np.float64))

    test_m = recall_probability(config.true_model, rate, config.test_time_days - last, omega)

    def cat(parts, dtype):
        return np.concatenate(parts).astype(dtype) if parts else np.zeros(0, dtype=dtype)

    return Trace(
        arm=arm,
        seed=crn.seed,
        event_session=cat(ev_s, np.int64),
        event_item=cat(ev_i, np.int64),
        event_recall_prob=cat(ev_m, np.float64),
        event_success=cat(ev_ok, bool),
        event_predicted=cat(ev_p, np.float64),
        final_rate=rate.copy(),
        last_review_day=last.copy(),
        test_recall_prob=test_m,
    )


def recall_at(config: SimConfig, trace: Trace, retention_interval_days: float) -> NDArray[np.float64]:
    """True recall of every item at D-1+RI for another RI (schedules do not depend on RI)."""
    t = config.window_days - 1 + retention_interval_days
    return recall_probability(config.true_model, trace.final_rate, t - trace.last_review_day, config.omega_per_day)
