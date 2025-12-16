"""
Season-long Kobe Quotient leaderboard generator.

Run with:
    uv run python3 ballhog/build_leaderboard.py --seasons 2023-24 2024-25
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable, List

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats

DEFAULT_SEASONS: List[str] = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
REQUEST_DELAY = 0.65  # seconds, satisfies NBA API rate limiting guidance


def fetch_player_stats(season: str, season_type: str) -> pd.DataFrame:
    """Pull season aggregate player stats from LeagueDashPlayerStats.

    Fetches both Base (for FTA, TOV) and Advanced (for AST_PCT) measure types
    and merges them to get all required columns for the Kobe Quotient calculation.
    """
    # Fetch Base stats (has FTA, TOV, TEAM_NAME, etc.)
    response_base = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star=season_type,
        per_mode_detailed="Totals",
        measure_type_detailed_defense="Base",
    )
    time.sleep(REQUEST_DELAY)
    df_base = response_base.get_data_frames()[0]

    # Fetch Advanced stats (has AST_PCT)
    response_adv = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star=season_type,
        per_mode_detailed="Totals",
        measure_type_detailed_defense="Advanced",
    )
    time.sleep(REQUEST_DELAY)
    df_adv = response_adv.get_data_frames()[0]

    # Merge on player and team identifiers, keeping all Base columns plus AST_PCT
    df = df_base.merge(
        df_adv[['PLAYER_ID', 'TEAM_ID', 'AST_PCT']],
        on=['PLAYER_ID', 'TEAM_ID'],
        how='left'
    )
    df["SEASON"] = season
    return df


def fetch_team_stats(season: str, season_type: str) -> pd.DataFrame:
    """Pull season aggregate team stats for denominator values."""
    response = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        season_type_all_star=season_type,
        per_mode_detailed="Totals",
        measure_type_detailed_defense="Base",
    )
    time.sleep(REQUEST_DELAY)
    df = response.get_data_frames()[0]
    df["SEASON"] = season
    return df


def compute_kobe_quotient(players: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Join player and team stats to calculate the Kobe Quotient per player-season."""
    player_cols = [
        "SEASON",
        "PLAYER_ID",
        "PLAYER_NAME",
        "TEAM_ID",
        "TEAM_ABBREVIATION",
        "GP",
        "MIN",
        "FGA",
        "FTA",
        "TOV",
        "AST_PCT",
    ]
    team_cols = [
        "SEASON",
        "TEAM_ID",
        "TEAM_NAME",
        "GP",
        "FGA",
        "FTA",
        "TOV",
    ]

    players_clean = players[player_cols].copy()
    teams_clean = teams[team_cols].copy()

    merged = players_clean.merge(
        teams_clean,
        on=["SEASON", "TEAM_ID"],
        suffixes=("", "_TEAM"),
        how="left",
    )

    merged["PLAYER_POSSESSIONS"] = (
        merged["FGA"] + 0.44 * merged["FTA"] + merged["TOV"]
    )
    merged["TEAM_POSSESSIONS"] = (
        merged["FGA_TEAM"] + 0.44 * merged["FTA_TEAM"] + merged["TOV_TEAM"]
    )

    merged["TEAM_POSSESSIONS"] = merged["TEAM_POSSESSIONS"].replace(0, pd.NA)

    # Standard Usage Rate (% of team possessions used)
    merged["USG_PCT"] = (
        merged["PLAYER_POSSESSIONS"] / merged["TEAM_POSSESSIONS"]
    ).fillna(0)

    # Self-Creation Index (usage adjusted down by assist percentage)
    # High value = high usage with low playmaking = selfish
    merged["SELF_CREATION_INDEX"] = merged["USG_PCT"] * (1 - (merged["AST_PCT"] / 100.0))

    # Assist-to-Usage Ratio (how much playmaking relative to usage)
    # Lower ratio = more selfish (high usage, low assists)
    merged["AST_TO_USG_RATIO"] = (merged["AST_PCT"] / 100.0) / merged["USG_PCT"]
    merged["AST_TO_USG_RATIO"] = merged["AST_TO_USG_RATIO"].replace([float('inf'), float('-inf')], 0).fillna(0)

    # Shot Creation Load (what % of player's possessions are shots vs turnovers)
    # Higher = more shooting, less playmaking/turnovers
    merged["SHOT_CREATION_LOAD"] = (
        merged["FGA"] / merged["PLAYER_POSSESSIONS"]
    ).fillna(0)

    # Composite Selfishness Score
    # Combines high usage + low assists + high shot creation
    # Normalized to 0-100 scale where higher = more selfish
    merged["SELFISHNESS_SCORE"] = (
        (merged["USG_PCT"] * 100) * 0.4 +  # 40% weight on usage
        ((1 - merged["AST_PCT"] / 100.0) * 100) * 0.4 +  # 40% weight on low assists
        (merged["SHOT_CREATION_LOAD"] * 100) * 0.2  # 20% weight on shot-heavy play
    )

    # Keep Kobe Quotient for backwards compatibility (same as Self-Creation Index)
    merged["KOBE_QUOTIENT"] = merged["SELF_CREATION_INDEX"]

    # Rankings based on Selfishness Score (primary metric for identifying selfish players)
    merged["TEAM_RANK"] = (
        merged.groupby(["SEASON", "TEAM_ID"])["SELFISHNESS_SCORE"]
        .rank(ascending=False, method="dense")
        .astype(int)
    )
    merged["LEAGUE_RANK"] = (
        merged.groupby("SEASON")["SELFISHNESS_SCORE"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    return merged


def build_leaderboard(
    seasons: Iterable[str],
    season_type: str,
) -> pd.DataFrame:
    """Fetch stats for the requested seasons and compute the Kobe Quotient."""
    outputs = []
    for season in seasons:
        print(f"Processing season {season} ({season_type})...")
        players = fetch_player_stats(season, season_type)
        teams = fetch_team_stats(season, season_type)
        leaderboard = compute_kobe_quotient(players, teams)
        outputs.append(leaderboard)
        print(
            f"  -> {len(leaderboard)} player rows processed; "
            f"most selfish: "
            f"{leaderboard.sort_values('SELFISHNESS_SCORE', ascending=False).iloc[0]['PLAYER_NAME']}"
        )
    return pd.concat(outputs, ignore_index=True)


def write_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Persist the leaderboard to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values(["SEASON", "SELFISHNESS_SCORE"], ascending=[True, False]).to_csv(
        output_path, index=False
    )
    print(f"Saved leaderboard to {output_path}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    """CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Build a season-long Kobe Quotient leaderboard."
    )
    parser.add_argument(
        "--seasons",
        nargs="+",
        default=DEFAULT_SEASONS,
        help="List of NBA seasons (e.g., 2023-24).",
    )
    parser.add_argument(
        "--season-type",
        default="Regular Season",
        choices=["Regular Season", "Playoffs"],
        help="NBA season type to query.",
    )
    parser.add_argument(
        "--output",
        default="ballhog/ballhog_metrics.csv",
        help="Path for the CSV output.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    """Script entrypoint."""
    args = parse_args(argv)
    leaderboard = build_leaderboard(args.seasons, args.season_type)
    write_csv(leaderboard, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
