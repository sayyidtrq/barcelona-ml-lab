"""Download La Liga CSVs from football-data.co.uk and build data/processed/matches.csv.

Idempotent: finished seasons are downloaded once; the current season is always refreshed.
Usage: python scripts/fetch_football_data.py [--first-season 2017]
"""

from __future__ import annotations

import argparse

import requests

from barca_ml.config import data_path, load_config
from barca_ml.data.football_data import (
    build_matches,
    current_season_start,
    season_code,
    season_url,
)


def main() -> None:
    cfg = load_config()["data"]["football_data"]
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-season", type=int, default=cfg["first_season"])
    args = parser.parse_args()

    league = cfg["league"]
    raw_dir = data_path("football_data")
    raw_dir.mkdir(parents=True, exist_ok=True)
    current = current_season_start()

    for year in range(args.first_season, current + 1):
        path = raw_dir / f"{league}_{season_code(year)}.csv"
        if path.exists() and year != current:
            continue
        resp = requests.get(season_url(year, league), timeout=30)
        if resp.status_code == 404:  # new season not published yet
            print(f"skip {year}: not published")
            continue
        resp.raise_for_status()
        path.write_bytes(resp.content)
        print(f"saved {path.name} ({len(resp.content) // 1024} KB)")

    matches = build_matches(raw_dir, league)
    out = data_path("matches.csv", kind="processed")
    matches.to_csv(out, index=False)
    print(f"{len(matches)} matches, {matches['season'].nunique()} seasons -> {out}")


if __name__ == "__main__":
    main()
