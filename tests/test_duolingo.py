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
