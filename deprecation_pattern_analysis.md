# nba_api Deprecation Pattern Analysis

## Discovery

**YES!** The library has an established deprecation pattern used for BoxScoreTraditionalV2 and other V2 endpoints being replaced by V3.

## Existing Pattern (from BoxScoreTraditionalV2)

### 1. Module Docstring
```python
"""
BoxScoreTraditionalV2 endpoint.

.. deprecated:: 2025-26
    This endpoint is deprecated. Please use BoxScoreTraditionalV3 instead.
    Data is no longer being published for BoxScoreTraditionalV2 as of the 2025-26 NBA season.
"""
```

### 2. Import warnings
```python
import warnings
```

### 3. Class Docstring with Sphinx Directive
```python
class BoxScoreTraditionalV2(Endpoint):
    """
    BoxScoreTraditionalV2 endpoint.

    .. deprecated:: 2025-26
        **DEPRECATION WARNING:** This endpoint is deprecated.
        Please use :class:`~nba_api.stats.endpoints.BoxScoreTraditionalV3` instead.
        Data is no longer being published for BoxScoreTraditionalV2 as of the 2025-26 NBA season.
    """
```

### 4. Runtime Warning in __init__
```python
def __init__(self, ...):
    warnings.warn(
        "BoxScoreTraditionalV2 is deprecated and will be removed in a future version. "
        "Please use BoxScoreTraditionalV3 instead. "
        "Data is no longer being published for BoxScoreTraditionalV2 as of the 2025-26 NBA season.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... rest of __init__
```

## Pattern Elements

| Element | Purpose | Example |
|---------|---------|---------|
| Module docstring | Documentation, shows in IDE | `.. deprecated:: 2025-26` |
| Class docstring | API reference, Sphinx docs | `:class:~nba_api.stats.endpoints.V3` |
| Runtime warning | Alerts developers at runtime | `warnings.warn(..., DeprecationWarning)` |
| stacklevel=2 | Points to caller's code | Shows warning at user's code line |

## Other Deprecated Endpoints Found

Looking at the library, many V2 endpoints have V3 replacements:

- BoxScoreAdvancedV2 → BoxScoreAdvancedV3
- BoxScoreTraditionalV2 → BoxScoreTraditionalV3 ✓ (has deprecation)
- BoxScoreFourFactorsV2 → BoxScoreFourFactorsV3
- BoxScoreMiscV2 → BoxScoreMiscV3
- BoxScoreScoringV2 → BoxScoreScoringV3
- BoxScoreSummaryV2 → BoxScoreSummaryV3
- BoxScoreUsageV2 → BoxScoreUsageV3
- **ScoreboardV2 → ScoreboardV3** ← Our case

## Proposed Implementation for ScoreboardV2

### File: `scoreboardv2.py`

```python
"""
ScoreboardV2 endpoint for NBA daily game schedule and scores.

.. deprecated:: 2025-26
    This endpoint has known issues with line score data for games between
    2025-10-22 and 2025-12-25. Please use ScoreboardV3 instead.
    ScoreboardV3 is fully backward compatible with all historical seasons.
"""
import warnings

from nba_api.stats.endpoints._base import Endpoint
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.library.parameters import DayOffset, GameDate, LeagueID


class ScoreboardV2(Endpoint):
    """
    ScoreboardV2 endpoint.

    .. deprecated:: 2025-26
        **DEPRECATION WARNING:** This endpoint has known issues with line score data.
        Please use :class:`~nba_api.stats.endpoints.ScoreboardV3` instead.

        For 2025-26 season games between October 22, 2025 and December 25, 2025,
        the line_score dataset returns empty despite games being available.

        ScoreboardV3 is fully backward compatible and resolves this issue.
        See: https://github.com/swar/nba_api/issues/596

    Args:
        day_offset (int, optional): Day offset from game_date.
        game_date (str, optional): Game date in YYYY-MM-DD format.
        league_id (str, optional): League ID ('00' for NBA).
        proxy (str, optional): HTTP/HTTPS proxy for requests.
        headers (dict, optional): Custom HTTP headers.
        timeout (int, optional): Request timeout in seconds. Defaults to 30.
        get_request (bool, optional): Whether to fetch data immediately. Defaults to True.

    Example:
        >>> # Deprecated (has issues with 2025 early season):
        >>> from nba_api.stats.endpoints import ScoreboardV2
        >>> scoreboard = ScoreboardV2(game_date='2025-10-22')
        >>>
        >>> # Recommended (works for all seasons):
        >>> from nba_api.stats.endpoints import ScoreboardV3
        >>> scoreboard = ScoreboardV3(game_date='2025-10-22')
    """

    # ... existing class code ...

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
        warnings.warn(
            "ScoreboardV2 has known issues with line score data for 2025-26 season games "
            "(October 22 - December 25, 2025). Please use ScoreboardV3 instead. "
            "ScoreboardV3 is fully backward compatible and works for all historical seasons. "
            "See: https://github.com/swar/nba_api/issues/596",
            DeprecationWarning,
            stacklevel=2
        )

        # ... existing __init__ code ...
```

