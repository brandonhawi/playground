# Agent Guidelines

This document provides guidance for AI agents working in this repository.

## Repository Structure

```
playground/
├── ballhog/                  # Player selfishness analysis ("ballhog" metrics)
│   ├── README.md             # Project overview and metric definitions
│   ├── build_leaderboard.py  # CLI to generate selfishness scores
│   ├── selfishness_analysis.ipynb # Visualizations and analysis
│   └── ballhog_metrics.csv   # Raw data (all seasons)
├── flagrant_fouls/           # Flagrant fouls impact analysis
│   ├── README.md             # Project overview
│   ├── data_collection.ipynb # NBA API data pulls
│   ├── point_differential_analysis.ipynb # Linear regression analysis
│   ├── nba_flagrant_fouls.csv # Raw data (all seasons)
│   └── nba_skipped_games.csv  # Games with no play-by-play data
├── nba_api_issue_validations/ # Notebooks to validate nba-api issues
│   ├── README.md             # Project overview
│   ├── issue_*.ipynb         # Notebooks reproducing/validating issues
│   └── test_*.py             # Python scripts for validation
├── .vscode/                  # VSCode workspace settings
├── pyproject.toml            # Project dependencies (uv-managed)
├── uv.lock                   # Locked dependency versions
└── .python-version           # Python 3.10 specification
```

## Project: Flagrant Fouls Analysis

**Goal:** Quantify the impact of flagrant fouls on NBA game outcomes using statistical modeling.

**Current State:**
- Data: entries covering identifiers with prefixes `0012`, `0022`, `0032`, `0042`, and `0052` (see `flagrant_fouls/nba_flagrant_fouls.csv` for the latest row count)
- Analysis: `point_differential_analysis.ipynb` fits a linear regression of point differential on flagrant counts
- Power: Likely insufficient for 80% statistical power

## Project: Ballhog Analysis

**Goal:** Measure player selfishness by analyzing possession dominance versus facilitation for teammates.

**Contents:**
- `build_leaderboard.py`: CLI tool to compute and rank players by various "selfishness" metrics.
- `selfishness_analysis.ipynb`: Detailed analysis, visualizations, and distributions of the metrics.
- `ballhog_metrics.csv`: The output data containing per-player-season selfishness scores.

## Project: NBA API Issue Validations

**Goal:** Provide executable notebooks to reproduce and validate bug fixes for the `nba_api` library.

**Contents:**
- Each `issue_*.ipynb` notebook corresponds to a specific GitHub issue, demonstrating the bug or validating a fix.
- Notebooks are designed to be run in Google Colab for easy, zero-setup verification.

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

## Definition of Done

Before considering any task complete, ensure ALL of the following criteria are met:

1. **Code Quality**
   - Code follows PEP 8 naming conventions
   - Functions have docstrings where appropriate
   - No hardcoded values; use parameterization
   - No security vulnerabilities introduced

2. **Testing & Validation**
   - Code runs without errors
   - Statistical analyses include power calculations
   - Results are reproducible
   - Outputs match expected formats

3. **Documentation**
   - All README files are updated to reflect changes
   - AGENTS.md is updated if workflow or structure changes
   - Schema documentation matches actual data structure
   - New files or notebooks are documented in appropriate README files
   - Code comments explain non-obvious logic

4. **Data Integrity**
   - CSV schema remains consistent (or documented if changed)
   - No data corruption or loss
   - Data quality issues are documented
   - File references in documentation are accurate

5. **Git & Version Control**
   - Commits follow conventional commit format
   - Commit messages are clear and descriptive
   - Changes are on appropriate feature branch
   - No sensitive data (credentials, tokens) committed

6. **Dependencies**
   - New dependencies added to `pyproject.toml`
   - `uv.lock` updated if dependencies change
   - All code runs via `uv run` commands

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

### Running Python Commands

**IMPORTANT:** Always run Python commands through `uv` to ensure correct environment:

```bash
# Run Python scripts
uv run python3 script.py

# Run Python commands
uv run python3 -c "import pandas; print(pandas.__version__)"

# Execute Jupyter notebooks
uv run jupyter nbconvert --to notebook --execute notebook.ipynb
```

**DO NOT** use system Python directly (`python3 script.py`) - this will not have access to project dependencies.

## Important Notes

1. **API Rate Limiting:** NBA API enforces rate limits. Always include 0.6 second sleep between requests (600ms).
2. **Game ID Format:** NBA API requires game IDs as 10-digit strings with leading zeros (e.g., `'0022000605'`). Never convert to integers.
3. **Data Integrity:** Never hardcode game IDs or season values; parameterize.
4. **Power Calculations:** Always report statistical power when introducing new analyses.
5. **Git:** Use `git mv` for file operations to preserve history.
6. **Commits:** Include `🤖 Generated with Claude Code` footer if created by AI.

## Questions?

Check existing notebooks for examples, or open an issue for discussion.
