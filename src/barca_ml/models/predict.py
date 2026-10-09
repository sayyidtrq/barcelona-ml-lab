"""Inferensi: dipakai oleh app Gradio / API."""
from __future__ import annotations

import joblib

from barca_ml.config import ROOT


def load_model(name: str = "classifier.joblib"):
    return joblib.load(ROOT / "models" / name)


def predict_proba(model, features: dict) -> dict:
    import pandas as pd

    X = pd.DataFrame([features])
    proba = model.predict_proba(X)[0]
    return dict(zip(model.classes_, map(float, proba)))
