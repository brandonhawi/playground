# Covariates Implemented

## Current Model Covariates (Issue #14)
The following covariates have been added to the multivariate regression model:

1. **Rebound differential** - Team rebounds minus opponent rebounds
2. **Assist differential** - Team assists minus opponent assists
3. **Turnover differential** - Opponent turnovers minus team turnovers (higher is better)
4. **Free throw differential** - Team FTM minus opponent FTM
5. **Inactive player differential** - Opponent inactive players minus team inactive (proxy for injuries)
6. **Home/Away status** - Categorical variable for location

## Data Collection
All covariates are automatically extracted from:
- **BoxScoreTraditionalV3** endpoint (rebounds, assists, turnovers, free throws)
- **PlayByPlayV3** endpoint (flagrant fouls, scores)
- Inactive players counted from box score (players with 0 minutes played)

## References
- Sampaio et al., 2015 - Mentions rebounds and assists as key performance indicators