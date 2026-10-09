"""Entry point training. Jalankan: python -m barca_ml.models.train"""
from __future__ import annotations

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from barca_ml.config import ROOT, load_config


def build_model(random_state: int = 42):
    return make_pipeline(
        StandardScaler(),
        RandomForestClassifier(n_estimators=300, random_state=random_state, class_weight="balanced"),
    )


def main() -> None:
    cfg = load_config()
    # TODO: load -> build features -> time-based split -> fit -> evaluate -> save
    raise NotImplementedError("Lihat PLAN.md Fase 2-3")


if __name__ == "__main__":
    main()
    _ = (joblib, ROOT)
