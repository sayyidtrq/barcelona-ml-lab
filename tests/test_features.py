import pandas as pd

from barca_ml.features.build import add_result_label, add_rolling_form


def _df():
    return pd.DataFrame(
        {
            "match_date": pd.to_datetime(["2020-01-01", "2020-01-08", "2020-01-15"]),
            "home_team.home_team_name": ["Barcelona", "Eibar", "Barcelona"],
            "home_score": [2, 1, 0],
            "away_score": [0, 1, 3],
        }
    )


def test_result_label():
    out = add_result_label(_df())
    assert list(out["result"]) == ["Win", "Draw", "Lose"]


def test_rolling_form_has_no_leakage():
    out = add_rolling_form(add_result_label(_df()))
    # baris pertama tidak punya histori -> NaN, tidak boleh memakai hasil laga itu sendiri
    assert pd.isna(out["form_points"].iloc[0])
    assert out["form_points"].iloc[1] == 3  # hanya dari laga sebelumnya (Win)
