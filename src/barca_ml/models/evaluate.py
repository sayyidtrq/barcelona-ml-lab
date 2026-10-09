"""Evaluasi: selalu bandingkan dengan baseline, dan laporkan metrik probabilistik."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss


def majority_baseline_accuracy(y_train, y_test) -> float:
    """Akurasi kalau selalu menebak kelas mayoritas di train. Model harus mengalahkan ini."""
    majority = y_train.value_counts().idxmax()
    return float((y_test == majority).mean())


def classification_report_prob(y_true, proba, classes) -> dict:
    y_pred = np.array(classes)[np.argmax(proba, axis=1)]
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "log_loss": float(log_loss(y_true, proba, labels=list(classes))),
    }


def brier_binary(y_true_bin, p_pos) -> float:
    return float(brier_score_loss(y_true_bin, p_pos))
