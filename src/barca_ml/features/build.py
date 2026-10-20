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


def add_elo(
    matches: pd.DataFrame,
    k: float = 20.0,
    home_advantage: float = 60.0,
    initial: float = 1500.0,
    season_regress: float = 1 / 3,
) -> pd.DataFrame:
    """Add league-wide PRE-MATCH Elo ratings (`home_elo`, `away_elo`) to a canonical match table.

    Each row gets the ratings *before* that match is played; the result only updates ratings for
    later matches. At a season change ratings shrink toward the mean by `season_regress`
    (squad turnover). Teams seen for the first time (e.g. promoted) start at `initial`.
    """
    out = matches.sort_values("match_date", kind="stable").copy()
    ratings: dict[str, float] = {}
    home_elo, away_elo = [], []
    season = None
    for row in out.itertuples(index=False):
        if "season" in out and row.season != season:
            if season is not None and ratings:
                mean = sum(ratings.values()) / len(ratings)
                ratings = {t: mean + (r - mean) * (1 - season_regress) for t, r in ratings.items()}
            season = row.season
        rh = ratings.get(row.home_team, initial)
        ra = ratings.get(row.away_team, initial)
        home_elo.append(rh)
        away_elo.append(ra)
        expected_home = 1 / (1 + 10 ** ((ra - rh - home_advantage) / 400))
        score_home = (
            1.0
            if row.home_goals > row.away_goals
            else (0.5 if row.home_goals == row.away_goals else 0.0)
        )
        delta = k * (score_home - expected_home)
        ratings[row.home_team] = rh + delta
        ratings[row.away_team] = ra - delta
    out["home_elo"] = home_elo
    out["away_elo"] = away_elo
    return out


def add_rest_days(df: pd.DataFrame) -> pd.DataFrame:
    """Days since the team's previous match in `df` (NaN for the first). df = one team's view.

    Only matches present in `df` count (league only for football-data), so midweek cup/UCL
    games are missed and rest is overestimated in those weeks.
    """
    out = df.sort_values("match_date").copy()
    out["rest_days"] = out["match_date"].diff().dt.days
    return out
