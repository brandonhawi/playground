# NBA API Library Fix Options

## Context
The bug exists in the **NBA's backend API**, not the `nba_api` Python library. The library is just a thin wrapper around the NBA Stats API endpoints. However, there are still several options for how the library can handle this.

## Option 1: Smart Wrapper Function (Recommended for Users)

Create a helper function that automatically chooses the correct endpoint.

### Implementation
```python
from datetime import datetime
from nba_api.stats.endpoints import ScoreboardV2, ScoreboardV3

def get_scoreboard(game_date, **kwargs):
    """
    Smart scoreboard function that automatically selects the best endpoint.

    For 2025-26 season games before Dec 26, 2025, uses ScoreboardV3.
    Otherwise uses ScoreboardV2 for backward compatibility.
    """
    # Parse the date
    if isinstance(game_date, str):
        date_obj = datetime.strptime(game_date, "%Y-%m-%d")
    else:
        date_obj = game_date

    # Check if it's in the affected range
    season_start = datetime(2025, 10, 1)
    cutoff_date = datetime(2025, 12, 26)

    if season_start <= date_obj < cutoff_date:
        # Use V3 for affected dates
        return ScoreboardV3(game_date=game_date, **kwargs)
    else:
        # Use V2 for everything else
        return ScoreboardV2(game_date=game_date, **kwargs)
```

**Pros:**
- ✅ Non-invasive, can be user-side code
- ✅ Maintains backward compatibility
- ✅ Easy to implement and test
- ✅ Can be added to the library as a utility function

**Cons:**
- ⚠️ Requires users to change their code
- ⚠️ Hardcoded date logic that might become obsolete

---

## Option 2: Automatic Fallback in ScoreboardV2

Modify `ScoreboardV2` to automatically detect empty line scores and retry with V3.

### Implementation Approach
```python
class ScoreboardV2Enhanced(ScoreboardV2):
    def load_response(self):
        super().load_response()

        # Check if we got games but no line scores (the bug)
        games = self.game_header.get_dict()["data"]
        linescores = self.line_score.get_dict()["data"]

        if len(games) > 0 and len(linescores) == 0:
            # Fallback to V3
            from nba_api.stats.endpoints import ScoreboardV3

            v3 = ScoreboardV3(
                game_date=self.parameters["GameDate"],
                league_id=self.parameters["LeagueID"],
                proxy=self.proxy,
                headers=self.headers,
                timeout=self.timeout
            )

            # Map V3 data to V2 structure
            self._map_v3_to_v2(v3)
```

**Pros:**
- ✅ Transparent to users - no code changes needed
- ✅ Automatically fixes the issue
- ✅ Graceful degradation

**Cons:**
- ❌ Complex - requires mapping V3 data structure to V2 format
- ❌ Extra API call overhead (2 calls instead of 1)
- ❌ May mask future API changes
- ❌ V2 and V3 have different data structures that may not map cleanly

---

## Option 3: Add Deprecation Warning

Add a warning to `ScoreboardV2` when used with affected dates.

### Implementation
```python
import warnings
from datetime import datetime

class ScoreboardV2(Endpoint):
    def __init__(self, game_date=GameDate.default, **kwargs):
        # Check if date is in affected range
        if game_date:
            try:
                date_obj = datetime.strptime(game_date, "%Y-%m-%d")
                if datetime(2025, 10, 1) <= date_obj < datetime(2025, 12, 26):
                    warnings.warn(
                        f"ScoreboardV2 has a known issue with line scores for "
                        f"dates between 2025-10-01 and 2025-12-25. "
                        f"Consider using ScoreboardV3 instead. "
                        f"See: https://github.com/swar/nba_api/issues/596",
                        UserWarning,
                        stacklevel=2
                    )
            except:
                pass

        super().__init__(game_date=game_date, **kwargs)
```

**Pros:**
- ✅ Simple to implement
- ✅ Informs users of the issue
- ✅ Non-breaking change
- ✅ Minimal overhead

**Cons:**
- ⚠️ Users still need to change their code
- ⚠️ Warning fatigue if used frequently

---

## Option 4: Proxy/Adapter Pattern

Create a unified `Scoreboard` class that transparently uses the right endpoint.

### Implementation
```python
class Scoreboard:
    """
    Unified scoreboard interface that automatically selects the best endpoint.
    """
    def __init__(self, game_date, **kwargs):
        self._game_date = game_date
        self._kwargs = kwargs
        self._backend = self._select_backend()

    def _select_backend(self):
        date_obj = datetime.strptime(self._game_date, "%Y-%m-%d")

        if datetime(2025, 10, 1) <= date_obj < datetime(2025, 12, 26):
            return ScoreboardV3(game_date=self._game_date, **self._kwargs)
        else:
            return ScoreboardV2(game_date=self._game_date, **self._kwargs)

    def __getattr__(self, name):
        # Delegate all attribute access to the backend
        return getattr(self._backend, name)
```

**Pros:**
- ✅ Clean API
- ✅ Transparent selection
- ✅ Easy to extend for future issues

