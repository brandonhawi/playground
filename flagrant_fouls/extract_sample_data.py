#!/usr/bin/env python3
"""
Extract sample of flagrant foul data WITH box score covariates
Limited to ~250 games to stay under API rate limit (500-600 calls/hour)
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime
from pathlib import Path
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder
from nba_api.stats.endpoints.playbyplayv3 import PlayByPlayV3
from nba_api.stats.endpoints.boxscoretraditionalv3 import BoxScoreTraditionalV3
import warnings
warnings.filterwarnings('ignore')

csv_file = Path('nba_flagrant_fouls.csv')

def extract_game_data(game_id):
    """Extract flagrant fouls, game outcome, and box score statistics."""
    try:
        # Get play-by-play for flagrant fouls
        pbp_response = PlayByPlayV3(game_id=game_id)
        pbp = pbp_response.play_by_play.get_data_frame()

        # Extract flagrants by team
        flagrants = pbp[pbp['subType'].isin(['Flagrant Type 1', 'Flagrant Type 2'])]
        home_flagrants = len(flagrants[flagrants['location'] == 'h'])
        away_flagrants = len(flagrants[flagrants['location'] == 'v'])

        # Get final score
        final_row = pbp.iloc[-1]
        home_score = final_row['scoreHome']
        away_score = final_row['scoreAway']

        # Get team IDs
        team_rows = pbp[pbp['teamId'] != 0]
        home_team = team_rows[team_rows['location'] == 'h']['teamId'].iloc[0]
        away_team = team_rows[team_rows['location'] == 'v']['teamId'].iloc[0]

        # Get box score statistics
        box_response = BoxScoreTraditionalV3(game_id=game_id)
        box_stats = box_response.get_data_frames()[0]

        # Aggregate team-level statistics
        team_stats = box_stats.groupby('teamId').agg({
            'reboundsTotal': 'sum',
            'assists': 'sum',
            'turnovers': 'sum',
            'freeThrowsMade': 'sum',
            'freeThrowsAttempted': 'sum'
        }).to_dict('index')

        home_stats = team_stats.get(home_team, {})
        away_stats = team_stats.get(away_team, {})

        # Count inactive players (minutes == '0' or empty)
        home_inactive = len(box_stats[(box_stats['teamId'] == home_team) & ((box_stats['minutes'] == '0') | (box_stats['minutes'] == ''))])
        away_inactive = len(box_stats[(box_stats['teamId'] == away_team) & ((box_stats['minutes'] == '0') | (box_stats['minutes'] == ''))])

        return {
            'game_id': str(game_id),
            'home_team': int(home_team),
            'away_team': int(away_team),
            'home_flagrants': int(home_flagrants),
            'away_flagrants': int(away_flagrants),
            'home_score': int(home_score),
            'away_score': int(away_score),
            'home_rebounds': int(home_stats.get('reboundsTotal', 0)),
            'away_rebounds': int(away_stats.get('reboundsTotal', 0)),
            'home_assists': int(home_stats.get('assists', 0)),
            'away_assists': int(away_stats.get('assists', 0)),
            'home_turnovers': int(home_stats.get('turnovers', 0)),
            'away_turnovers': int(away_stats.get('turnovers', 0)),
            'home_ftm': int(home_stats.get('freeThrowsMade', 0)),
            'away_ftm': int(away_stats.get('freeThrowsMade', 0)),
            'home_fta': int(home_stats.get('freeThrowsAttempted', 0)),
            'away_fta': int(away_stats.get('freeThrowsAttempted', 0)),
            'home_inactive_players': int(home_inactive),
            'away_inactive_players': int(away_inactive)
        }, None
    except Exception as e:
        return None, e

# Get 2023-24 season games
print("Fetching game IDs for 2023-24 season...")
gamefinder = LeagueGameFinder(season_nullable='2023-24')
games_df = gamefinder.get_data_frames()[0]
game_ids = games_df['GAME_ID'].unique().tolist()

# Limit to 250 games (500 API calls)
MAX_GAMES = 250
game_ids = game_ids[:MAX_GAMES]

print(f"Extracting {len(game_ids)} games (will use ~{len(game_ids)*2} API calls)")
print(f"Starting extraction at {datetime.now().strftime('%H:%M:%S')}")
print(f"Estimated completion: {(len(game_ids) * 1.5 / 60):.1f} minutes\n")

successful_count = 0
failed_count = 0
all_games = []

for i, game_id in enumerate(game_ids):
    if (i + 1) % 25 == 0:
        print(f"Progress: {i+1}/{len(game_ids)} | Success: {successful_count} | Errors: {failed_count}")

    game_data, error = extract_game_data(game_id)

    if game_data:
        all_games.append(game_data)
        successful_count += 1
    else:
        print(f"  Error on game {game_id}: {error}")
        failed_count += 1

    # 1.5 second throttle
    time.sleep(1.5)

# Save all data
if all_games:
    df = pd.DataFrame(all_games)
    df.to_csv(csv_file, index=False)
    print(f"\n{'='*70}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*70}")
    print(f"Successfully extracted: {successful_count} games")
    print(f"Errors: {failed_count} games")
    print(f"Saved to: {csv_file}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nSample data:")
    print(df.head())
else:
    print("No data extracted!")
