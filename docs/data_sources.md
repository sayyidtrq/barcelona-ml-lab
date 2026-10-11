# Data sources

| Source | What | Script | Status |
|---|---|---|---|
| [football-data.co.uk](https://www.football-data.co.uk/data.php) | La Liga (`SP1`) results, shots, 1X2 odds, 2017/18 to now | `scripts/fetch_football_data.py` | implemented |
| StatsBomb-style course data (85 Barca matches, 2018-2021) | events, lineups | `barca_ml.data.load` | legacy, copy manually to `data/raw/` |
| Understat | xG | - | planned |

## football-data.co.uk
- Free CSV download, no API key. Column docs: https://www.football-data.co.uk/notes.txt
- License: no formal license published. Free for personal/research use; credit the source, do not
  redistribute the raw CSVs (they stay in `data/raw/`, not committed). **TODO (Sayyid):** reread the
  site's terms before any public deploy.
- Odds columns: we take the market average (`AvgH/D/A`, called `BbAvH/D/A` before 2019/20), then
  fall back to Bet365. These are pre-match prices, so they're allowed as a **baseline/feature**
  (not leakage). Closing odds (`AvgCH`, ...) are not used.
- **Network note:** the domain may be blocked by some Indonesian ISPs (connect timeout). Run the fetch
  over a VPN, from Colab, or from GitHub Actions.

## Canonical schema (`data/processed/matches.csv`, one row per league match)
`match_date, kick_off, season, home_team, away_team, home_goals, away_goals, home_shots,
away_shots, home_shots_on_target, away_shots_on_target, odds_home, odds_draw, odds_away, source`

All La Liga matches are kept (not just Barca's), so later we can compute opponent strength (Elo,
standings, form). `barca_ml.data.football_data.team_view()` produces the Barca-perspective table.
