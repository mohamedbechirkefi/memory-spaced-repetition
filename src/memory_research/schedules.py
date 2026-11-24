# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Review schedules (protocol section 3).

Fixed arms produce a plan before the simulation starts. Adaptive arms choose
items session by session from observed outcomes only (never from the true
forgetting state, except through the model the scheduler is given).
All arms place exactly B = k N reviews in sessions 1..D-1, at most one review
per item per session.
"""

from __future__ import annotations

from typing import Final, Protocol

import numpy as np
from numpy.typing import NDArray

from .config import SimConfig
from .models import EXPONENTIAL, POWER, initial_rate, recall_probability, update_rate

FIXED_ARMS: Final = ("uniform", "expanding", "massed")
ADAPTIVE_ARMS: Final = ("leitner", "greedy", "greedy-exp", "greedy-power")
ARMS: Final = FIXED_ARMS + ADAPTIVE_ARMS
BASELINE: Final = "uniform"

LEITNER_INTERVALS_DAYS: Final = (1, 2, 4, 8, 16)  # boxes 1..5


class ScheduleError(ValueError):
    """Raised when a schedule cannot be built or behaves invalidly."""


def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


# ---------------------------------------------------------------- fixed plans

def uniform_plan(config: SimConfig) -> list[list[int]]:
    """Equal spacing g = (D-1)/k with item offsets phi_i = g (i+1)/N.

    Session of item i's j-th review: ceil(phi_i + j g), computed exactly in
    integers as ceil((D-1)((i+1) + j N) / (k N)). The last item gets reviews
    at g, 2g, ..., k g = D-1 (rounded up); earlier items are shifted earlier
    by less than one gap, which spreads the daily load.
    """
    n, k, s_max = config.n_items, config.reviews_per_item, config.n_review_sessions
    plan = []
    for i in range(n):
        plan.append([_ceil_div(s_max * ((i + 1) + j * n), k * n) for j in range(k)])
    return plan


def expanding_sessions(k: int, s_max: int) -> list[int]:
    """Geometric gaps g, 2g, 4g, ... (ratio 2) from encoding, ending at s_max.

    Targets t_j = g (2^(j+1) - 1), g = s_max / (2^k - 1), rounded half up to
    integer sessions; then a forward pass enforces s_j >= s_{j-1} + 1 and
    s_0 >= 1 so that sessions are distinct. Requires k <= s_max.
    """
    if not (1 <= k <= s_max):
        raise ScheduleError(f"need 1 <= k <= D-1, got k={k}, D-1={s_max}")
    denom = 2**k - 1
    out: list[int] = []
    prev = 0
    for j in range(k):
        num = s_max * (2 ** (j + 1) - 1)  # target = num / denom
        target = (2 * num + denom) // (2 * denom)  # round half up, exact
        s = max(target, prev + 1)
        out.append(s)
        prev = s
    if out[-1] != s_max:
        raise ScheduleError(f"expanding schedule does not end at D-1: {out}")
    return out


def expanding_plan(config: SimConfig) -> list[list[int]]:
    sessions = expanding_sessions(config.reviews_per_item, config.n_review_sessions)
    return [list(sessions) for _ in range(config.n_items)]


def massed_plan(config: SimConfig) -> list[list[int]]:
    """All k reviews in the last k sessions of the window (cramming)."""
    s_max, k = config.n_review_sessions, config.reviews_per_item
    sessions = list(range(s_max - k + 1, s_max + 1))
    return [list(sessions) for _ in range(config.n_items)]


PLAN_BUILDERS: Final = {"uniform": uniform_plan, "expanding": expanding_plan, "massed": massed_plan}


def daily_capacity(config: SimConfig) -> NDArray[np.int64]:
    """Capacity per session s = 1..D-1 with an exact integer carry.

    c_s = floor(s B / (D-1)) - floor((s-1) B / (D-1)); sum over s equals B.
    Index 0 of the returned array is session 1.
    """
    b, s_max = config.budget, config.n_review_sessions
    s = np.arange(0, s_max + 1, dtype=np.int64)
    cum = (s * b) // s_max
    cap = np.diff(cum)
    if cap.sum() != b or cap.max() > config.n_items:
        raise ScheduleError("daily capacity does not fit the budget or exceeds N")
    return cap


# ---------------------------------------------------------------- schedulers

class Scheduler(Protocol):
    name: str

    def select(self, session: int) -> NDArray[np.int64]:
        """Item indices to review in this session (any order; deduplicated by caller check)."""

    def predicted_recall(self, session: int, items: NDArray[np.int64]) -> NDArray[np.float64] | None:
        """Scheduler's predicted recall for the selected items, or None."""

    def observe(self, session: int, items: NDArray[np.int64], success: NDArray[np.bool_]) -> None:
        """Receive the observed outcomes of this session's reviews."""


class FixedScheduler:
    def __init__(self, name: str, plan: list[list[int]], config: SimConfig):
        self.name = name
        s_max = config.n_review_sessions
        by_session: list[list[int]] = [[] for _ in range(s_max + 1)]
        for i, sessions in enumerate(plan):
            for s in sessions:
                if not (1 <= s <= s_max):
                    raise ScheduleError(f"{name}: session {s} outside 1..{s_max}")
                by_session[s].append(i)
        self._by_session = [np.array(sorted(x), dtype=np.int64) for x in by_session]

    def select(self, session: int) -> NDArray[np.int64]:
        return self._by_session[session]

    def predicted_recall(self, session: int, items: NDArray[np.int64]) -> None:
        return None

    def observe(self, session: int, items: NDArray[np.int64], success: NDArray[np.bool_]) -> None:
        return None


