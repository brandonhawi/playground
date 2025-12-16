"""
Test script to validate nba_api issue #595
Issue: LeagueDashLineups returns WNBA data instead of NBA data
GitHub: https://github.com/swar/nba_api/issues/595
"""

from nba_api.stats.endpoints import leaguedashlineups
import pandas as pd

def test_leaguedashlineups():
    print("=" * 80)
    print("Testing LeagueDashLineups endpoint")
    print("=" * 80)

    # Test 1: Default parameters (should return NBA data)
    print("\n1. Testing with default parameters:")
    print("-" * 80)
    try:
        ldsh = leaguedashlineups.LeagueDashLineups()
        df = ldsh.get_data_frames()[0]

        print(f"Number of rows returned: {len(df)}")
        print(f"\nColumns: {list(df.columns)}")

        # Check if we can identify the league from the data
        if 'GROUP_NAME' in df.columns:
            print(f"\nSample lineups (first 10):")
            print(df['GROUP_NAME'].head(10).to_string())

        # Check team IDs to determine if NBA or WNBA
        if 'TEAM_ID' in df.columns:
            team_ids = df['TEAM_ID'].unique()
            print(f"\nUnique TEAM_IDs: {team_ids[:10]}")  # Show first 10
            print(f"Total unique teams: {len(team_ids)}")

            # NBA team IDs are typically 10 digits starting with 161
            # WNBA team IDs are typically 10 digits starting with 161 but different range
            # Let's check the range
            if len(team_ids) > 0:
                print(f"Sample TEAM_ID: {team_ids[0]}")

        if 'TEAM_ABBREVIATION' in df.columns:
            team_abbrevs = df['TEAM_ABBREVIATION'].unique()
            print(f"\nTeam abbreviations: {sorted(team_abbrevs)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Check available parameters
    print("\n\n2. Inspecting available parameters:")
    print("-" * 80)
    ldsh_inspect = leaguedashlineups.LeagueDashLineups()
    if hasattr(ldsh_inspect, 'parameters'):
        print(f"Available parameters:")
        for key, value in ldsh_inspect.parameters.items():
            print(f"  {key}: {value}")

    # Test 3: Verify this is NBA data by checking team IDs
    print("\n\n3. Validating this is NBA (not WNBA) data:")
    print("-" * 80)

    # NBA team IDs are in the 1610612000 range
    # WNBA team IDs are in the 1611661000 range
    nba_teams = {
        1610612737: 'ATL', 1610612738: 'BOS', 1610612751: 'BKN',
        1610612766: 'CHA', 1610612741: 'CHI', 1610612739: 'CLE',
        1610612742: 'DAL', 1610612743: 'DEN', 1610612765: 'DET',
        1610612744: 'GSW', 1610612745: 'HOU', 1610612754: 'IND',
        1610612746: 'LAC', 1610612747: 'LAL', 1610612763: 'MEM',
        1610612748: 'MIA', 1610612749: 'MIL', 1610612750: 'MIN',
        1610612740: 'NOP', 1610612752: 'NYK', 1610612760: 'OKC',
        1610612753: 'ORL', 1610612755: 'PHI', 1610612756: 'PHX',
        1610612757: 'POR', 1610612758: 'SAC', 1610612759: 'SAS',
        1610612761: 'TOR', 1610612762: 'UTA', 1610612764: 'WAS'
    }

    if 'TEAM_ID' in df.columns:
        returned_team_ids = set(df['TEAM_ID'].unique())
        nba_team_ids = set(nba_teams.keys())

        matches_nba = returned_team_ids.issubset(nba_team_ids)
        print(f"All team IDs match NBA teams: {matches_nba}")
        print(f"Number of NBA team IDs found: {len(returned_team_ids)}")

        if not matches_nba:
            unknown_ids = returned_team_ids - nba_team_ids
            print(f"Unknown team IDs (possibly WNBA): {unknown_ids}")

    # Test 4: Cross-reference player names
    print("\n\n4. Checking player names to confirm NBA:")
    print("-" * 80)
    if 'GROUP_NAME' in df.columns:
        # Sample a few lineups and check if players are NBA players
        sample_lineups = df['GROUP_NAME'].head(5).tolist()
        print("Sample lineups to verify:")
        for i, lineup in enumerate(sample_lineups, 1):
            print(f"  {i}. {lineup}")
        print("\nNote: These should be recognizable NBA players from 2024-25 season")

    print("\n" + "=" * 80)
    print("Test complete")
    print("=" * 80)

if __name__ == "__main__":
    test_leaguedashlineups()
