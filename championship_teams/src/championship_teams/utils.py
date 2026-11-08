from nba_api.stats.endpoints import TeamGameLog
from nba_api.stats.static.teams import find_team_by_abbreviation
from pandas import Series

from championship_teams.types import TeamAbbreviation


def get_team_results_in_time_series(
    abbreviation: TeamAbbreviation, season: str
) -> Series:
    team_id = find_team_by_abbreviation(abbreviation)["id"]
    df = TeamGameLog(
        team_id=team_id,
        season=season,
        season_type_all_star="Regular Season",
    ).get_data_frames()[0]
    return df["W"][::-1]


def get_team_wins_in_first_n_games(
    abbreviation: TeamAbbreviation, season: str, n: int
) -> int:
    team_id = find_team_by_abbreviation(abbreviation)["id"]
    df = TeamGameLog(
        team_id=team_id,
        season=season,
        season_type_all_star="Regular Season",
    ).get_data_frames()[0]
    df = df[::-1].reset_index(drop=True)
    if df["W"].isna().any():
        num_wins = int((df["WL"].head(n) == "W").sum())
    else:
        num_wins = int(df.iloc[n - 1]["W"])
    return num_wins
