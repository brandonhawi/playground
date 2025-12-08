"""
Proposed deprecation for ScoreboardV2 following nba_api library patterns

This follows the EXACT pattern used for BoxScoreTraditionalV2 deprecation
in the nba_api library (see boxscoretraditionalv2.py lines 1-154)
"""

import warnings
from nba_api.stats.endpoints._base import Endpoint
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.library.parameters import DayOffset, GameDate, LeagueID


class ScoreboardV2Deprecated(Endpoint):
    """
    ScoreboardV2 endpoint.

    .. deprecated:: 2025-26
        **DEPRECATION WARNING:** This endpoint has known issues with line score data
        for games between 2025-10-22 and 2025-12-25 (returns empty line scores).
        Please use :class:`~nba_api.stats.endpoints.ScoreboardV3` instead.
        ScoreboardV3 is fully backward compatible and works for all historical seasons.

    Known Issue:
        For 2025-26 season games between October 22, 2025 and December 25, 2025,
        the line_score dataset returns an empty array despite games being available.
        This is an NBA backend API issue. See: https://github.com/swar/nba_api/issues/596

    Recommendation:
        Use ScoreboardV3 for all scoreboard queries. It is 100% backward compatible
        with historical data (tested back to 2020-21 season) and does not have the
        line score bug.

    Args:
        day_offset (int, optional): Day offset from game_date.
        game_date (str, optional): Game date in YYYY-MM-DD format.
        league_id (str, optional): League ID ('00' for NBA). Defaults to LeagueID.default.
        proxy (str, optional): HTTP/HTTPS proxy for requests.
        headers (dict, optional): Custom HTTP headers.
        timeout (int, optional): Request timeout in seconds. Defaults to 30.
        get_request (bool, optional): Whether to fetch data immediately. Defaults to True.

    Example:
        >>> # Instead of this (deprecated):
        >>> from nba_api.stats.endpoints import ScoreboardV2
        >>> scoreboard = ScoreboardV2(game_date='2025-10-22')
        >>>
        >>> # Use this:
        >>> from nba_api.stats.endpoints import ScoreboardV3
        >>> scoreboard = ScoreboardV3(game_date='2025-10-22')
    """
    endpoint = "scoreboardv2"
    expected_data = {
        "Available": ["GAME_ID", "PT_AVAILABLE"],
        "GameHeader": [
            "GAME_DATE_EST",
            "GAME_SEQUENCE",
            "GAME_ID",
            "GAME_STATUS_ID",
            "GAME_STATUS_TEXT",
            "GAMECODE",
            "HOME_TEAM_ID",
            "VISITOR_TEAM_ID",
            "SEASON",
            "LIVE_PERIOD",
            "LIVE_PC_TIME",
            "NATL_TV_BROADCASTER_ABBREVIATION",
            "HOME_TV_BROADCASTER_ABBREVIATION",
            "AWAY_TV_BROADCASTER_ABBREVIATION",
            "LIVE_PERIOD_TIME_BCAST",
            "ARENA_NAME",
            "WH_STATUS",
        ],
        "LineScore": [
            "GAME_DATE_EST",
            "GAME_SEQUENCE",
            "GAME_ID",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "TEAM_CITY_NAME",
            "TEAM_NAME",
            "TEAM_WINS_LOSSES",
            "PTS_QTR1",
            "PTS_QTR2",
            "PTS_QTR3",
            "PTS_QTR4",
            "PTS_OT1",
            "PTS_OT2",
            "PTS_OT3",
            "PTS_OT4",
            "PTS_OT5",
            "PTS_OT6",
            "PTS_OT7",
            "PTS_OT8",
            "PTS_OT9",
            "PTS_OT10",
            "PTS",
            "FG_PCT",
            "FT_PCT",
            "FG3_PCT",
            "AST",
            "REB",
            "TOV",
        ],
        # ... other datasets omitted for brevity
    }

    nba_response = None
    data_sets = None
    player_stats = None
    team_stats = None
    headers = None

    def __init__(
        self,
        day_offset=DayOffset.default,
        game_date=GameDate.default,
        league_id=LeagueID.default,
        proxy=None,
        headers=None,
        timeout=30,
        get_request=True,
    ):
        # DEPRECATION WARNING - Following library pattern from BoxScoreTraditionalV2
        warnings.warn(
            "ScoreboardV2 has known issues with line score data for 2025-26 season games "
            "(October 22 - December 25, 2025). Please use ScoreboardV3 instead. "
            "ScoreboardV3 is fully backward compatible and works for all historical seasons. "
            "See: https://github.com/swar/nba_api/issues/596",
            DeprecationWarning,
            stacklevel=2
        )

        self.proxy = proxy
        if headers is not None:
            self.headers = headers
        self.timeout = timeout
        self.parameters = {
            "DayOffset": day_offset,
            "GameDate": game_date,
            "LeagueID": league_id,
        }
        if get_request:
            self.get_request()

    def get_request(self):
        self.nba_response = NBAStatsHTTP().send_api_request(
            endpoint=self.endpoint,
            parameters=self.parameters,
            proxy=self.proxy,
            headers=self.headers,
            timeout=self.timeout,
        )
        self.load_response()

    def load_response(self):
        data_sets = self.nba_response.get_data_sets()
        self.data_sets = [
            Endpoint.DataSet(data=data_set)
            for data_set_name, data_set in data_sets.items()
        ]
        self.available = Endpoint.DataSet(data=data_sets["Available"])
        self.east_conf_standings_by_day = Endpoint.DataSet(
            data=data_sets["EastConfStandingsByDay"]
        )
        self.game_header = Endpoint.DataSet(data=data_sets["GameHeader"])
        self.last_meeting = Endpoint.DataSet(data=data_sets["LastMeeting"])
        self.line_score = Endpoint.DataSet(data=data_sets["LineScore"])
        # ... rest of datasets


# DEMONSTRATION: Test the deprecation warning
if __name__ == "__main__":
    print("="*80)
    print("TESTING DEPRECATION WARNING")
    print("="*80)
    print("\nThis demonstrates the deprecation pattern used in nba_api library")
    print("Pattern source: BoxScoreTraditionalV2 (boxscoretraditionalv2.py:149-155)\n")

    print("Attempting to use ScoreboardV2Deprecated with game_date='2025-10-22'...\n")

    # This will trigger the deprecation warning
    try:
        scoreboard = ScoreboardV2Deprecated(game_date='2025-10-22', timeout=60)
        print("✓ Endpoint created successfully (with deprecation warning above)")
    except Exception as e:
        print(f"Error: {e}")
