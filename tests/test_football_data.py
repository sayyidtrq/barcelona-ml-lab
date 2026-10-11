from datetime import date

import pandas as pd

from barca_ml.data.football_data import (
    build_matches,
    current_season_start,
    parse_season,
    season_code,
    team_view,
)
from barca_ml.features.build import add_rolling_form


def _raw(odds_prefix="Avg"):
    """Shape of a football-data.co.uk SP1 CSV (subset of columns)."""
    return pd.DataFrame(
        {
            "Div": ["SP1"] * 3 + [None],
            "Date": ["18/08/2023", "25/08/23", "01/09/2023", None],  # mixed yy/yyyy happens
            "HomeTeam": ["Barcelona", "Sevilla", "Real Madrid", None],
            "AwayTeam": ["Getafe", "Barcelona", "Valencia", None],
            "FTHG": [2, 1, 0, None],
            "FTAG": [0, 1, 3, None],
            "HS": [20, 8, 10, None],
            "AS": [5, 12, 9, None],
            "HST": [8, 3, 4, None],
            "AST": [1, 5, 6, None],
            f"{odds_prefix}H": [1.3, 4.0, 1.5, None],
            f"{odds_prefix}D": [5.0, 3.6, 4.0, None],
            f"{odds_prefix}A": [9.0, 1.9, 6.0, None],
        }
    )


def test_season_helpers():
    assert season_code(2017) == "1718"
    assert season_code(2099) == "9900"
    assert current_season_start(date(2026, 10, 11)) == 2026
    assert current_season_start(date(2027, 3, 1)) == 2026


def test_parse_season_drops_blank_rows_and_parses_dates():
    out = parse_season(_raw(), 2023)
    assert len(out) == 3
    assert list(out["match_date"].dt.day) == [18, 25, 1]
    assert (out["season"] == "2023/2024").all()


def test_parse_season_odds_fallback_for_old_column_names():
    out = parse_season(_raw(odds_prefix="BbAv"), 2017)
    assert out["odds_home"].iloc[0] == 1.3


def test_team_view_perspective():
    tv = team_view(parse_season(_raw(), 2023))
    assert len(tv) == 2  # Real Madrid - Valencia excluded
    assert list(tv["is_home"]) == [1, 0]
    assert list(tv["opponent"]) == ["Getafe", "Sevilla"]
    assert list(tv["result"]) == ["Win", "Draw"]
    assert list(tv["team_shots"]) == [20, 12]
    assert list(tv["odds_win"]) == [1.3, 1.9]  # away match -> away odds


def test_team_view_works_with_rolling_form():
    out = add_rolling_form(team_view(parse_season(_raw(), 2023)))
    assert pd.isna(out["form_points"].iloc[0])
    assert out["form_points"].iloc[1] == 3


def test_build_matches_reads_all_seasons(tmp_path):
    _raw("BbAv").to_csv(tmp_path / "SP1_1718.csv", index=False)
    _raw().to_csv(tmp_path / "SP1_2324.csv", index=False)
    out = build_matches(tmp_path)
    assert list(out["season"].unique()) == ["2017/2018", "2023/2024"]
    assert out["match_date"].is_monotonic_increasing
