# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Ingestion and calibration (protocol 15.2) on a committed synthetic fixture and on
simulated traces with known half-lives. No real DS01 row is used or committed."""

from pathlib import Path

import numpy as np
import pytest

from memory_research.duolingo import (
    FALLBACK, H_MAX_DAYS, Processed, SchemaMismatch, calibrate, fit_split, ingest,
    learner_in_calibration_split, mle_half_lives,
)

FIXTURE = Path(__file__).parent / "fixtures" / "duolingo_synthetic.csv"


def test_ingest_counts_on_fixture():
    with FIXTURE.open(newline="") as fh:
        data, rep = ingest(fh)
    assert rep.n_rows == 47 and rep.n_valid == 41
    assert rep.excluded == {"wrong field count": 1, "empty field": 1, "unparsable number": 1, "delta < 0": 1,
                            "history counts inconsistent": 1, "session counts inconsistent": 1}
    assert rep.missing["user_id"] == 1 and sum(rep.missing.values()) == 1
    assert rep.n_not_first_review == 10 and rep.n_zero_delta_first_review == 1
    assert rep.n_subset_rows == 30 == data.lexeme.size
    assert rep.n_subset_rows_by_split["C"] + rep.n_subset_rows_by_split["V"] == 30
    assert sorted(data.lexemes) == ["synthlex00", "synthlex01", "synthlex02"]
    assert np.all(data.delta_days > 0) and np.all(data.successes <= data.trials)


def test_ingest_is_pure_and_deterministic():
    lines = FIXTURE.read_text().splitlines()
    a, ra = ingest(lines)
    b, rb = ingest(lines)
    assert ra.to_dict() == rb.to_dict()
    np.testing.assert_array_equal(a.delta_days, b.delta_days)


def test_ingest_rejects_wrong_header():
    with pytest.raises(SchemaMismatch):
        ingest(["a,b,c", "1,2,3"])


def test_split_is_by_learner_and_stable():
    assert learner_in_calibration_split("synthU0") == learner_in_calibration_split("synthU0")
    shares = np.mean([learner_in_calibration_split(f"u{i}") for i in range(4000)])
    assert 0.45 < shares < 0.55


def _simulated(h_true, rows_per_lexeme, rng, trials=5):
    lex, d, n, k = [], [], [], []
    for j, h in enumerate(h_true):
        dd = rng.uniform(0.1 * h, 3.0 * h, rows_per_lexeme)  # informative delays for each h
        kk = rng.binomial(trials, np.exp2(-dd / h))
        lex += [j] * rows_per_lexeme
        d += dd.tolist()
        n += [trials] * rows_per_lexeme
        k += kk.tolist()
    return np.array(lex), np.array(d), np.array(n), np.array(k)


def test_mle_recovers_known_half_lives():
    rng = np.random.default_rng(1)
    h_true = np.array([0.5, 2.0, 6.0, 20.0])
    lex, d, n, k = _simulated(h_true, 4000, rng)
    h, boundary = mle_half_lives(lex, 4, d, n, k)
    assert not boundary.any()
    np.testing.assert_allclose(h, h_true, rtol=0.08)


def test_all_correct_lexeme_sits_on_upper_bound():
    h, boundary = mle_half_lives(np.zeros(3, dtype=np.int64), 1, np.array([1.0, 2.0, 3.0]),
                                 np.array([4, 4, 4]), np.array([4, 4, 4]))
    assert boundary[0] and h[0] == H_MAX_DAYS


def _processed(h_true, rows, rng):
    lex, d, n, k = _simulated(h_true, rows, rng)
    split = (np.arange(lex.size) % 2 == 0)
    return Processed([f"x{i}" for i in range(len(h_true))], lex, split, d, n, k)


def test_calibrate_recovers_population_median_and_spread():
    rng = np.random.default_rng(2)
    h_true = np.exp(rng.normal(np.log(4.0), 0.5, 300))
    res = calibrate(_processed(h_true, 120, rng))
    assert res["usable"] and res["source"].startswith("fitted")
    assert res["values"]["h0_days"] == pytest.approx(4.0, rel=0.15)
    assert 0.4 < res["values"]["lognormal_sigma"] < 0.75  # sampling noise inflates sigma (disclosed)
    assert res["validation"]["holdout_log_loss_per_trial"]["n_rows"] > 0


def test_calibrate_falls_back_when_too_few_lexemes():
    rng = np.random.default_rng(3)
    res = calibrate(_processed(np.full(10, 3.0), 300, rng))
    assert not res["usable"] and res["values"] == FALLBACK


def test_fit_split_ignores_lexemes_below_trial_minimum():
    rng = np.random.default_rng(4)
    data = _processed(np.full(3, 3.0), 10, rng)  # 5 rows x 5 trials = 25 per split per lexeme
    assert fit_split(data, True)["n_eligible_lexemes"] == 0


# Protocol 16.1 (round 3): model comparison on synthetic data with a known generating curve.

from memory_research.duolingo import (  # noqa: E402
    compare_models, exp_curve, lognormal_population_curve, mle_power_exponent, power_curve,
    power_exponent_for_half_life,
)


def test_power_exponent_matches_initial_half_life():
    h = np.array([0.5, 6.0, 54.0])
    n = power_exponent_for_half_life(h, 1.0)
    np.testing.assert_allclose(power_curve(h[:1], n[0], 1.0), [0.5])
    np.testing.assert_allclose([power_curve(np.array([hh]), nn, 1.0)[0] for hh, nn in zip(h, n)], 0.5)


def test_population_curve_quadrature_matches_monte_carlo():
    rng = np.random.default_rng(5)
    hs = np.exp(rng.normal(np.log(10.0), 0.8, 400_000))
    d = np.array([0.1, 3.0, 10.0, 60.0])
    for model in ("exponential", "power"):
        q = lognormal_population_curve(d, 10.0, 0.8, model, 1.0)
        if model == "exponential":
            mc = np.exp2(-d[:, None] / hs[None, :]).mean(axis=1)
        else:
            mc = np.exp(-power_exponent_for_half_life(hs, 1.0)[None, :] * np.log1p(d[:, None])).mean(axis=1)
        np.testing.assert_allclose(q, mc, atol=2e-3)


def test_power_mle_recovers_exponent():
    rng = np.random.default_rng(6)
    d = rng.uniform(0.05, 60.0, 50_000)
    k = rng.binomial(5, power_curve(d, 0.3, 1.0))
    n_hat, boundary = mle_power_exponent(d, np.full(d.size, 5), k, 1.0)
    assert not boundary and n_hat == pytest.approx(0.3, rel=0.03)


def _single_curve_data(p_of_d, rng, rows=40_000):
    d = rng.uniform(0.01, 90.0, rows)
    k = rng.binomial(4, p_of_d(d))
    split = np.arange(rows) % 2 == 0
    return Processed(["x"], np.zeros(rows, dtype=np.int64), split, d, np.full(rows, 4), k)


def test_compare_models_prefers_the_generating_family():
    rng = np.random.default_rng(7)
    res = compare_models(_single_curve_data(lambda d: power_curve(d, 0.25, 1.0), rng), 10.0, 0.5)
    assert res["better_family"] == "power" and res["family_best"]["power"]["curve"] == "power-mle"
    assert res["family_best"]["power"]["beats_constant"] and not res["neither_beats_constant"]
    res = compare_models(_single_curve_data(lambda d: exp_curve(d, 20.0), rng), 20.0, 0.5)
    assert res["better_family"] == "exponential"
    assert sum(b["n_trials"] for b in res["calibration_by_delay_bin_V"]) == res["n_trials_V"]


def test_compare_models_flags_when_no_family_beats_constant():
    # Recall flat at 0.9 whatever the delay: every curve with p(0) = 1 loses to the constant.
    rng = np.random.default_rng(8)
    res = compare_models(_single_curve_data(lambda d: np.full(d.shape, 0.9), rng), 54.0, 0.759)
    assert res["neither_beats_constant"]
