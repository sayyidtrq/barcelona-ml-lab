# Features

Every feature for match t uses only information available before kick-off of match t.
Each one has an anti-leakage test in `tests/`.

| Feature | Function | Meaning | Source | Leakage risk / notes |
|---|---|---|---|---|
| `form_points`, `form_goals_for`, `form_goals_against` | `add_rolling_form` | Mean points / goals for / goals against over the last `form_window` matches | team view | `shift(1)` before rolling; first match is NaN |
| `team_elo`, `opp_elo` | `add_elo` (league table) -> `team_view` | Pre-match Elo of Barca and the opponent | all La Liga matches | Rating stored *before* the match updates it. K=20, home advantage 60, start 1500, 1/3 shrink to mean each new season. Promoted teams start at 1500 (probably too high) |
| `rest_days` | `add_rest_days` | Days since previous match | team view | Date of match t is known in advance. League-only data misses cup/UCL games, so rest is overestimated in those weeks |

Use `add_elo` on the **full league table** before `team_view`, otherwise opponent ratings only
reflect their games against Barca.
