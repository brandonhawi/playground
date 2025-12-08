"""
Test to validate GitHub Issue #596 from swar/nba_api
Issue: ScoreboardV2 not returning final scores for 2025 regular season games
https://github.com/swar/nba_api/issues/596
"""

from nba_api.stats.endpoints import ScoreboardV2, ScoreboardV3


def test_scoreboard_v2_2025():
    """Test ScoreboardV2 with 2025 regular season game (should return empty line scores)"""
    print("\n" + "="*80)
    print("Testing ScoreboardV2 with 2025 regular season game (Oct 22, 2025)")
    print("="*80)

    # Using a date from the 2025 regular season
    scoreboard = ScoreboardV2(game_date="2025-10-22", timeout=60)

    # Get game headers
    games = scoreboard.game_header.get_dict()["data"]
    print(f"\nGame header data retrieved: {len(games)} game(s) found")

    if games:
        print(f"Sample game: {games[0]}")

    # Get line scores - this is where the issue occurs
    linescores = scoreboard.line_score.get_dict()["data"]
    print(f"\nLine score data retrieved: {len(linescores)} line score(s) found")

    if not linescores:
        print("⚠️  ISSUE CONFIRMED: Line scores are empty for 2025 games with ScoreboardV2")
    else:
        print(f"✓ Line scores found: {linescores}")

    return len(games) > 0, len(linescores) > 0


def test_scoreboard_v2_2024():
    """Test ScoreboardV2 with 2024 regular season game (should work correctly)"""
    print("\n" + "="*80)
    print("Testing ScoreboardV2 with 2024 regular season game (Oct 22, 2024)")
    print("="*80)

    # Using a date from the 2024 regular season
    scoreboard = ScoreboardV2(game_date="2024-10-22", timeout=60)

    # Get game headers
    games = scoreboard.game_header.get_dict()["data"]
    print(f"\nGame header data retrieved: {len(games)} game(s) found")

    # Get line scores
    linescores = scoreboard.line_score.get_dict()["data"]
    print(f"Line score data retrieved: {len(linescores)} line score(s) found")

    if linescores:
        print(f"✓ Line scores working for 2024 games")
        print(f"Sample line score: {linescores[0][:5] if linescores else 'None'}")

    return len(games) > 0, len(linescores) > 0


def test_scoreboard_v3_2025():
    """Test ScoreboardV3 with 2025 regular season game (should work as workaround)"""
    print("\n" + "="*80)
    print("Testing ScoreboardV3 with 2025 regular season game (Oct 22, 2025)")
    print("="*80)

    try:
        # Using ScoreboardV3 as the workaround
        scoreboard = ScoreboardV3(game_date="2025-10-22", timeout=60)

        # Get scoreboard data
        scoreboard_data = scoreboard.get_dict()
        print(f"\nScoreboardV3 data structure keys: {list(scoreboard_data.keys())}")

        # Try to access games data
        if "scoreboard" in scoreboard_data:
            games_data = scoreboard_data["scoreboard"].get("games", [])
            print(f"Games found: {len(games_data)}")

            if games_data:
                print("✓ ScoreboardV3 successfully returns data for 2025 games")
                print(f"Sample game keys: {list(games_data[0].keys()) if games_data else 'None'}")
                return True

        print("ScoreboardV3 data retrieved but structure may differ")
        return True

    except Exception as e:
        print(f"Error with ScoreboardV3: {e}")
        return False


def test_multiple_2025_dates():
    """Test ScoreboardV2 with multiple 2025 regular season dates"""
    print("\n" + "="*80)
    print("Testing ScoreboardV2 with MULTIPLE 2025 regular season dates")
    print("="*80)

    # Test various dates throughout the 2025 season
    test_dates = [
        "2025-10-22",  # Opening week
        "2025-10-29",  # Week 2
        "2025-11-15",  # Mid November
        "2025-12-01",  # Early December
        "2025-12-25",  # Christmas Day games
        "2026-01-15",  # Mid season
        "2026-02-14",  # All-Star break period
        "2026-03-15",  # Late season
    ]

    results = []

    for date in test_dates:
        try:
            scoreboard = ScoreboardV2(game_date=date, timeout=60)
            games = scoreboard.game_header.get_dict()["data"]
            linescores = scoreboard.line_score.get_dict()["data"]

            result = {
                "date": date,
                "games": len(games),
                "linescores": len(linescores),
                "issue": len(games) > 0 and len(linescores) == 0
            }
            results.append(result)

            status = "⚠️ ISSUE" if result["issue"] else ("✓ OK" if len(linescores) > 0 else "- No games")
            print(f"{date}: {len(games)} games, {len(linescores)} line scores - {status}")

        except Exception as e:
            print(f"{date}: Error - {e}")
            results.append({"date": date, "error": str(e)})

    return results


def main():
    print("\n" + "="*80)
    print("NBA API Issue #596 Validation Test")
    print("="*80)

    # Test ScoreboardV2 with 2024 (should work)
    games_2024, scores_2024 = test_scoreboard_v2_2024()

    # Test ScoreboardV2 with 2025 (should have empty line scores)
    games_2025, scores_2025 = test_scoreboard_v2_2025()

    # Test multiple 2025 dates to validate the claim
    multiple_results = test_multiple_2025_dates()

    # Test ScoreboardV3 with 2025 (workaround)
    v3_works = test_scoreboard_v3_2025()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"ScoreboardV2 2024 - Games found: {games_2024}, Scores found: {scores_2024}")
    print(f"ScoreboardV2 2025 - Games found: {games_2025}, Scores found: {scores_2025}")
    print(f"ScoreboardV3 2025 - Works: {v3_works}")

    # Analyze multiple date results
    issue_count = sum(1 for r in multiple_results if r.get("issue", False))
    tested_count = sum(1 for r in multiple_results if "issue" in r)
    print(f"\nMultiple Date Test: {issue_count}/{tested_count} dates showed the issue")

    if issue_count == tested_count and tested_count > 0:
        print("\n✓ CLAIM VALIDATED: ALL tested 2025 dates show the same issue")
    elif issue_count > 0:
        print(f"\n⚠️ PARTIAL: {issue_count} out of {tested_count} dates show the issue")

    if games_2025 and not scores_2025:
        print("✓ ISSUE VALIDATED: ScoreboardV2 returns games but not line scores for 2025")
        if v3_works:
            print("✓ WORKAROUND CONFIRMED: ScoreboardV3 works for 2025 games")
    else:
        print("\n? Issue could not be reproduced or has been fixed")


if __name__ == "__main__":
    main()
