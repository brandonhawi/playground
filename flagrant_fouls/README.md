# Flagrant Fouls Analysis

Statistical analysis of the impact of flagrant fouls on game outcomes in NBA basketball.

## Research Question

Does committing a flagrant foul significantly impact a team's probability of winning the game?

## Notebooks

### 1. `flagrant_analysis.ipynb`
Binary logistic regression analysis with win/loss as the outcome variable.

**Output:** Odds ratio showing the multiplicative change in odds of winning when a team commits a flagrant foul.

**Key Statistics:**
- Odds ratio & 95% CI
- P-value & significance test
- Model fit (AIC, BIC, Pseudo R²)
- Statistical power calculation

### 2. `point_differential_analysis.ipynb`
Linear regression analysis with point differential (continuous) as the outcome variable.

**Output:** Regression coefficient showing the change in point differential (in points) when a team commits a flagrant foul.

**Key Statistics:**
- Coefficient & 95% CI
- P-value & significance test
- Model fit (R², Adj. R², F-statistic, AIC, BIC)
- Statistical power calculation
- 4 diagnostic plots (scatter, box plot, histogram, residuals)

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

**Current Data:** 2023-24 season (~600 games)

**Design:** One row per game. Can append additional seasons without schema changes.

## Running the Analysis

1. **Install dependencies** (from project root):
   ```bash
   uv sync
   ```

2. **Open and run notebooks** in Jupyter:
   ```bash
   cd flagrant_fouls
   jupyter notebook
   ```

3. **To extend with new seasons:**
   - Update the data collection notebook to pull additional seasons
   - Append new rows to `nba_flagrant_fouls.csv`
   - Re-run analysis notebooks (they auto-load the CSV)

## Key Findings

Once you run the analysis, you'll get:
- Whether the effect is statistically significant (p < 0.05)
- Effect size (odds ratio or point differential)
- Statistical power of current sample
- Estimated seasons needed for 80% power

## Dependencies

See `../pyproject.toml` for the full dependency list. Key packages:
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `statsmodels` - Statistical modeling & power calculations
- `matplotlib`, `seaborn` - Visualization
- `nba-api` - NBA data retrieval

## Contributing

See [AGENTS.md](../AGENTS.md) for guidance on this repository's structure and conventions for AI agents.

Open issues for tracking development priorities and tasks.
