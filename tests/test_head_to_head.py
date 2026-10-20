import pandas as pd
import pytest

from barca_ml.features.build import add_head_to_head


def _view():
    """Barca team view: three meetings with Real Madrid, two with Getafe."""
    return pd.DataFrame(
        {
            "match_date": pd.to_datetime(
                ["2023-08-13", "2023-10-28", "2024-01-14", "2024-04-21", "2024-05-01"]
            ),
            "opponent": ["Getafe", "Real Madrid", "Getafe", "Real Madrid", "Real Madrid"],
            "team_goals": [2, 1, 4, 2, 0],
            "opp_goals": [0, 2, 0, 3, 0],
            "result": ["Win", "Lose", "Win", "Lose", "Draw"],
        }
    )


def test_first_meeting_has_no_history():
    out = add_head_to_head(_view())
    first = out.drop_duplicates("opponent")
    assert (first["h2h_n"] == 0).all()
    assert first["h2h_points"].isna().all()


def test_h2h_only_uses_same_opponent():
    out = add_head_to_head(_view())
    # 3rd match (Getafe): only the 2-0 win counts, not the loss to Real Madrid in between
    assert out["h2h_points"].iloc[2] == 3
    assert out["h2h_goal_diff"].iloc[2] == 2
    # 5th match (Real Madrid): two previous losses
    assert out["h2h_n"].iloc[4] == 2
    assert out["h2h_points"].iloc[4] == 0
    assert out["h2h_goal_diff"].iloc[4] == -1


def test_h2h_window_limits_history():
    out = add_head_to_head(_view(), window=1)
    assert out["h2h_n"].iloc[4] == 1
    assert out["h2h_goal_diff"].iloc[4] == -1  # only the 2-3 loss


@pytest.mark.parametrize("t", range(5))
def test_h2h_has_no_leakage(t):
    """Changing the result of match t must not change h2h features of matches <= t."""
    base = add_head_to_head(_view())
    changed_view = _view()
    changed_view.loc[t, ["team_goals", "opp_goals", "result"]] = [9, 0, "Win"]
    changed = add_head_to_head(changed_view)
    cols = ["h2h_points", "h2h_goal_diff", "h2h_n"]
    pd.testing.assert_frame_equal(base[cols].iloc[: t + 1], changed[cols].iloc[: t + 1])
