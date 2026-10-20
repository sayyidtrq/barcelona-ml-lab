import pandas as pd
import pytest

from barca_ml.data.football_data import team_view
from barca_ml.features.build import add_elo, add_rest_days


def _league():
    """Tiny canonical league table spanning two seasons."""
    return pd.DataFrame(
        {
            "match_date": pd.to_datetime(
                ["2023-08-13", "2023-08-20", "2023-08-27", "2024-08-18", "2024-08-25"]
            ),
            "kick_off": ["21:00"] * 5,
            "season": ["2023/2024"] * 3 + ["2024/2025"] * 2,
            "home_team": ["Barcelona", "Sevilla", "Barcelona", "Barcelona", "Getafe"],
            "away_team": ["Getafe", "Barcelona", "Sevilla", "Getafe", "Barcelona"],
            "home_goals": [2, 1, 3, 1, 0],
            "away_goals": [0, 1, 0, 1, 2],
            "home_shots": [15] * 5,
            "away_shots": [8] * 5,
            "home_shots_on_target": [6] * 5,
            "away_shots_on_target": [3] * 5,
            "odds_home": [1.3] * 5,
            "odds_draw": [5.0] * 5,
            "odds_away": [9.0] * 5,
        }
    )


def test_elo_starts_at_initial_and_is_pre_match():
    out = add_elo(_league())
    assert out[["home_elo", "away_elo"]].iloc[0].tolist() == [1500, 1500]
    # Barca won match 0, so its rating going into match 1 is above the start
    assert out["away_elo"].iloc[1] > 1500


@pytest.mark.parametrize("t", range(5))
def test_elo_has_no_leakage(t):
    """Changing the score of match t must not change any rating at matches <= t."""
    base = add_elo(_league())
    flipped = _league()
    flipped.loc[t, ["home_goals", "away_goals"]] = flipped.loc[
        t, ["away_goals", "home_goals"]
    ].values
    flipped.loc[t, "home_goals"] += 5
    changed = add_elo(flipped)
    cols = ["home_elo", "away_elo"]
    pd.testing.assert_frame_equal(base[cols].iloc[: t + 1], changed[cols].iloc[: t + 1])


def test_elo_regresses_toward_mean_between_seasons():
    no_reg = add_elo(_league(), season_regress=0)
    full_reg = add_elo(_league(), season_regress=1)
    # full regression -> everyone equal at the first match of the new season
    assert full_reg["home_elo"].iloc[3] == pytest.approx(full_reg["away_elo"].iloc[3])
    assert no_reg["home_elo"].iloc[3] > no_reg["away_elo"].iloc[3]


def test_team_view_passes_elo_through():
    tv = team_view(add_elo(_league()))
    assert {"team_elo", "opp_elo"} <= set(tv.columns)
    # match 1 (away at Sevilla): Barca carries the win from match 0, Sevilla is still at start
    assert tv["team_elo"].iloc[1] > 1500
    assert tv["opp_elo"].iloc[1] == 1500
    assert "team_elo" not in team_view(_league()).columns


def test_rest_days_uses_only_previous_match():
    tv = add_rest_days(team_view(_league()))
    assert pd.isna(tv["rest_days"].iloc[0])
    assert tv["rest_days"].iloc[1] == 7
    # changing a later date must not affect earlier rest_days
    later = _league()
    later.loc[4, "match_date"] = pd.Timestamp("2024-12-01")
    tv2 = add_rest_days(team_view(later))
    pd.testing.assert_series_equal(tv["rest_days"].iloc[:4], tv2["rest_days"].iloc[:4])
