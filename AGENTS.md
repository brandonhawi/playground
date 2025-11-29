# Agent Guidelines

This document provides guidance for AI agents working in this repository.

## Repository Structure

```
playground/
├── flagrant_fouls/          # Flagrant fouls impact analysis
│   ├── README.md             # Project overview
│   ├── .gitignore            # Local file exclusions
│   ├── data_collection.ipynb # NBA API data pulls
│   ├── point_differential_analysis.ipynb # Linear regression analysis
│   ├── point_differential_analysis.png    # Saved diagnostics
│   └── nba_flagrant_fouls.csv # Raw data (all seasons)
├── .vscode/                   # VSCode workspace settings
├── pyproject.toml            # Project dependencies (uv-managed)
├── uv.lock                   # Locked dependency versions
└── .python-version           # Python 3.10 specification
```

## Project: Flagrant Fouls Analysis

**Goal:** Quantify the impact of flagrant fouls on NBA game outcomes using statistical modeling.

**Current State:**
- Data: entries covering identifiers with prefixes `0022`, `0032`, `0042`, and `0052` (see `flagrant_fouls/nba_flagrant_fouls.csv` for the latest row count)
- Analysis: `point_differential_analysis.ipynb` fits a linear regression of point differential on flagrant counts
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
- Never modify the schema without updating README.md and whichever notebooks consume the file

## Common Tasks

### Adding a New Season
1. Update the data collection notebook to request the new season_id
2. Append the returned rows to `nba_flagrant_fouls.csv`
3. Re-run `point_differential_analysis.ipynb` so the latest data feeds into the model
4. Refresh the README(s) and mention the new row count/data span

### Adding a New Notebook
1. Follow the structure: Data → Stats → Analysis → Results → Visualization
2. Add description in `README.md`
3. Reference the same CSV file
4. Include power calculation if outcome is binary/continuous

## Git Workflow

This repository follows a **feature-branch development workflow**:

1. **Main branch:** `main` is the stable, production-ready branch
2. **Feature branches:** Create feature branches off `main` with descriptive names:
   - Format: `feat/description`, `fix/description`, `docs/description`, etc.
   - Example: `feat/binary-outcome-analysis`, `fix/data-collection-rate-limit`
3. **Development process:**
   - Create a feature branch from `main`
   - Make commits on the feature branch
   - Push to origin and create a pull request
   - Request review and merge to `main` once approved
4. **Commit messages:**
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
   - Keep messages clear and descriptive
   - Reference GitHub issues when applicable: `Closes #123`
5. **Keep branches up to date:**
   - Before merging, ensure your feature branch is rebased on latest `main`
   - This keeps the git history clean and linear

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
