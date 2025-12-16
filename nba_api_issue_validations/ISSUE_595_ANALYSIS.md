# Issue #595 Analysis: LeagueDashLineups Returns WNBA Data Instead of NBA Data

**GitHub Issue**: https://github.com/swar/nba_api/issues/595

**Status**: ❌ INVALID - Issue cannot be reproduced

## Summary

The reported issue claims that `LeagueDashLineups` returns only WNBA lineup data instead of NBA data. Testing confirms this claim is **incorrect** - the endpoint returns NBA data by default.

## Test Results

### Test Script
`test_issue_595.py` validates the league data returned by the endpoint.

### Findings

1. **Default Parameters Return NBA Data**
   - LeagueID parameter defaults to `'00'` (NBA)
   - Season shows `2025-26` NBA season

2. **Team Validation**
   - Returns data for all 30 NBA teams
   - Team IDs: Range 1610612737-1610612766 (NBA team ID range)
   - Team abbreviations: ATL, BKN, BOS, CHA, CHI, CLE, DAL, DEN, DET, GSW, HOU, IND, LAC, LAL, MEM, MIA, MIL, MIN, NOP, NYK, OKC, ORL, PHI, PHX, POR, SAC, SAS, TOR, UTA, WAS
   - All team IDs match official NBA team IDs

3. **Player Validation**
   - Sample lineups contain current NBA players:
     - R. Gobert, J. Randle, D. DiVincenzo, A. Edwards (Minnesota Timberwolves)
     - G. Antetokounmpo, M. Turner (Milwaukee Bucks)
     - N. Jokić, J. Murray (Denver Nuggets)
     - K. Durant (Phoenix Suns)
   - No WNBA players found in dataset

## Root Cause Analysis

**The issue does not exist.** The endpoint functions as designed:

1. The `LeagueDashLineups` endpoint has a `LeagueID` parameter that defaults to `'00'` (NBA)
2. WNBA would require `LeagueID='10'`, but this parameter is not exposed in the current implementation
3. The NBA.com API backend correctly returns NBA data when LeagueID is set to '00'

## Possible Reasons for Confusion

The issue reporter may have:
1. Misidentified the data source
2. Been testing during WNBA season when NBA was off-season
3. Confused this endpoint with another one that returns WNBA data
4. Made an error in their test code

## Conclusion

**Issue Status**: Invalid - Cannot reproduce

The `LeagueDashLineups` endpoint correctly returns NBA lineup data by default. No fix is needed.

## Test Evidence

Run the validation script:
```bash
cd playground
uv run python3 nba_api_issue_validations/test_issue_595.py
```

Expected output:
- 2000 lineup combinations
- 30 NBA teams
- Current NBA season player names
- LeagueID parameter set to '00' (NBA)
