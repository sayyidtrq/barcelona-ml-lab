# Features

Every feature for match t uses only information available before kick-off of match t.
Each one has an anti-leakage test in `tests/`.

| Feature | Function | Meaning | Source | Leakage risk / notes |
|---|---|---|---|---|
| `form_points`, `form_goals_for`, `form_goals_against` | `add_rolling_form` | Mean points / goals for / goals against over the last `form_window` matches | team view | `shift(1)` before rolling; first match is NaN |
| `team_elo`, `opp_elo` | `add_elo` (league table) -> `team_view` | Pre-match Elo of Barca and the opponent | all La Liga matches | Rating stored *before* the match updates it. K=20, home advantage 60, start 1500, 1/3 shrink to mean each new season. Promoted teams start at 1500 (probably too high) |
| `team_position`, `opp_position`, `team_ppg`, `opp_ppg`, `team_gd_per_game`, `opp_gd_per_game` | `add_standings` (league table) -> `team_view` | League table before the match: rank, points per game, goal difference per game | all La Liga matches | Only matches on earlier dates count (same-day games are simultaneous). Resets each season; `ppg` NaN before a team's first game and `position` is meaningless early in the season, so prefer `ppg` |
| `h2h_points`, `h2h_goal_diff`, `h2h_n` | `add_head_to_head` | Mean points / goal difference in the last 5 meetings with this opponent, and how many meetings were used | team view | `shift(1)` within each opponent. Only seasons loaded count; few meetings per opponent (~2 per season), so noisy: use with `h2h_n` |
| `rest_days` | `add_rest_days` | Days since previous match | team view | Date of match t is known in advance. League-only data misses cup/UCL games, so rest is overestimated in those weeks |

Use `add_elo` and `add_standings` on the **full league table** before `team_view`, otherwise opponent ratings only
reflect their games against Barca.
