"""Pembuatan fitur PRE-MATCH.

ATURAN EMAS: fitur untuk pertandingan ke-t hanya boleh dihitung dari pertandingan < t.
Jangan pernah memakai skor akhir / statistik event dari pertandingan yang sedang diprediksi.
"""

from __future__ import annotations

import pandas as pd


def add_result_label(df: pd.DataFrame, team: str = "Barcelona") -> pd.DataFrame:
    """Label Win/Draw/Lose dari sudut pandang `team`. Hanya untuk TARGET, bukan fitur."""
    out = df.copy()
    is_home = out["home_team.home_team_name"].eq(team)
    gf = out["home_score"].where(is_home, out["away_score"])
    ga = out["away_score"].where(is_home, out["home_score"])
    out["is_home"] = is_home.astype(int)
    out["team_goals"], out["opp_goals"] = gf, ga
    out["result"] = (gf - ga).apply(lambda d: "Win" if d > 0 else ("Draw" if d == 0 else "Lose"))
    return out


def add_rolling_form(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Contoh fitur rolling dengan shift(1) agar tidak bocor. df harus urut waktu."""
    out = df.sort_values("match_date").copy()
    pts = out["result"].map({"Win": 3, "Draw": 1, "Lose": 0})
    out["form_points"] = pts.shift(1).rolling(window, min_periods=1).mean()
    out["form_goals_for"] = out["team_goals"].shift(1).rolling(window, min_periods=1).mean()
    out["form_goals_against"] = out["opp_goals"].shift(1).rolling(window, min_periods=1).mean()
    return out
