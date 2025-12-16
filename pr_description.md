# Add Deprecation Warning to ScoreboardV2

Fixes #596

## Problem

`ScoreboardV2` returns **empty line scores** for 2025-26 season games between **Oct 22 - Dec 25, 2025** due to an NBA backend API bug with a date-based cutoff.

## Solution

Add deprecation warning (following `BoxScoreTraditionalV2` pattern) to guide users to `ScoreboardV3`, which:
- ✅ Works for ALL dates (including the broken Oct-Dec range)
- ✅ 100% backward compatible (tested back to 2020-21 season)

## Demo

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/brandonhawi/playground/blob/main/nba_api_issue_validations/issue_596_deprecation_demo.ipynb)

Click to see the deprecation warning in action and verify ScoreboardV3 works correctly.

## Changes

Adds standard library deprecation pattern:
- Module + class docstrings with Sphinx deprecation directive
- Runtime `DeprecationWarning` in `__init__` (stacklevel=2)
- Clear migration example

**Before:**
```python
scoreboard = ScoreboardV2(game_date='2025-10-22')
# Returns 12 games but 0 line scores ❌
```

**After:**
```python
scoreboard = ScoreboardV2(game_date='2025-10-22')
# DeprecationWarning: ...use ScoreboardV3 instead...
# Still returns 0 line scores, but warns user

scoreboard = ScoreboardV3(game_date='2025-10-22')
# Returns 12 games + 24 line scores ✅
```

## Quick Validation

| Endpoint | Oct 22, 2025 | Dec 25, 2025 | Dec 26, 2025 | 2024 Season |
|----------|--------------|--------------|--------------|-------------|
| V2 | 0 scores ⚠️ | 0 scores ⚠️ | ✓ Works | ✓ Works |
| V3 | ✓ Works | ✓ Works | ✓ Works | ✓ Works |

**Finding:** Cutoff at exactly Dec 25-26, 2025. V3 has no issues.

---

**Non-breaking change** - Existing code works, just shows warning.

<details>
<summary>Full analysis (optional)</summary>

- [Bug Analysis](https://github.com/brandonhawi/playground/blob/main/final_bug_analysis.md)
- [Deprecation Pattern](https://github.com/brandonhawi/playground/blob/main/deprecation_pattern_analysis.md)
- [V3 Compatibility Testing](https://github.com/brandonhawi/playground/blob/main/test_v3_historical.py)

</details>
