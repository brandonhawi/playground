# Agent Guidelines

This document provides guidance for AI agents working in this repository.

## Repository Structure

```
playground/
├── flagrant_fouls/          # Flagrant fouls impact analysis
│   ├── README.md           # Project overview
│   ├── .gitignore          # Local file exclusions
│   ├── flagrant_analysis.ipynb              # Binary outcome analysis
│   ├── point_differential_analysis.ipynb    # Continuous outcome analysis
│   └── nba_flagrant_fouls.csv              # Raw data (all seasons)
├── .vscode/                 # VSCode workspace settings
├── pyproject.toml          # Project dependencies (uv-managed)
├── uv.lock                 # Locked dependency versions
└── .python-version         # Python 3.10 specification
```

## Project: Flagrant Fouls Analysis

**Goal:** Quantify the impact of flagrant fouls on NBA game outcomes using statistical modeling.

**Current State:**
- Data: 2023-24 season (~600 games)
- Analysis: Unadjusted logistic and linear regression
- Power: Likely insufficient for 80% statistical power

## Code Style & Standards

### Python
- Use `pandas` for data manipulation
- Use `statsmodels` for statistical modeling
- Follow PEP 8 naming conventions
- Add docstrings to functions

### Notebooks
- **Structure:** Data → Descriptive Stats → Analysis → Results → Visualization
- **Markdown headers:** Use `##` (h2) for sections, `###` (h3) for subsections
- **Output:** Extract key statistics in dedicated cells
- **Plots:** Use `seaborn` for styling consistency, save to PNG at 300 dpi

### Data Files
- Format: CSV (one row per game)
- Location: `flagrant_fouls/nba_flagrant_fouls.csv`
- Schema: `game_id, home_team, away_team, home_flagrants, away_flagrants, home_score, away_score`
- Never modify schema without updating README and both notebooks

## Common Tasks

### Adding a New Season
1. Update data collection code to include new season_id
2. Append new rows to `nba_flagrant_fouls.csv`
3. Re-run both analysis notebooks
4. Update README.md with new data size

### Adding a New Notebook
1. Follow the structure: Data → Stats → Analysis → Results → Visualization
2. Add description in `README.md`
3. Reference the same CSV file
4. Include power calculation if outcome is binary/continuous

### Working with GitHub Issues
- Check open issues before starting work
- Reference issue in commit message: `Closes #123`
- Keep commits atomic and well-documented

## Dependencies

Managed via `uv` (see `pyproject.toml`):
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `statsmodels>=0.14.0` - Statistical modeling
- `matplotlib>=3.7.0` - Plotting
- `seaborn>=0.12.0` - Statistical visualization
- `nba-api>=1.11.3` - NBA data retrieval
- `jupyter>=1.1.1`, `notebook>=7.5.0`, `ipykernel>=7.1.0` - Jupyter environment

Install with: `uv sync`

## Important Notes

1. **API Rate Limiting:** NBA API enforces rate limits. Always include 1+ second sleep between requests.
2. **Data Integrity:** Never hardcode game IDs or season values; parameterize.
3. **Power Calculations:** Always report statistical power when introducing new analyses.
4. **Git:** Use `git mv` for file operations to preserve history.
5. **Commits:** Include `🤖 Generated with Claude Code` footer if created by AI.

## Questions?

Check existing notebooks for examples, or open an issue for discussion.