**Cons:**
- ⚠️ New class - requires user adoption
- ⚠️ Attribute delegation complexity
- ⚠️ Different V2/V3 APIs may cause issues

---

## Option 5: Documentation Only

Simply document the known issue in the README/docs.

### Implementation
Add to documentation:
```markdown
## Known Issues

### ScoreboardV2 - 2025-26 Season Line Scores (Issue #596)

ScoreboardV2 does not return line score data for 2025-26 regular season
games between October 22, 2025 and December 25, 2025.

**Workaround:** Use `ScoreboardV3` instead for this date range.

**Example:**
```python
# Instead of:
scoreboard = ScoreboardV2(game_date='2025-10-22')

# Use:
scoreboard = ScoreboardV3(game_date='2025-10-22')
```

**Status:** This is a backend NBA API issue, not a library bug.
```

**Pros:**
- ✅ No code changes needed
- ✅ Zero overhead
- ✅ Accurate representation (it's an NBA API bug)

**Cons:**
- ❌ Doesn't help users who don't read docs
- ❌ Manual workaround required
- ❌ Users will still file bugs

---

## Option 6: Fork/Patch Approach

Create a patched version of the library with fixes.

**Pros:**
- ✅ Can implement any fix immediately
- ✅ Full control

**Cons:**
- ❌ Maintenance burden
- ❌ Divergence from upstream
- ❌ Not a sustainable solution

---

## Recommendation Matrix

| Option | Effort | User Impact | Maintainability | Recommended For |
|--------|--------|-------------|-----------------|-----------------|
| #1 Smart Wrapper | Low | Medium | High | **End Users** (quick fix) |
| #2 Auto Fallback | High | Low | Low | Not recommended |
| #3 Deprecation Warning | Low | Medium | High | **Library maintainers** (interim) |
| #4 Proxy Pattern | Medium | Low | Medium | Future library design |
| #5 Documentation | Very Low | High | High | **Minimum viable** |
| #6 Fork | High | Low | Very Low | Not recommended |

---

## Best Path Forward

### For End Users (Now)
**Use Option #1** - Create a helper function in your own codebase:
```python
def get_scoreboard_safe(game_date, **kwargs):
    # Use V3 for early 2025 season, V2 otherwise
    from datetime import datetime
    date = datetime.strptime(game_date, "%Y-%m-%d")

    if datetime(2025, 10, 1) <= date < datetime(2025, 12, 26):
        from nba_api.stats.endpoints import ScoreboardV3
        return ScoreboardV3(game_date=game_date, **kwargs)
    else:
        from nba_api.stats.endpoints import ScoreboardV2
        return ScoreboardV2(game_date=game_date, **kwargs)
```

### For Library Maintainers (Short-term)
**Combine Options #3 + #5**:
1. Add deprecation warning to ScoreboardV2 for affected dates
2. Document the issue and workaround in README
3. Optionally add Option #1 as a utility function

### For Library Maintainers (Long-term)
**Consider Option #4** for next major version:
- Design a unified `Scoreboard` interface
- Abstract away V2/V3 differences
- Handle version selection internally

---

## Example PR for nba_api

```python
# In nba_api/stats/endpoints/scoreboardv2.py

def __init__(self, ...):
    # Add warning for affected dates
    if game_date:
        try:
            date_obj = datetime.strptime(game_date, "%Y-%m-%d")
            if datetime(2025, 10, 1) <= date_obj < datetime(2025, 12, 26):
                warnings.warn(
                    "ScoreboardV2 may return empty line scores for this date range. "
                    "See https://github.com/swar/nba_api/issues/596 for details. "
                    "Consider using ScoreboardV3 as a workaround.",
                    UserWarning,
                    stacklevel=2
                )
        except ValueError:
            pass  # Invalid date format, let it fail later

    # ... rest of existing code
```

```python
# In nba_api/stats/utils.py (new file)

def get_scoreboard(game_date, **kwargs):
    """
    Get scoreboard data with automatic endpoint selection.

    This function automatically selects ScoreboardV3 for dates affected by
    the line score bug (2025-10-22 to 2025-12-25) and ScoreboardV2 otherwise.

    Args:
        game_date (str): Game date in YYYY-MM-DD format
        **kwargs: Additional arguments passed to the scoreboard endpoint

    Returns:
        ScoreboardV2 or ScoreboardV3 instance

    Example:
        >>> scoreboard = get_scoreboard('2025-10-22')
        >>> games = scoreboard.game_header.get_dict()
    """
    from datetime import datetime
    from nba_api.stats.endpoints import ScoreboardV2, ScoreboardV3

    try:
        date_obj = datetime.strptime(game_date, "%Y-%m-%d")
        if datetime(2025, 10, 1) <= date_obj < datetime(2025, 12, 26):
            return ScoreboardV3(game_date=game_date, **kwargs)
    except ValueError:
        pass

    return ScoreboardV2(game_date=game_date, **kwargs)
```
