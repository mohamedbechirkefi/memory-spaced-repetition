# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Duolingo trace ingestion and half-life calibration (protocol section 15.2).

Everything here is pure: :func:`ingest` turns an iterable of CSV lines into the
calibration subset plus counts; :func:`fit_half_lives` and :func:`validate`
compute the values of protocol 15.2.5 to 15.2.9 from that subset. No function
reads files, draws random numbers or touches the simulation. The raw file and
the processed arrays hold pseudonymous learner identifiers and are never
committed; only aggregate values are.
"""

from __future__ import annotations

import csv
import hashlib
import math
from dataclasses import dataclass, field
from typing import Any, Iterable

import numpy as np
from numpy.typing import NDArray

COLUMNS = (
    "p_recall", "timestamp", "delta", "user_id", "learning_language", "ui_language",
    "lexeme_id", "lexeme_string", "history_seen", "history_correct", "session_seen", "session_correct",
)
INT_COLUMNS = ("timestamp", "delta", "history_seen", "history_correct", "session_seen", "session_correct")
SECONDS_PER_DAY = 86400.0

# Protocol 15.2.5 to 15.2.7 (fixed before fitting).
MIN_TRIALS_PER_LEXEME = 100
H_MIN_DAYS = 0.01
H_MAX_DAYS = 3650.0
BISECTION_ITERATIONS = 60
MAD_TO_SD = 1.4826
MIN_ELIGIBLE_LEXEMES = 200
MAX_BOUNDARY_SHARE = 0.25
H0_RANGE_DAYS = (0.25, 365.0)
FALLBACK = {"h0_days": 6.0, "lognormal_sigma": 0.75}
INSTABILITY_THRESHOLD = 0.25
LN2 = math.log(2.0)


class SchemaMismatch(ValueError):
    """The input does not have the expected header."""


@dataclass
class Processed:
    """Calibration subset (history_seen == 1, delta > 0), one entry per row."""

    lexemes: list[str]  # lexeme_id per lexeme index
    lexeme: NDArray[np.int64]
    split_c: NDArray[np.bool_]  # True: calibration split C; False: validation split V
    delta_days: NDArray[np.float64]
    trials: NDArray[np.int64]
    successes: NDArray[np.int64]


@dataclass
class IngestReport:
    n_rows: int = 0
    n_valid: int = 0
    excluded: dict[str, int] = field(default_factory=dict)
    missing: dict[str, int] = field(default_factory=dict)
    n_subset_rows: int = 0
    n_subset_rows_by_split: dict[str, int] = field(default_factory=dict)
    n_subset_learners_by_split: dict[str, int] = field(default_factory=dict)
    n_subset_trials_by_split: dict[str, int] = field(default_factory=dict)
    n_not_first_review: int = 0
    n_zero_delta_first_review: int = 0

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def learner_in_calibration_split(user_id: str) -> bool:
    """Protocol 15.2.4: split C iff int(sha256(user_id)[:8], 16) is even."""
    return int(hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:8], 16) % 2 == 0


def _bump(d: dict[str, int], key: str) -> None:
    d[key] = d.get(key, 0) + 1


def ingest(lines: Iterable[str]) -> tuple[Processed, IngestReport]:
    """Validate every row, count missingness and exclusions, keep the calibration subset."""
    reader = csv.reader(lines)
    header = next(reader, None)
    if header is None or tuple(h.strip() for h in header) != COLUMNS:
        raise SchemaMismatch(f"unexpected header {header!r}; expected {COLUMNS}")
    rep = IngestReport(missing={c: 0 for c in COLUMNS})
    lex_index: dict[str, int] = {}
    lex, split, dd, nn, kk = [], [], [], [], []
    learners: dict[bool, set[str]] = {True: set(), False: set()}
    split_cache: dict[str, bool] = {}
    for row in reader:
        rep.n_rows += 1
        if len(row) != len(COLUMNS):
            _bump(rep.excluded, "wrong field count")
            continue
        rec = dict(zip(COLUMNS, row))
        empty = [c for c in COLUMNS if rec[c] == ""]
        for c in empty:
            rep.missing[c] += 1
        if empty:
            _bump(rep.excluded, "empty field")
            continue
        try:
            v = {c: int(rec[c]) for c in INT_COLUMNS}
            p = float(rec["p_recall"])
        except ValueError:
            _bump(rep.excluded, "unparsable number")
            continue
        if not (0.0 <= p <= 1.0):
            _bump(rep.excluded, "p_recall outside [0, 1]")
            continue
        if v["delta"] < 0:
            _bump(rep.excluded, "delta < 0")
            continue
        if v["history_seen"] < 1 or not (0 <= v["history_correct"] <= v["history_seen"]):
            _bump(rep.excluded, "history counts inconsistent")
            continue
        if v["session_seen"] < 1 or not (0 <= v["session_correct"] <= v["session_seen"]):
            _bump(rep.excluded, "session counts inconsistent")
            continue
        rep.n_valid += 1
        if v["history_seen"] != 1:
            rep.n_not_first_review += 1
            continue
        if v["delta"] == 0:
            rep.n_zero_delta_first_review += 1
            continue
        uid = rec["user_id"]
        in_c = split_cache.get(uid)
        if in_c is None:
            in_c = split_cache[uid] = learner_in_calibration_split(uid)
        learners[in_c].add(uid)
        lex.append(lex_index.setdefault(rec["lexeme_id"], len(lex_index)))
        split.append(in_c)
        dd.append(v["delta"] / SECONDS_PER_DAY)
        nn.append(v["session_seen"])
        kk.append(v["session_correct"])
    processed = Processed(
        lexemes=list(lex_index),
        lexeme=np.asarray(lex, dtype=np.int64),
        split_c=np.asarray(split, dtype=bool),
        delta_days=np.asarray(dd, dtype=np.float64),
        trials=np.asarray(nn, dtype=np.int64),
        successes=np.asarray(kk, dtype=np.int64),
    )
    rep.n_subset_rows = int(processed.lexeme.size)
    for name, mask in (("C", processed.split_c), ("V", ~processed.split_c)):
        rep.n_subset_rows_by_split[name] = int(mask.sum())
        rep.n_subset_trials_by_split[name] = int(processed.trials[mask].sum())
    rep.n_subset_learners_by_split = {"C": len(learners[True]), "V": len(learners[False])}
    return processed, rep


def _score(log_lam: NDArray[np.float64], group: NDArray[np.int64], n_groups: int,
           delta: NDArray[np.float64], n: NDArray[np.int64], k: NDArray[np.int64]) -> NDArray[np.float64]:
    """d/d(lambda) of the binomial log-likelihood per group (decreasing in lambda)."""
    x = np.exp(log_lam)[group] * delta
    with np.errstate(over="ignore", divide="ignore"):
        tail = np.where(x > 700.0, 0.0, delta / np.expm1(np.minimum(x, 700.0)))
    terms = -k * delta + (n - k) * tail
    return np.bincount(group, weights=terms, minlength=n_groups)


def mle_half_lives(group: NDArray[np.int64], n_groups: int, delta: NDArray[np.float64],
                   n: NDArray[np.int64], k: NDArray[np.int64]) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
    """Per-group MLE of h in [H_MIN_DAYS, H_MAX_DAYS] for p = 2^(-delta/h) (protocol 15.2.5).

    Returns (half-lives, boundary flags)."""
    lo = np.full(n_groups, math.log(LN2 / H_MAX_DAYS))  # smallest rate: largest h
    hi = np.full(n_groups, math.log(LN2 / H_MIN_DAYS))
    s_lo = _score(lo, group, n_groups, delta, n, k)
    s_hi = _score(hi, group, n_groups, delta, n, k)
    at_max_h = s_lo <= 0.0  # likelihood decreasing over the whole range: largest h
    at_min_h = s_hi >= 0.0
    a, b = lo.copy(), hi.copy()
    for _ in range(BISECTION_ITERATIONS):
        mid = 0.5 * (a + b)
        s = _score(mid, group, n_groups, delta, n, k)
        a = np.where(s > 0.0, mid, a)
        b = np.where(s > 0.0, b, mid)
    lam = np.exp(0.5 * (a + b))
    h = LN2 / lam
    h = np.where(at_max_h, H_MAX_DAYS, np.where(at_min_h, H_MIN_DAYS, h))
    return h, at_max_h | at_min_h


def _robust(h: NDArray[np.float64]) -> tuple[float, float]:
    logs = np.log(h)
    med = float(np.median(logs))
    return math.exp(med), MAD_TO_SD * float(np.median(np.abs(logs - med)))


def _sig3(x: float) -> float:
    return float(f"{x:.3g}")


def fit_split(data: Processed, split_c: bool) -> dict[str, Any]:
    """Protocol 15.2.5 and 15.2.6 on one split."""
    mask = data.split_c if split_c else ~data.split_c
    lex, d, n, k = data.lexeme[mask], data.delta_days[mask], data.trials[mask], data.successes[mask]
    n_lex = len(data.lexemes)
    trials = np.bincount(lex, weights=n, minlength=n_lex)
    eligible = trials >= MIN_TRIALS_PER_LEXEME
    keep = eligible[lex]
    remap = -np.ones(n_lex, dtype=np.int64)
    remap[eligible] = np.arange(int(eligible.sum()))
    g = remap[lex[keep]]
    n_elig = int(eligible.sum())
    out: dict[str, Any] = {"n_rows": int(mask.sum()), "n_trials": int(n.sum()), "n_eligible_lexemes": n_elig}
    if n_elig == 0:
        out.update(h0_days=None, lognormal_sigma=None, n_boundary=0, boundary_share=None)
        return out
    h, boundary = mle_half_lives(g, n_elig, d[keep], n[keep], k[keep])
    h0, sigma = _robust(h)
    pooled, _ = mle_half_lives(np.zeros(int(keep.sum()), dtype=np.int64), 1, d[keep], n[keep], k[keep])
    out.update(
        h0_days=h0, lognormal_sigma=sigma,
        n_boundary=int(boundary.sum()), boundary_share=float(boundary.mean()),
        n_at_upper_bound=int(np.sum(h >= H_MAX_DAYS)), n_at_lower_bound=int(np.sum(h <= H_MIN_DAYS)),
        half_life_quantiles_days={q: float(np.quantile(h, float(q))) for q in ("0.1", "0.25", "0.5", "0.75", "0.9")},
        pooled_mle_half_life_days=float(pooled[0]),
        mean_recall_rate=float(k.sum() / n.sum()),
    )
    return out


def usable(fit: dict[str, Any]) -> tuple[bool, list[str]]:
    """Protocol 15.2.7."""
    reasons = []
    if fit["n_eligible_lexemes"] < MIN_ELIGIBLE_LEXEMES:
        reasons.append(f"only {fit['n_eligible_lexemes']} eligible lexemes (< {MIN_ELIGIBLE_LEXEMES})")
    if fit.get("boundary_share") is not None and fit["boundary_share"] > MAX_BOUNDARY_SHARE:
        reasons.append(f"boundary share {fit['boundary_share']:.3f} > {MAX_BOUNDARY_SHARE}")
    h0 = fit.get("h0_days")
    if h0 is None or not (H0_RANGE_DAYS[0] <= h0 <= H0_RANGE_DAYS[1]):
        reasons.append(f"h0 {h0!r} outside {H0_RANGE_DAYS}")
    return not reasons, reasons


def log_loss(p: NDArray[np.float64], n: NDArray[np.int64], k: NDArray[np.int64]) -> float:
    p = np.clip(p, 1e-12, 1.0 - 1e-12)
    return float(-(k * np.log(p) + (n - k) * np.log1p(-p)).sum() / n.sum())


def calibrate(data: Processed) -> dict[str, Any]:
    """Full protocol 15.2.5 to 15.2.9: fit on C, usability rule, validation on V."""
    fit_c = fit_split(data, True)
    ok, reasons = usable(fit_c)
    if ok:
        values = {"h0_days": _sig3(fit_c["h0_days"]), "lognormal_sigma": _sig3(fit_c["lognormal_sigma"])}
        source = "fitted on split C (protocol 15.2.6)"
    else:
        values, source = dict(FALLBACK), "fallback (protocol 15.2.7): " + "; ".join(reasons)
    fit_v = fit_split(data, False)
    vmask = ~data.split_c
    d, n, k = data.delta_days[vmask], data.trials[vmask], data.successes[vmask]
    curve = np.exp2(-d / values["h0_days"])
    const = np.full(d.shape, fit_c.get("mean_recall_rate") or 0.5)
    rel = {}
    for key in ("h0_days", "lognormal_sigma"):
        a, b = fit_c.get(key), fit_v.get(key)
        rel[key] = None if (a in (None, 0) or b is None) else b / a - 1.0
    unstable = any(v is None or abs(v) > INSTABILITY_THRESHOLD for v in rel.values())
    return {
        "method": "research/protocol.md section 15.2",
        "values": values,
        "source": source,
        "usable": ok,
        "usability_reasons": reasons,
        "fit_split_C": fit_c,
        "validation": {
            "refit_split_V": fit_v,
            "relative_difference_V_vs_C": rel,
            "flag_unstable": unstable,
            "holdout_log_loss_per_trial": {
                "calibrated_curve": log_loss(curve, n, k) if n.size else None,
                "constant_split_C_mean": log_loss(const, n, k) if n.size else None,
                "n_rows": int(vmask.sum()),
                "n_trials": int(n.sum()),
            },
        },
    }


# Protocol 16.1 (round 3): diagnosis of the forgetting-model misfit. Fixed before computing.
QUADRATURE_NODES = 64
DELAY_BINS_DAYS = (0.0, 1.0 / 24.0, 1.0, 7.0, 30.0, math.inf)
DELAY_BIN_LABELS = ("< 1 hour", "1 hour to 1 day", "1 to 7 days", "7 to 30 days", ">= 30 days")


def exp_curve(delta_days: NDArray[np.float64], h_days: float) -> NDArray[np.float64]:
    """p = 2^(-delta/h)."""
    return np.exp2(-np.asarray(delta_days, dtype=np.float64) / h_days)


def power_curve(delta_days: NDArray[np.float64], n: float, omega: float) -> NDArray[np.float64]:
    """p = (1 + omega delta)^(-n), evaluated as exp(-n log1p(omega delta))."""
    return np.exp(-n * np.log1p(omega * np.asarray(delta_days, dtype=np.float64)))


def power_exponent_for_half_life(h_days: Any, omega: float) -> Any:
    """Protocol 2.4: n = ln 2 / ln(1 + omega h), same initial half-life as the exponential."""
    return LN2 / np.log1p(omega * np.asarray(h_days, dtype=np.float64))


def lognormal_population_curve(delta_days: NDArray[np.float64], h0: float, sigma: float, model: str,
                               omega: float = 1.0, nodes: int = QUADRATURE_NODES) -> NDArray[np.float64]:
    """E[p(delta; H)] with log H ~ Normal(log h0, sigma^2), by Gauss-Hermite quadrature."""
    x, w = np.polynomial.hermite.hermgauss(nodes)
    h = np.exp(math.log(h0) + math.sqrt(2.0) * sigma * x)
    w = w / math.sqrt(math.pi)
    d = np.asarray(delta_days, dtype=np.float64)[:, None]
    if model == "exponential":
        p = np.exp2(-d / h[None, :])
    elif model == "power":
        p = np.exp(-power_exponent_for_half_life(h, omega)[None, :] * np.log1p(omega * d))
    else:
        raise ValueError(f"unknown model {model!r}")
    return p @ w


def mle_power_exponent(delta: NDArray[np.float64], n: NDArray[np.int64], k: NDArray[np.int64],
                       omega: float) -> tuple[float, bool]:
    """Pooled MLE of n for p = (1 + omega delta)^(-n) (protocol 16.1.3, power-mle).

    p = exp(-n a) with a = log1p(omega delta), the exponential form with rate n and
    'delay' a, so the bisection of protocol 15.2.5 applies unchanged; it returns
    h = ln 2 / n, hence n = ln 2 / h, over the same bounds."""
    a = np.log1p(omega * np.asarray(delta, dtype=np.float64))
    h, boundary = mle_half_lives(np.zeros(a.size, dtype=np.int64), 1, a, n, k)
    return float(LN2 / h[0]), bool(boundary[0])


def compare_models(data: Processed, h0: float, sigma: float, omega: float = 1.0) -> dict[str, Any]:
    """Protocol 16.1: fit on split C, held-out log-loss on split V, family decision."""
    c, v = data.split_c, ~data.split_c
    dc, nc, kc = data.delta_days[c], data.trials[c], data.successes[c]
    dv, nv, kv = data.delta_days[v], data.trials[v], data.successes[v]
    const = float(kc.sum() / nc.sum())
    h_exp, b_exp = mle_half_lives(np.zeros(dc.size, dtype=np.int64), 1, dc, nc, kc)
    n_pow, b_pow = mle_power_exponent(dc, nc, kc, omega)
    n_med = float(power_exponent_for_half_life(h0, omega))
    curves = {
        "constant": lambda d: np.full(d.shape, const),
        "exp-median": lambda d: exp_curve(d, h0),
        "exp-population": lambda d: lognormal_population_curve(d, h0, sigma, "exponential"),
        "power-median": lambda d: power_curve(d, n_med, omega),
        "power-population": lambda d: lognormal_population_curve(d, h0, sigma, "power", omega),
        "exp-mle": lambda d: exp_curve(d, float(h_exp[0])),
        "power-mle": lambda d: power_curve(d, n_pow, omega),
    }
    pred_v = {name: f(dv) for name, f in curves.items()}
    losses = {name: log_loss(p, nv, kv) for name, p in pred_v.items()}
    families = {
        "exponential": min(("exp-median", "exp-population", "exp-mle"), key=lambda m: losses[m]),
        "power": min(("power-median", "power-population", "power-mle"), key=lambda m: losses[m]),
    }
    best = {fam: {"curve": m, "log_loss": losses[m], "beats_constant": losses[m] < losses["constant"]}
            for fam, m in families.items()}
    bins = []
    idx = np.digitize(dv, DELAY_BINS_DAYS[1:-1], right=False)
    for b, label in enumerate(DELAY_BIN_LABELS):
        m = idx == b
        tn = int(nv[m].sum())
        bins.append({
            "bin": label, "n_rows": int(m.sum()), "n_trials": tn,
            "observed_recall": float(kv[m].sum() / tn) if tn else None,
            "mean_prediction": {name: (float(np.sum(p[m] * nv[m]) / tn) if tn else None) for name, p in pred_v.items()},
        })
    better = "exponential" if best["exponential"]["log_loss"] < best["power"]["log_loss"] else "power"
    return {
        "method": "research/protocol.md section 16.1",
        "inputs": {"h0_days": h0, "lognormal_sigma": sigma, "omega_per_day": omega,
                   "quadrature_nodes": QUADRATURE_NODES},
        "fits_split_C": {"constant_recall": const, "exp_mle_half_life_days": float(h_exp[0]),
                         "exp_mle_boundary": bool(b_exp[0]), "power_mle_exponent": n_pow,
                         "power_mle_boundary": b_pow, "power_median_exponent": n_med},
        "holdout_log_loss_per_trial": losses,
        "n_rows_V": int(v.sum()), "n_trials_V": int(nv.sum()),
        "family_best": best,
        "better_family": better,
        "neither_beats_constant": not (best["exponential"]["beats_constant"] or best["power"]["beats_constant"]),
        "calibration_by_delay_bin_V": bins,
    }