class LeitnerScheduler:
    """Leitner boxes 1..5 with intervals 1, 2, 4, 8, 16 days.

    Encoding at day 0 places every item in box 1, due at day 1. Each session
    fills its capacity c_s (exact-carry rule of :func:`daily_capacity`) with
    the priority key (amendment A2, owner-approved 2026-11-24):

      1. coverage: items never reviewed since encoding first;
      2. due items (due day <= session) before items not yet due;
      3. earliest due day first (oldest overdue first);
      4. lowest box first;
      5. lowest item index.

    Spare capacity therefore goes to not-yet-due items by earliest due day,
    then lowest box, then index. Every item is reviewed at least once
    because B = k N >= N. Success promotes one box (capped at 5); failure
    demotes to box 1; next due = session + interval of the new box.
    """

    name = "leitner"

    def __init__(self, config: SimConfig):
        self._cap = daily_capacity(config)
        n = config.n_items
        self.box = np.ones(n, dtype=np.int64)
        self.due = np.ones(n, dtype=np.int64)
        self.reviewed = np.zeros(n, dtype=bool)
        self._idx = np.arange(n, dtype=np.int64)
        self._intervals = np.array(LEITNER_INTERVALS_DAYS, dtype=np.int64)

    def select(self, session: int) -> NDArray[np.int64]:
        c = int(self._cap[session - 1])
        not_due = (self.due > session).astype(np.int64)
        covered = self.reviewed.astype(np.int64)
        # np.lexsort sorts by the last key first.
        order = np.lexsort((self._idx, self.box, self.due, not_due, covered))
        return order[:c].astype(np.int64)

    def predicted_recall(self, session: int, items: NDArray[np.int64]) -> None:
        return None

    def observe(self, session: int, items: NDArray[np.int64], success: NDArray[np.bool_]) -> None:
        new_box = np.where(success, np.minimum(self.box[items] + 1, len(self._intervals)), 1)
        self.box[items] = new_box
        self.due[items] = session + self._intervals[new_box - 1]
        self.reviewed[items] = True


class GreedyScheduler:
    """Reviews c_s items per session: coverage first, then lowest predicted recall.

    Priority key (amendment A2, owner-approved 2026-11-24): (1) items never
    reviewed since encoding first; (2) lowest predicted recall under the
    scheduler's own model; (3) lowest item index. Capacity c_s follows the
    exact-carry rule of :func:`daily_capacity`, so every item is reviewed at
    least once (B = k N >= N).

    The scheduler knows each item's true initial half-life and the update
    parameters alpha, beta; it converts the half-life to a rate under its own
    model family and updates it from observed outcomes. Ties in predicted
    recall are broken by lowest item index. With the true model family it is
    the oracle-model condition of EXP-001 (its prediction equals the truth).
    """

    def __init__(self, name: str, model: str, config: SimConfig, half_lives_days: NDArray[np.float64]):
        self.name = name
        self.model = model
        self._cap = daily_capacity(config)
        self._omega = config.omega_per_day
        self._alpha, self._beta = config.alpha, config.beta
        self.rate = initial_rate(model, half_lives_days, self._omega)
        self.last = np.zeros(config.n_items, dtype=np.float64)
        self.reviewed = np.zeros(config.n_items, dtype=bool)
        self._idx = np.arange(config.n_items, dtype=np.int64)

    def _predict_all(self, session: int) -> NDArray[np.float64]:
        return recall_probability(self.model, self.rate, session - self.last, self._omega)

    def select(self, session: int) -> NDArray[np.int64]:
        c = int(self._cap[session - 1])
        m_hat = self._predict_all(session)
        order = np.lexsort((self._idx, m_hat, self.reviewed.astype(np.int64)))
        return order[:c].astype(np.int64)

    def predicted_recall(self, session: int, items: NDArray[np.int64]) -> NDArray[np.float64]:
        return recall_probability(self.model, self.rate[items], session - self.last[items], self._omega)

    def observe(self, session: int, items: NDArray[np.int64], success: NDArray[np.bool_]) -> None:
        self.rate[items] = update_rate(self.rate[items], success, self._alpha, self._beta)
        self.last[items] = float(session)
        self.reviewed[items] = True


def make_scheduler(arm: str, config: SimConfig, half_lives_days: NDArray[np.float64]) -> Scheduler:
    if arm in PLAN_BUILDERS:
        return FixedScheduler(arm, PLAN_BUILDERS[arm](config), config)
    if arm == "leitner":
        return LeitnerScheduler(config)
    if arm == "greedy":
        return GreedyScheduler(arm, config.true_model, config, half_lives_days)
    if arm == "greedy-exp":
        return GreedyScheduler(arm, EXPONENTIAL, config, half_lives_days)
    if arm == "greedy-power":
        return GreedyScheduler(arm, POWER, config, half_lives_days)
    raise ScheduleError(f"unknown arm {arm!r}; expected one of {ARMS}")
