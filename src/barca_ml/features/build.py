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


_TABLE_COLS = ["position", "ppg", "gd_per_game"]


def add_standings(matches: pd.DataFrame) -> pd.DataFrame:
    """Add each side's league table state BEFORE the match (`home_*`/`away_*` columns).

    `position` (1 = top; ties by points, goal difference, goals scored), `ppg` (points per game)
    and `gd_per_game`. Tables reset every season. Only matches on EARLIER dates count, so games
    played the same day don't see each other's results. Before a team's first game `ppg` and
    `gd_per_game` are NaN; `position` then is the order among all season teams (not informative).
    """
    out = matches.sort_values("match_date", kind="stable").copy()
    cols = {f"{side}_{name}": [] for side in ("home", "away") for name in _TABLE_COLS}
    for _, season_df in out.groupby("season", sort=False):
        teams = sorted(set(season_df["home_team"]) | set(season_df["away_team"]))
        table = pd.DataFrame(0, index=teams, columns=["pts", "gd", "gf", "played"])
        for _, day in season_df.groupby("match_date", sort=True):
            ranked = table.sort_values(["pts", "gd", "gf"], ascending=False, kind="stable")
            position = pd.Series(range(1, len(ranked) + 1), index=ranked.index)
            played = table["played"].where(table["played"] > 0)
            state = {
                "position": position,
                "ppg": table["pts"] / played,
                "gd_per_game": table["gd"] / played,
            }
            for side in ("home", "away"):
                for name in _TABLE_COLS:
                    cols[f"{side}_{name}"].extend(state[name][day[f"{side}_team"]].tolist())
            for row in day.itertuples(index=False):
                hg, ag = row.home_goals, row.away_goals
                for team, gf, ga in [(row.home_team, hg, ag), (row.away_team, ag, hg)]:
                    table.loc[team] += [3 if gf > ga else int(gf == ga), gf - ga, gf, 1]
    # groupby(season, sort=False) + sorted dates keeps the original (date-sorted) row order
    for name, values in cols.items():
        out[name] = values
    return out


def add_head_to_head(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Record against the same opponent in the last `window` meetings before this match.

    df = one team's view (needs `opponent`, `result`, `team_goals`, `opp_goals`). Adds
    `h2h_points` (mean points), `h2h_goal_diff` (mean goal difference) and `h2h_n` (meetings
    used; 0 -> the means are NaN). Only meetings inside `df` count, so the history is limited
    to the seasons loaded.
    """
    out = df.sort_values("match_date").copy()
    pts = out["result"].map({"Win": 3, "Draw": 1, "Lose": 0})
    gd = out["team_goals"] - out["opp_goals"]
    by_opp = out["opponent"]

    def past(s: pd.Series, how: str) -> pd.Series:
        return s.groupby(by_opp).transform(
            lambda x: getattr(x.shift(1).rolling(window, min_periods=1), how)()
        )

    out["h2h_points"] = past(pts, "mean")
    out["h2h_goal_diff"] = past(gd, "mean")
    out["h2h_n"] = past(pts, "count").fillna(0).astype(int)
    return out
