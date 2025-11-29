# Flagrant Fouls Analysis

Statistical workbench focused on how flagrant fouls move the needle on NBA game outcomes.

## Research Focus

What portion of point differential can be attributed to a team's propensity for committing or drawing flagrant fouls? Current work uses a linear regression framework to explore that question.

## Notebooks

### `flagrant_fouls/data_collection.ipynb`
- Pulls play-by-play data from the NBA API (respecting rate limits) and writes structured rows into `nba_flagrant_fouls.csv`.
- Parameterizes the season identifier so new seasons can be added programmatically.

### `flagrant_fouls/point_differential_analysis.ipynb`
- Loads the shared CSV, computes descriptive stats, and fits a linear regression of point differential on the number of flagrant fouls.
- Outputs coefficients, confidence intervals, p-values, model fit metrics (R², adjusted R², AIC/BIC), and computes statistical power.
- Includes diagnostic visuals (scatter, histograms, residual plots) saved to `point_differential_analysis.png`.

## Data

**File:** `nba_flagrant_fouls.csv`

**Structure:**
```
game_id          (str)    - NBA game ID
home_team        (int)    - Home team ID
away_team        (int)    - Away team ID
home_flagrants   (int)    - Number of flagrant fouls committed by home team
away_flagrants   (int)    - Number of flagrant fouls committed by away team
home_score       (int)    - Final home team score
away_score       (int)    - Final away team score
```

**Snapshot:** Games with identifiers prefixed by `0022`, `0032`, `0042`, and `0052` (multiple seasons). Refer to `nba_flagrant_fouls.csv` for the current row count; the file remains one row per game and can be extended without schema changes.

## Running the Analysis

1. **Install dependencies** (from the project root):
   ```bash
   uv sync
   ```

2. **Run notebooks**:
   ```bash
   cd flagrant_fouls
   jupyter notebook  # or lab
   ```

3. **After adding new seasons**:
   - Update the season identifier inside `data_collection.ipynb`.
   - Append fresh rows to `nba_flagrant_fouls.csv`.
   - Re-run `point_differential_analysis.ipynb`.

## Key Deliverables

- Point differential coefficient with confidence interval, significance testing, and explained variance.
- Diagnostic plots to check linearity and residual behavior.
- Statistical power estimate for the current dataset.

## Dependencies

See `../pyproject.toml` for the full dependency list. Key packages:
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `statsmodels` - Statistical modeling & power calculations
- `matplotlib`, `seaborn` - Visualization
- `nba-api` - NBA data retrieval

## Contributing

See [AGENTS.md](../AGENTS.md) for repository conventions and agent-specific guidance.

Open issues document further work.
