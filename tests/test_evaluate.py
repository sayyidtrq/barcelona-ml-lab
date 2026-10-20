import numpy as np
import pandas as pd
import pytest

from barca_ml.models.evaluate import (
    CLASSES,
    always_win_proba,
    baseline_reports,
    frequency_proba,
    market_proba,
    multiclass_brier,
)


def test_multiclass_brier_bounds():
    y = ["Win", "Draw"]
    perfect = np.array([[0, 0, 1], [1, 0, 0]], dtype=float)
    worst = np.array([[1, 0, 0], [0, 1, 0]], dtype=float)
    assert multiclass_brier(y, perfect) == 0
    assert multiclass_brier(y, worst) == 2


def test_frequency_proba_matches_train_distribution():
    proba = frequency_proba(pd.Series(["Win", "Win", "Draw", "Lose"]), n=3)
    assert proba.shape == (3, 3)
    assert proba[0].tolist() == [0.25, 0.25, 0.5]  # Draw, Lose, Win


def test_always_win_rows_sum_to_one():
    proba = always_win_proba(4)
    np.testing.assert_allclose(proba.sum(axis=1), 1)
    assert CLASSES[int(np.argmax(proba[0]))] == "Win"


def test_market_proba_removes_overround():
    df = pd.DataFrame({"odds_win": [1.5, np.nan], "odds_draw": [4.0, 3.0], "odds_lose": [6.0, 3.0]})
    proba = market_proba(df)
    assert proba[0].sum() == pytest.approx(1)
    assert proba[0][CLASSES.index("Win")] > proba[0][CLASSES.index("Lose")]
    assert np.isnan(proba[1]).all()


def test_baseline_reports_has_all_rows():
    y_train = pd.Series(["Win"] * 6 + ["Draw"] * 2 + ["Lose"] * 2)
    y_test = pd.Series(["Win", "Draw", "Lose", "Win"])
    test_df = pd.DataFrame(
        {"odds_win": [1.4, 1.6, 2.5, np.nan], "odds_draw": [4.5] * 4, "odds_lose": [7.0] * 4}
    )
    rep = baseline_reports(y_train, y_test, test_df)
    assert list(rep.index) == ["train_frequency", "always_win", "market_odds"]
    assert rep.loc["always_win", "accuracy"] == 0.5
    assert rep.loc["market_odds", "n"] == 3  # one row without odds is skipped
    assert rep.loc["train_frequency", "n"] == 4
    assert {"log_loss", "brier"} <= set(rep.columns)
