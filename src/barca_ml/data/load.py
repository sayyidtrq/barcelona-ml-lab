"""Loader data mentah. Satu fungsi per sumber data; jangan baca CSV langsung di notebook."""

from __future__ import annotations

import pandas as pd

from barca_ml.config import data_path


def load_matches(name: str = "train.csv") -> pd.DataFrame:
    """Data level pertandingan StatsBomb-style (skor, tim, stadion, wasit, manajer, Poss)."""
    df = pd.read_csv(data_path(name))
    df["match_date"] = pd.to_datetime(df["match_date"])
    return df.sort_values("match_date").reset_index(drop=True)


def load_events(name: str = "events_train.csv") -> pd.DataFrame:
    """Data event per aksi (pass, shot, dll). Besar (~330k baris); gunakan low_memory=False."""
    return pd.read_csv(data_path(name), low_memory=False)