## Why This Pattern Works

1. **Progressive Disclosure**
   - Documentation warns at read-time
   - Warning fires at run-time
   - Users see it at both stages

2. **Non-Breaking**
   - Code still works (just warns)
   - Users can migrate on their schedule
   - No immediate production breaks

3. **Clear Migration Path**
   - Explicit recommendation: "Use ScoreboardV3"
   - Links to issue for context
   - Example code provided

4. **Standard Python Convention**
   - Uses DeprecationWarning (standard)
   - stacklevel=2 points to user code
   - Follows PEP 565 guidelines

## Comparison with Our Options

| Approach | Matches Pattern | Breaking Change | User Visible |
|----------|----------------|-----------------|--------------|
| Documentation only | Partial | No | Low visibility |
| Runtime warning | ✓ Yes | No | High visibility |
| Smart wrapper | No (new pattern) | No | Transparent |
| Auto-fallback | No | No | Hidden |
| Proxy pattern | No | Yes (new API) | Requires adoption |

## Recommendation for nba_api PR

**Use the existing deprecation pattern** (Option from previous analysis):

### Changes Required

1. **scoreboardv2.py** - Add deprecation warning (minimal change)
   - Add module docstring deprecation notice
   - Update class docstring with Sphinx directive
   - Add `warnings.warn()` in `__init__`

2. **Optional: Add utility function** in new file `stats/utils.py`:
   ```python
   def get_scoreboard(game_date, **kwargs):
       """Smart wrapper that uses V3 (recommended for new code)"""
       from nba_api.stats.endpoints import ScoreboardV3
       return ScoreboardV3(game_date=game_date, **kwargs)
   ```

3. **README.md** - Add known issues section
   ```markdown
   ## Known Issues

   ### ScoreboardV2 Line Score Bug (2025-26 Season)
   ScoreboardV2 returns empty line scores for games between Oct 22 - Dec 25, 2025.

   **Solution:** Use ScoreboardV3 instead (100% backward compatible).

   See [Issue #596](https://github.com/swar/nba_api/issues/596)
   ```

### Timeline

- **v1.11.4** (next patch): Add deprecation warnings
- **v1.12.0** (next minor): Add utility function (optional)
- **v2.0.0** (future major): Remove ScoreboardV2 entirely

## Files in This Investigation

- `scoreboard_v2_deprecation_proposal.py` - Full implementation example
- `deprecation_pattern_analysis.md` - This document
- `library_fix_options.md` - All solution options compared
- `final_bug_analysis.md` - Complete bug report
- `test_v3_historical.py` - V3 backward compatibility proof

## Next Steps

1. Create GitHub issue in swar/nba_api with findings
2. Submit PR with deprecation warnings following this pattern
3. Reference issue #596 in the PR
4. Include test results showing V3 compatibility
