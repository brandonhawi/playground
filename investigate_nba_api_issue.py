"""
Deep investigation of NBA API Issue #596
Let's examine the actual data being returned to understand the bug
"""

from nba_api.stats.endpoints import ScoreboardV2
import json
from datetime import datetime


def detailed_game_analysis(game_date, label):
    """Analyze a specific date in detail"""
    print("\n" + "="*80)
    print(f"DETAILED ANALYSIS: {label} ({game_date})")
    print("="*80)

    scoreboard = ScoreboardV2(game_date=game_date, timeout=60)

    # Get all available data
    games = scoreboard.game_header.get_dict()["data"]
    linescores = scoreboard.line_score.get_dict()["data"]

    print(f"\nGames found: {len(games)}")
    print(f"Line scores found: {len(linescores)}")

    if games:
        print("\n--- SAMPLE GAME DATA ---")
        sample_game = games[0]
        headers = scoreboard.game_header.get_dict()["headers"]

        # Create a readable dict
        game_dict = dict(zip(headers, sample_game))

        print(f"Game ID: {game_dict.get('GAME_ID')}")
        print(f"Game Date: {game_dict.get('GAME_DATE_EST')}")
        print(f"Game Status: {game_dict.get('GAME_STATUS_TEXT')}")
        print(f"Season: {game_dict.get('SEASON')}")
        print(f"Home Team ID: {game_dict.get('HOME_TEAM_ID')}")
        print(f"Away Team ID: {game_dict.get('VISITOR_TEAM_ID')}")

        # Check game status
        game_status_id = game_dict.get('GAME_STATUS_ID')
        print(f"Game Status ID: {game_status_id} (1=Not Started, 2=In Progress, 3=Final)")

        # Analyze the GAME_ID to understand the season
        game_id = game_dict.get('GAME_ID', '')
        if game_id:
            # NBA game IDs format: 00SYYYGGGG where S=season type, YYY=year, GGGG=game number
            season_type = game_id[2]
            season_year = game_id[3:5]
            print(f"Game ID breakdown: Type={season_type}, Year=20{season_year}")

    if linescores:
        print("\n--- SAMPLE LINE SCORE DATA ---")
        sample_linescore = linescores[0]
        linescore_headers = scoreboard.line_score.get_dict()["headers"]
        linescore_dict = dict(zip(linescore_headers, sample_linescore))
        print(f"Team ID: {linescore_dict.get('TEAM_ID')}")
        print(f"PTS: {linescore_dict.get('PTS')}")
        print(f"Game ID: {linescore_dict.get('GAME_ID')}")
    else:
        print("\n--- NO LINE SCORE DATA ---")
        print("Line scores array is empty")

    # Check what other data sets are available
    print("\n--- AVAILABLE DATA SETS ---")
    available_datasets = [attr for attr in dir(scoreboard) if not attr.startswith('_')]
    for dataset in available_datasets[:20]:  # Show first 20
        try:
            data = getattr(scoreboard, dataset)
            if hasattr(data, 'get_dict'):
                dataset_data = data.get_dict()["data"]
                print(f"{dataset}: {len(dataset_data)} items")
        except:
            pass

    return {
        "date": game_date,
        "games": len(games),
        "linescores": len(linescores),
        "game_status": game_dict.get('GAME_STATUS_ID') if games else None,
        "season": game_dict.get('SEASON') if games else None,
        "game_id": game_dict.get('GAME_ID') if games else None
    }


def investigate_hypothesis():
    """Test specific hypotheses about the bug"""
    print("\n" + "="*80)
    print("HYPOTHESIS INVESTIGATION")
    print("="*80)

    test_cases = [
        # Past dates from 2025 season (definitely played)
        ("2024-10-22", "2024 season - Past played games"),

        # Early 2025 season dates (issue confirmed)
        ("2025-10-22", "2025 season opener - Issue confirmed"),
        ("2025-11-01", "2025 early season"),

        # Later 2025 season dates (worked in previous test)
        ("2026-01-15", "Jan 2026 - Worked before"),
        ("2026-03-15", "Mar 2026 - Worked before"),

        # Try dates closer to today
        ("2025-12-07", "Today's date (Dec 7, 2025)"),
        ("2025-12-06", "Yesterday"),
    ]

    results = []
    for date, label in test_cases:
        result = detailed_game_analysis(date, label)
        results.append(result)

    # Summary analysis
    print("\n" + "="*80)
    print("PATTERN ANALYSIS")
    print("="*80)

    for r in results:
        has_issue = r["games"] > 0 and r["linescores"] == 0
        status = "⚠️ ISSUE" if has_issue else "✓ OK"
        print(f"{r['date']}: Season={r['season']}, GameID={r['game_id']}, Status={r['game_status']} - {status}")

    # Check if there's a pattern based on game ID
    print("\n--- GAME ID PATTERN ANALYSIS ---")
    issue_dates = [r for r in results if r["games"] > 0 and r["linescores"] == 0]
    working_dates = [r for r in results if r["linescores"] > 0]

    if issue_dates:
        print(f"\nDates with issue (game IDs starting with):")
        for r in issue_dates:
            if r["game_id"]:
                print(f"  {r['date']}: {r['game_id'][:7]}")

    if working_dates:
        print(f"\nDates working correctly (game IDs starting with):")
        for r in working_dates:
            if r["game_id"]:
                print(f"  {r['date']}: {r['game_id'][:7]}")


if __name__ == "__main__":
    investigate_hypothesis()
