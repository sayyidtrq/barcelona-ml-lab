import pandas as pd
import pytest

from barca_ml.data.football_data import team_view
from barca_ml.features.build import add_standings


def _league():
    """Two rounds of a 4-team league plus a new season (same-day games in each round)."""
    return pd.DataFrame(
        {
            "match_date": pd.to_datetime(
                ["2023-08-13", "2023-08-13", "2023-08-20", "2023-08-20", "2024-08-18"]
            ),
            "kick_off": ["21:00"] * 5,
            "season": ["2023/2024"] * 4 + ["2024/2025"],
            "home_team": ["Barcelona", "Sevilla", "Getafe", "Barcelona", "Barcelona"],
            "away_team": ["Getafe", "Valencia", "Valencia", "Sevilla", "Getafe"],
            "home_goals": [3, 1, 0, 1, 2],
            "away_goals": [0, 1, 2, 1, 0],
            "home_shots": [15] * 5,
            "away_shots": [8] * 5,
            "home_shots_on_target": [6] * 5,
            "away_shots_on_target": [3] * 5,
            "odds_home": [1.3] * 5,
            "odds_draw": [5.0] * 5,
            "odds_away": [9.0] * 5,
        }
    )


def test_first_round_has_no_history():
    out = add_standings(_league())
    assert out[["home_ppg", "away_ppg"]].iloc[:2].isna().all().all()


def test_same_day_games_do_not_see_each_other():
    # Barca-Getafe (row 0) is the same day as Sevilla-Valencia (row 1): rows 0-1 must not
    # depend on each other's score, even though row 0 comes first in the table
    base = add_standings(_league())
    changed_scores = _league()
    changed_scores.loc[0, ["home_goals", "away_goals"]] = [0, 5]
    changed = add_standings(changed_scores)
    cols = ["home_position", "away_position"]
    pd.testing.assert_frame_equal(base[cols].iloc[:2], changed[cols].iloc[:2])


def test_table_after_first_round():
    out = add_standings(_league())
    # round 2: Barca 3 pts (+3) is 1st, Getafe 0 pts (-3) last, Sevilla/Valencia 1 pt
    assert out["home_position"].iloc[3] == 1
    assert out["home_ppg"].iloc[3] == 3
    assert out["home_gd_per_game"].iloc[3] == 3
    assert out["home_position"].iloc[2] == 4  # Getafe
    assert out["away_ppg"].iloc[3] == 1  # Sevilla


def test_table_resets_each_season():
    out = add_standings(_league())
    assert pd.isna(out["home_ppg"].iloc[4])


@pytest.mark.parametrize("t", range(5))
def test_standings_have_no_leakage(t):
    """Changing the score of match t must not change table features of matches <= t."""
    base = add_standings(_league())
    changed_scores = _league()
    changed_scores.loc[t, "away_goals"] += 4
    changed = add_standings(changed_scores)
    cols = [c for c in base.columns if c.endswith(("_position", "_ppg", "_gd_per_game"))]
    pd.testing.assert_frame_equal(base[cols].iloc[: t + 1], changed[cols].iloc[: t + 1])


def test_team_view_passes_standings_through():
    tv = team_view(add_standings(_league()))
    assert {"team_position", "opp_position", "team_ppg", "opp_ppg"} <= set(tv.columns)
    assert tv["team_ppg"].iloc[1] == 3  # Barca after the 3-0 win
    assert tv["opp_ppg"].iloc[1] == 1  # Sevilla after the draw
