"""football-data.co.uk -> canonical match table (league-wide, one row per match).

Source CSV docs: https://www.football-data.co.uk/notes.txt
The canonical schema is source-independent; other sources (Understat, StatsBomb) should map
into the same columns so features never depend on a specific provider.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

BASE_URL = "https://www.football-data.co.uk/mmz4281/{code}/{league}.csv"

# canonical column -> football-data column
COLUMNS = {
    "home_team": "HomeTeam",
    "away_team": "AwayTeam",
    "home_goals": "FTHG",
    "away_goals": "FTAG",
    "home_shots": "HS",
    "away_shots": "AS",
    "home_shots_on_target": "HST",
    "away_shots_on_target": "AST",
}

# Pre-match 1X2 odds, first available wins. Market average columns were renamed in 2019/20.
ODDS_PREFIXES = ["Avg", "BbAv", "B365"]


def season_code(start_year: int) -> str:
    """2017 -> '1718' (the URL folder name)."""
    return f"{start_year % 100:02d}{(start_year + 1) % 100:02d}"


def season_label(start_year: int) -> str:
    """2017 -> '2017/2018' (same format as configs/config.yaml split)."""
    return f"{start_year}/{start_year + 1}"


def current_season_start(today: date | None = None) -> int:
    today = today or date.today()
    return today.year if today.month >= 7 else today.year - 1


def season_url(start_year: int, league: str = "SP1") -> str:
    return BASE_URL.format(code=season_code(start_year), league=league)


def parse_season(raw: pd.DataFrame, start_year: int) -> pd.DataFrame:
    """Map one raw football-data season CSV to the canonical schema."""
    raw = raw.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])
    out = pd.DataFrame({"match_date": pd.to_datetime(raw["Date"], dayfirst=True, format="mixed")})
    out["kick_off"] = raw["Time"] if "Time" in raw else pd.NA
    out["season"] = season_label(start_year)
    for canon, col in COLUMNS.items():
        out[canon] = raw[col] if col in raw else pd.NA
    for canon, suffix in [("odds_home", "H"), ("odds_draw", "D"), ("odds_away", "A")]:
        cols = [p + suffix for p in ODDS_PREFIXES if p + suffix in raw]
        out[canon] = raw[cols].bfill(axis=1).iloc[:, 0] if cols else pd.NA
    out["source"] = "football-data.co.uk"
    out[["home_goals", "away_goals"]] = out[["home_goals", "away_goals"]].astype(int)
    return out.reset_index(drop=True)


def build_matches(raw_dir: Path, league: str = "SP1") -> pd.DataFrame:
    """Concatenate every downloaded season in `raw_dir` (files named SP1_1718.csv, ...)."""
    frames = []
    for path in sorted(raw_dir.glob(f"{league}_*.csv")):
        code = path.stem.split("_")[1]
        start_year = 2000 + int(code[:2])
        raw = pd.read_csv(path, encoding="utf-8-sig", encoding_errors="replace")
        frames.append(parse_season(raw, start_year))
    if not frames:
        msg = f"No {league}_*.csv in {raw_dir}; run scripts/fetch_football_data.py"
        raise FileNotFoundError(msg)
    return pd.concat(frames).sort_values("match_date").reset_index(drop=True)


def team_view(matches: pd.DataFrame, team: str = "Barcelona") -> pd.DataFrame:
    """One row per `team` match from its own perspective. `result` is a TARGET, never a feature."""
    df = matches[(matches["home_team"] == team) | (matches["away_team"] == team)].copy()
    home = df["home_team"] == team
    df["is_home"] = home.astype(int)
    df["opponent"] = df["away_team"].where(home, df["home_team"])
    for side in ["goals", "shots", "shots_on_target"]:
        df[f"team_{side}"] = df[f"home_{side}"].where(home, df[f"away_{side}"])
        df[f"opp_{side}"] = df[f"away_{side}"].where(home, df[f"home_{side}"])
    df["odds_win"] = df["odds_home"].where(home, df["odds_away"])
    df["odds_lose"] = df["odds_away"].where(home, df["odds_home"])
    has_elo = "home_elo" in df  # set by barca_ml.features.build.add_elo on the league table
    if has_elo:
        df["team_elo"] = df["home_elo"].where(home, df["away_elo"])
        df["opp_elo"] = df["away_elo"].where(home, df["home_elo"])
    diff = df["team_goals"] - df["opp_goals"]
    df["result"] = pd.cut(diff, [-99, -1, 0, 99], labels=["Lose", "Draw", "Win"]).astype(str)
    keep = [
        "match_date",
        "kick_off",
        "season",
        "is_home",
        "opponent",
        "team_goals",
        "opp_goals",
        "team_shots",
        "opp_shots",
        "team_shots_on_target",
        "opp_shots_on_target",
        "odds_win",
        "odds_draw",
        "odds_lose",
        "result",
    ]
    if has_elo:
        keep[-1:-1] = ["team_elo", "opp_elo"]
    return df[keep].sort_values("match_date").reset_index(drop=True)
