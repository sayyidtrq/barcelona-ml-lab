"""Evaluasi: selalu bandingkan dengan baseline, dan laporkan metrik probabilistik."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss

# Fixed class order for every probability matrix (= sklearn's sorted order of the labels).
CLASSES = ("Draw", "Lose", "Win")


def majority_baseline_accuracy(y_train, y_test) -> float:
    """Akurasi kalau selalu menebak kelas mayoritas di train. Model harus mengalahkan ini."""
    majority = y_train.value_counts().idxmax()
    return float((y_test == majority).mean())


def multiclass_brier(y_true, proba, classes=CLASSES) -> float:
    """Mean squared error between proba and the one-hot outcome (0 = perfect, 2 = worst)."""
    onehot = (np.asarray(y_true)[:, None] == np.asarray(classes)[None, :]).astype(float)
    return float(np.mean(np.sum((np.asarray(proba) - onehot) ** 2, axis=1)))


def classification_report_prob(y_true, proba, classes=CLASSES) -> dict:
    y_pred = np.array(classes)[np.argmax(proba, axis=1)]
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "log_loss": float(log_loss(y_true, proba, labels=list(classes))),
        "brier": multiclass_brier(y_true, proba, classes),
    }


def brier_binary(y_true_bin, p_pos) -> float:
    return float(brier_score_loss(y_true_bin, p_pos))


def frequency_proba(y_train, n: int, classes=CLASSES) -> np.ndarray:
    """Predict the train class frequencies for every match (probabilistic majority baseline)."""
    freq = pd.Series(y_train).value_counts(normalize=True).reindex(classes, fill_value=0)
    return np.tile(freq.to_numpy(), (n, 1))


def always_win_proba(n: int, p_win: float = 0.98, classes=CLASSES) -> np.ndarray:
    """ "Barca always wins": near-certain Win. p_win < 1 so log loss stays finite on a loss."""
    rest = (1 - p_win) / (len(classes) - 1)
    row = [p_win if c == "Win" else rest for c in classes]
    return np.tile(row, (n, 1))


def market_proba(df: pd.DataFrame, classes=CLASSES) -> np.ndarray:
    """Implied probabilities from pre-match odds (team view), overround removed by normalising.

    Uses `odds_win`, `odds_draw`, `odds_lose`; rows with missing odds come out as NaN.
    """
    cols = {"Win": "odds_win", "Draw": "odds_draw", "Lose": "odds_lose"}
    inv = 1 / df[[cols[c] for c in classes]].to_numpy(dtype=float)
    return inv / inv.sum(axis=1, keepdims=True)


def baseline_reports(y_train, y_test, test_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Metrics of every baseline on the test set; the model must beat these rows."""
    y_test = pd.Series(y_test).reset_index(drop=True)
    n = len(y_test)
    rows = {
        "train_frequency": classification_report_prob(y_test, frequency_proba(y_train, n)),
        "always_win": classification_report_prob(y_test, always_win_proba(n)),
    }
    if test_df is not None and {"odds_win", "odds_draw", "odds_lose"} <= set(test_df.columns):
        proba = market_proba(test_df)
        ok = ~np.isnan(proba).any(axis=1)
        if ok.any():
            rows["market_odds"] = classification_report_prob(y_test[ok], proba[ok])
            rows["market_odds"]["n"] = int(ok.sum())
    out = pd.DataFrame(rows).T
    out["n"] = out.get("n", pd.Series(dtype=float)).fillna(n).astype(int)
    return out
