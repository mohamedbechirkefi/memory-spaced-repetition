# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Run validation (protocol section 8) and metrics (protocol section 5)."""

from __future__ import annotations

from typing import Any

import numpy as np

from .config import SimConfig
from .items import CommonRandomNumbers
from .simulate import Trace, recall_at

MASTERY_THRESHOLD = 0.9
EXTRA_RETENTION_INTERVALS_DAYS = (1, 7, 30)


def validate_trace(config: SimConfig, trace: Trace) -> list[str]:
    """Return the list of violated checks (empty when the run is valid)."""
    problems: list[str] = []
    n_ev = trace.event_session.size
    if n_ev != config.budget:
        problems.append(f"budget: {n_ev} review events, expected exactly B={config.budget}")
    if n_ev and (trace.event_session.min() < 1 or trace.event_session.max() > config.n_review_sessions):
        problems.append("window: a review lies outside sessions 1..D-1")
    if n_ev and np.any(np.diff(trace.event_session) < 0):
        problems.append("ordering: review times are not non-decreasing in processing order")
    if n_ev:
        keys = trace.event_session * (config.n_items + 1) + trace.event_item
        if np.unique(keys).size != n_ev:
            problems.append("ordering: an item is reviewed more than once in a session")
    for name, arr in (("review recall", trace.event_recall_prob), ("test recall", trace.test_recall_prob)):
        if np.any(~np.isfinite(arr)):
            problems.append(f"probability: NaN or infinite {name}")
        elif np.any((arr < 0.0) | (arr > 1.0)):
            problems.append(f"probability: {name} outside [0, 1]")
    pred = trace.event_predicted[~np.isnan(trace.event_predicted)]
    if np.any((pred < 0.0) | (pred > 1.0)):
        problems.append("probability: scheduler prediction outside [0, 1]")
    if np.any(~np.isfinite(trace.final_rate)) or np.any(trace.final_rate <= 0):
        problems.append("state: non-finite or non-positive final forgetting rate")
    return problems


def compute_metrics(config: SimConfig, trace: Trace, crn: CommonRandomNumbers) -> dict[str, Any]:
    m = trace.test_recall_prob
    observed = crn.test_uniforms < m
    pred_mask = ~np.isnan(trace.event_predicted)
    if pred_mask.any():
        calib = float(np.mean(np.abs(trace.event_predicted[pred_mask] - trace.event_recall_prob[pred_mask])))
    else:
        calib = None
    loads = np.bincount(trace.event_session, minlength=config.n_review_sessions + 1)[1:]
    reviews_per_item = np.bincount(trace.event_item, minlength=config.n_items)
    return {
        "recall_mean": float(np.mean(m)),
        "observed_recall": float(np.mean(observed)),
        "mastery_share": float(np.mean(m >= MASTERY_THRESHOLD)),
        "recall_min": float(np.min(m)),
        "recall_p10": float(np.percentile(m, 10)),
        "recall_mean_at_ri": {str(ri): float(np.mean(recall_at(config, trace, ri))) for ri in EXTRA_RETENTION_INTERVALS_DAYS},
        "calibration_mae": calib,
        "peak_daily_load": int(loads.max()) if loads.size else 0,
        "sessions_used": int(np.count_nonzero(loads)),
        "review_events": int(trace.event_session.size),
        "review_success_rate": float(np.mean(trace.event_success)) if trace.event_success.size else None,
        "min_reviews_per_item": int(reviews_per_item.min()),
        "max_reviews_per_item": int(reviews_per_item.max()),
        "items_never_reviewed": int(np.count_nonzero(reviews_per_item == 0)),
    }
