"""
Test ScoreboardV3 backward compatibility with historical seasons
"""

from nba_api.stats.endpoints import ScoreboardV2, ScoreboardV3


def test_historical_seasons():
    """Test if V3 works for the last 5 NBA seasons"""
    print("="*80)
    print("Testing ScoreboardV3 Backward Compatibility")
    print("Testing last 5 seasons (2020-2025)")
    print("="*80)

    # Test one date from each of the last 5 seasons
    # Using Christmas Day games when available, or opening week
    test_dates = [
        ("2020-12-25", "2020-21 Season - Christmas Games"),
        ("2021-12-25", "2021-22 Season - Christmas Games"),
        ("2022-12-25", "2022-23 Season - Christmas Games"),
        ("2023-12-25", "2023-24 Season - Christmas Games"),
        ("2024-10-22", "2024-25 Season - Opening Week"),
        ("2025-10-22", "2025-26 Season - Opening Week"),
    ]

    results = []

    for game_date, label in test_dates:
        print(f"\n{'-'*80}")
        print(f"{label} - {game_date}")
        print(f"{'-'*80}")

        # Test V2
        try:
            v2 = ScoreboardV2(game_date=game_date, timeout=60)
            v2_games = v2.game_header.get_dict()["data"]
            v2_scores = v2.line_score.get_dict()["data"]
            v2_status = "✓" if len(v2_scores) > 0 or len(v2_games) == 0 else "⚠️"

            print(f"V2: {len(v2_games)} games, {len(v2_scores)} line scores - {v2_status}")
        except Exception as e:
            print(f"V2: ERROR - {e}")
            v2_games = []
            v2_scores = []
            v2_status = "❌"

        # Test V3
        try:
            v3 = ScoreboardV3(game_date=game_date, timeout=60)
            v3_data = v3.get_dict()

            # V3 has a different structure
            if "scoreboard" in v3_data:
                v3_games = v3_data["scoreboard"].get("games", [])
            else:
                v3_games = []

            # Try to get line scores from V3
            v3_line_scores = v3.line_score.get_dict()["data"] if hasattr(v3, 'line_score') else []

            v3_status = "✓" if len(v3_games) > 0 else ("⚠️" if len(v3_games) == 0 else "❌")

            print(f"V3: {len(v3_games)} games, {len(v3_line_scores)} line scores - {v3_status}")

        except Exception as e:
            print(f"V3: ERROR - {str(e)[:100]}")
            v3_games = []
            v3_line_scores = []
            v3_status = "❌"

        results.append({
            "date": game_date,
            "label": label,
            "v2_games": len(v2_games),
            "v2_scores": len(v2_scores),
            "v2_status": v2_status,
            "v3_games": len(v3_games),
            "v3_scores": len(v3_line_scores),
            "v3_status": v3_status
        })

    # Summary
    print("\n" + "="*80)
    print("SUMMARY - Historical Compatibility")
    print("="*80)
    print(f"{'Season':<25} {'V2 Status':<15} {'V3 Status':<15} {'Recommendation'}")
    print("-"*80)

    for r in results:
        season = r['label'].split(' - ')[0]
        v2_desc = f"{r['v2_status']} ({r['v2_games']}g, {r['v2_scores']}s)"
        v3_desc = f"{r['v3_status']} ({r['v3_games']}g, {r['v3_scores']}s)"

        if r['v2_status'] == "✓" and r['v3_status'] == "✓":
            recommendation = "Both work"
        elif r['v2_status'] == "✓" and r['v3_status'] != "✓":
            recommendation = "Use V2 only"
        elif r['v2_status'] != "✓" and r['v3_status'] == "✓":
            recommendation = "Use V3 only"
        else:
            recommendation = "Neither work"

        print(f"{season:<25} {v2_desc:<15} {v3_desc:<15} {recommendation}")

    # Final recommendation
    print("\n" + "="*80)
    print("BACKWARD COMPATIBILITY ANALYSIS")
    print("="*80)

    v3_working = sum(1 for r in results if r['v3_status'] == "✓")
    v3_total = len(results)

    if v3_working == v3_total:
        print("✓ ScoreboardV3 works for ALL tested seasons (100% backward compatible)")
        print("  → Safe to use V3 as the default endpoint")
    elif v3_working >= v3_total * 0.8:
        print(f"⚠️ ScoreboardV3 works for {v3_working}/{v3_total} seasons ({v3_working/v3_total*100:.0f}%)")
        print("  → Mostly backward compatible, but check edge cases")
    else:
        print(f"❌ ScoreboardV3 only works for {v3_working}/{v3_total} seasons ({v3_working/v3_total*100:.0f}%)")
        print("  → NOT backward compatible - stick with V2 for historical data")


if __name__ == "__main__":
    test_historical_seasons()
