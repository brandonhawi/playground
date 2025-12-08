"""
Find the exact cutoff point where line scores start appearing
"""

from nba_api.stats.endpoints import ScoreboardV2


def binary_search_cutoff():
    """Use binary search to find when line scores start appearing"""
    print("="*80)
    print("FINDING THE EXACT CUTOFF POINT")
    print("="*80)

    # We know:
    # - Game ~350 (Dec 6-7): NO line scores
    # - Game ~578 (Jan 15): HAS line scores
    # Let's test dates in between

    test_dates = [
        "2025-12-10",
        "2025-12-15",
        "2025-12-20",
        "2025-12-25",
        "2025-12-31",
        "2026-01-01",
        "2026-01-05",
        "2026-01-10",
        "2026-01-15",
    ]

    results = []

    for date in test_dates:
        try:
            scoreboard = ScoreboardV2(game_date=date, timeout=60)
            games = scoreboard.game_header.get_dict()["data"]
            linescores = scoreboard.line_score.get_dict()["data"]

            if games:
                game_id = games[0][2]  # GAME_ID is at index 2
                game_number = int(game_id[5:9])  # Extract game number from ID

                result = {
                    "date": date,
                    "game_id": game_id,
                    "game_number": game_number,
                    "games": len(games),
                    "linescores": len(linescores),
                    "has_linescores": len(linescores) > 0
                }
                results.append(result)

                status = "✓ HAS" if len(linescores) > 0 else "⚠️ MISSING"
                print(f"{date}: Game #{game_number:4d} ({game_id}) - {len(games)} games, {len(linescores):2d} linescores - {status}")
            else:
                print(f"{date}: No games scheduled")

        except Exception as e:
            print(f"{date}: Error - {e}")

    # Find the cutoff
    print("\n" + "="*80)
    print("CUTOFF ANALYSIS")
    print("="*80)

    missing = [r for r in results if not r["has_linescores"]]
    present = [r for r in results if r["has_linescores"]]

    if missing:
        max_missing = max(missing, key=lambda x: x["game_number"])
        print(f"Last game WITHOUT line scores: #{max_missing['game_number']} on {max_missing['date']}")

    if present:
        min_present = min(present, key=lambda x: x["game_number"])
        print(f"First game WITH line scores: #{min_present['game_number']} on {min_present['date']}")

    if missing and present:
        print(f"\nCutoff is somewhere between game #{max_missing['game_number']} and #{min_present['game_number']}")


def test_specific_game_numbers():
    """Test around the potential cutoff based on calendar date"""
    print("\n" + "="*80)
    print("TESTING AROUND POTENTIAL CUTOFF DATE")
    print("="*80)

    # Christmas is often a pivotal point in NBA season
    # Let's test days around it more granularly
    test_dates = [
        "2025-12-23",
        "2025-12-24",
        "2025-12-25",
        "2025-12-26",
        "2025-12-27",
        "2025-12-28",
        "2025-12-29",
        "2025-12-30",
    ]

    for date in test_dates:
        try:
            scoreboard = ScoreboardV2(game_date=date, timeout=60)
            games = scoreboard.game_header.get_dict()["data"]
            linescores = scoreboard.line_score.get_dict()["data"]

            if games:
                game_id = games[0][2]
                game_number = int(game_id[5:9])
                status = "✓ HAS" if len(linescores) > 0 else "⚠️ MISSING"
                print(f"{date}: Game #{game_number:4d} - {status} ({len(linescores)} line scores)")
        except Exception as e:
            print(f"{date}: Error - {e}")


if __name__ == "__main__":
    binary_search_cutoff()
    test_specific_game_numbers()
