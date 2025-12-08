"""
Smart Scoreboard Wrapper - Production-Ready Solution
Automatically handles the ScoreboardV2 line score bug for 2025-26 season
"""

from datetime import datetime
from typing import Optional
import warnings


def get_scoreboard(
    game_date: str,
    day_offset: int = 0,
    league_id: str = "00",
    proxy: Optional[str] = None,
    headers: Optional[dict] = None,
    timeout: int = 30,
    force_v3: bool = False
):
    """
    Get scoreboard data with automatic endpoint selection.

    Automatically uses ScoreboardV3 for dates affected by the line score bug
    (2025-10-22 to 2025-12-25) and ScoreboardV2 for everything else.

    Args:
        game_date: Game date in YYYY-MM-DD format
        day_offset: Day offset from game_date (ScoreboardV2 only)
        league_id: League ID ('00' for NBA)
        proxy: HTTP/HTTPS proxy for requests
        headers: Custom HTTP headers
        timeout: Request timeout in seconds
        force_v3: Force use of ScoreboardV3 regardless of date

    Returns:
        ScoreboardV2 or ScoreboardV3 instance with unified interface

    Example:
        >>> # Automatically uses V3 for affected dates
        >>> scoreboard = get_scoreboard('2025-10-22')
        >>> games = scoreboard.game_header.get_dict()
        >>> scores = scoreboard.line_score.get_dict()

        >>> # Works normally for other dates
        >>> scoreboard = get_scoreboard('2024-10-22')
        >>> games = scoreboard.game_header.get_dict()
    """
    from nba_api.stats.endpoints import ScoreboardV2, ScoreboardV3

    use_v3 = force_v3

    if not force_v3:
        try:
            date_obj = datetime.strptime(game_date, "%Y-%m-%d")

            # Check if date is in the affected range
            affected_start = datetime(2025, 10, 1)
            affected_end = datetime(2025, 12, 26)

            if affected_start <= date_obj < affected_end:
                use_v3 = True
                warnings.warn(
                    f"Date {game_date} is in the affected range for ScoreboardV2 "
                    f"line score bug. Automatically using ScoreboardV3. "
                    f"See: https://github.com/swar/nba_api/issues/596",
                    UserWarning,
                    stacklevel=2
                )
        except ValueError:
            # Invalid date format - let it fail in the endpoint
            pass

    if use_v3:
        return ScoreboardV3(
            game_date=game_date,
            league_id=league_id,
            proxy=proxy,
            headers=headers,
            timeout=timeout
        )
    else:
        return ScoreboardV2(
            game_date=game_date,
            day_offset=day_offset,
            league_id=league_id,
            proxy=proxy,
            headers=headers,
            timeout=timeout
        )


def validate_scoreboard_fix():
    """Test the wrapper to ensure it works correctly"""
    print("="*80)
    print("VALIDATING SCOREBOARD WRAPPER")
    print("="*80)

    test_cases = [
        ("2024-10-22", "2024 season (should use V2)"),
        ("2025-10-22", "2025 affected date (should use V3)"),
        ("2025-12-25", "Christmas 2025 (should use V3)"),
        ("2025-12-26", "Dec 26 2025 (should use V2)"),
        ("2026-01-15", "Jan 2026 (should use V2)"),
    ]

    for game_date, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"Date: {game_date}")

        try:
            scoreboard = get_scoreboard(game_date, timeout=60)
            endpoint_type = type(scoreboard).__name__

            games = scoreboard.game_header.get_dict()["data"]
            linescores = scoreboard.line_score.get_dict()["data"]

            print(f"  Endpoint: {endpoint_type}")
            print(f"  Games: {len(games)}")
            print(f"  Line scores: {len(linescores)}")

            if len(games) > 0 and len(linescores) == 0:
                print(f"  Status: ⚠️ STILL HAS ISSUE")
            elif len(games) > 0:
                print(f"  Status: ✓ WORKING")
            else:
                print(f"  Status: - No games")

        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    validate_scoreboard_fix()
