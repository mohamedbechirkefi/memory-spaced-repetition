# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Rule (b) of protocol 16.2: choose the central retention interval from the
baseline arm alone. Only the ``uniform`` arm is ever simulated here; no other arm
and no contrast is computed."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from .config import SimConfig
from .items import draw_common_random_numbers
from .simulate import recall_at, simulate

BASELINE_ARM = "uniform"
TARGET_RANGE = (0.4, 0.7)
TARGET_MIDPOINT = 0.55
RI_CANDIDATES_DAYS = tuple(range(1, 366))
EXPLORATORY_SEEDS = tuple(range(1, 31))


def baseline_recall_by_ri(config: SimConfig, seeds: Iterable[int], ris: Iterable[int]) -> dict[int, float]:
    """Mean over seeds of the uniform arm's learner-level R at each retention interval.

    The uniform schedule does not depend on RI, so one simulation per seed suffices."""
    ris = list(ris)
    per_seed = []
    for seed in seeds:
        trace = simulate(config, BASELINE_ARM, draw_common_random_numbers(config, seed))
        per_seed.append([float(np.mean(recall_at(config, trace, ri))) for ri in ris])
    means = np.mean(np.asarray(per_seed), axis=0)
    return {ri: float(m) for ri, m in zip(ris, means)}


def select_ri(curve: dict[int, float], lo: float = TARGET_RANGE[0], hi: float = TARGET_RANGE[1],
              target: float = TARGET_MIDPOINT) -> int | None:
    """Protocol 16.2.2: candidate in [lo, hi] closest to the midpoint, ties to the smaller RI."""
    inside = [ri for ri, r in curve.items() if lo <= r <= hi]
    if not inside:
        return None
    return min(inside, key=lambda ri: (abs(curve[ri] - target), ri))


def selection_summary(curve: dict[int, float], chosen: int | None) -> dict[str, Any]:
    inside = [ri for ri, r in curve.items() if TARGET_RANGE[0] <= r <= TARGET_RANGE[1]]
    vals = list(curve.values())
    return {
        "chosen_ri_days": chosen,
        "baseline_R_at_chosen": None if chosen is None else curve[chosen],
        "candidates_in_range": [min(inside), max(inside)] if inside else None,
        "monotone_non_increasing": bool(all(b <= a + 1e-15 for a, b in zip(vals, vals[1:]))),
        "baseline_R_at": {str(ri): curve[ri] for ri in (1, 7, 30, 90, 180, 365) if ri in curve},
    }
