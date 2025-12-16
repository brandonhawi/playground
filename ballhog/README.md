# Ballhog Analysis

This folder holds a sister workflow to `flagrant_fouls/` that focuses on measuring player selfishness in basketball - specifically identifying players who dominate possessions for their own scoring rather than facilitating for teammates.

## Contents

- `build_leaderboard.py` – CLI helper that calls `LeagueDashPlayerStats` (Base and Advanced measure types) and `LeagueDashTeamStats` to compute selfishness metrics for all players.
- `selfishness_analysis.ipynb` – Interactive Jupyter notebook with visualizations, distributions, and detailed analysis of player selfishness. **Start here for an accessible introduction to the metrics!**
- `ballhog_metrics.csv` – one row per player-season capturing individual stats, team totals, and all computed selfishness metrics.

## Planned Future Work

- `data_collection.ipynb` – pull season game IDs (`LeagueGameFinder`) and per-game box scores from `BoxScoreTraditionalV3` / `BoxScoreAdvancedV2` for game-level analysis.
- `point_differential_analysis.ipynb` – reuse the modeling pattern in `flagrant_fouls/point_differential_analysis.ipynb`, now with ballhog features alongside flagrant counts.

## Selfishness Metrics

We calculate multiple metrics to identify the most selfish players in the NBA:

### 1. Selfishness Score (Primary Metric)

A composite metric combining usage, assist rate, and shot creation:

$$
\text{Selfishness Score} = (\text{USG%} \times 100) \times 0.4 + \left(1 - \frac{\text{AST%}}{100}\right) \times 100 \times 0.4 + (\text{Shot Load} \times 100) \times 0.2
$$

**Components:**

- **40% weight on Usage Rate** - How much they dominate possessions
- **40% weight on Low Assists** - How little they create for teammates
- **20% weight on Shot Creation Load** - How shot-heavy their usage is

**Scale:** 0-100, where higher = more selfish

### 2. Self-Creation Index (Original "Kobe Quotient")

Usage rate adjusted down by assist percentage:

$$
\text{Self-Creation Index} = \left( \frac{FGA + 0.44 \times FTA + TOV}{\text{Team FGA} + 0.44 \times \text{Team FTA} + \text{Team TOV}} \right) \times \left(1 - \frac{AST_{PCT}}{100}\right)
$$

- High-usage players with low assist percentages rank highest
- Measures possession usage specifically for self-scoring (excludes playmaking)

### 3. Assist-to-Usage Ratio

$$
\text{AST-to-USG Ratio} = \frac{\text{AST%} / 100}{\text{USG%}}
$$

- **Lower ratio = more selfish** (high usage, few assists)
- Recommended by Cleaning the Glass analytics<sup>[1](#ref1)</sup>
- Fixes the problem that high-usage players naturally have higher assist percentages

### 4. Standard Usage Rate (USG%)

$$
\text{USG%} = \frac{FGA + 0.44 \times FTA + TOV}{\text{Team FGA} + 0.44 \times \text{Team FTA} + \text{Team TOV}}
$$

- The foundational possession usage formula from Dean Oliver's "Basketball on Paper"<sup>[2](#ref2)</sup>
- Estimates percentage of team possessions a player uses
- Does NOT account for playmaking (assists don't reduce usage)

## Why These Formulas?

### The 0.44 Coefficient

The **0.44 multiplier for free throw attempts** comes from empirical analysis of NBA play-by-play data from 2003-06<sup>[3](#ref3)</sup>. It represents the proportion of **possession-ending free throws**:

- Not all FTAs end possessions (and-1s, multi-shot sequences, offensive rebounds on misses)
- Empirically, approximately 44% of free throw attempts correspond to unique possessions
- Some analysts use 0.46 or 0.475 (especially in college basketball)<sup>[4](#ref4)</sup>
- **Note:** Recent research (2023) suggests this value may need updating for modern NBA basketball due to changing shooting profiles<sup>[5](#ref5)</sup>

### Why Include Turnovers?

Turnovers represent **possessions that end without a shot attempt**<sup>[6](#ref6)</sup>. To accurately measure possession usage, we need all three ways possessions end:

1. **FGA** - Possessions ending with field goal attempts
2. **FTA × 0.44** - Possessions ending with free throws
3. **TOV** - Possessions ending with turnovers (bad passes, travels, offensive fouls, etc.)

High-usage players often have high turnover rates (e.g., Luka Dončić, James Harden). Without turnovers, we'd significantly underestimate their possession dominance.

### Why NOT Reduce by Assists (in Traditional Usage)?

The scholarly literature treats **assists as separate from usage**, not as a reduction factor<sup>[1](#ref1)</sup>:

- A player using a possession to assist is still "using" that possession
- High usage + high assists = elite playmaker (Jokić, LeBron), not "less ball dominant"
- Experts prefer **modular approaches**: calculate USG% and AST% separately, then analyze their relationship<sup>[7](#ref7)</sup>

**Our approach:** We calculate BOTH traditional usage AND selfishness-adjusted metrics to capture different dimensions of play.

## Implementation Details

The `build_leaderboard.py` script:

1. Fetches **both Base and Advanced** measure types from `LeagueDashPlayerStats`:
   - **Base** provides: FGA, FTA, TOV, TEAM_ABBREVIATION
   - **Advanced** provides: AST_PCT
2. Merges the two measure types to get all required columns
3. Joins with `LeagueDashTeamStats` (Base measure type) to get team denominators (FGA, FTA, TOV)
4. Calculates the Kobe Quotient for every player-season
5. Computes team rank and league rank for each player within their season
6. Outputs `ballhog_metrics.csv` with all players sorted by season and KQ

## Usage

Generate the season-long leaderboard (defaults to 2020-21 through 2024-25 regular seasons):

```bash
uv run python3 ballhog/build_leaderboard.py
```

Override seasons, season type, or output location as needed:

```bash
uv run python3 ballhog/build_leaderboard.py --seasons 2023-24 --season-type "Playoffs" --output ballhog/2024_playoffs.csv
```

Process only specific seasons:

```bash
uv run python3 ballhog/build_leaderboard.py --seasons 2022-23 2023-24
```

## Example Output

Top 10 most selfish players from the 2023-24 season (by Selfishness Score):

| Rank | Player Name             | Team | Selfishness Score | USG%  | AST%  | Self-Creation Index |
| ---- | ----------------------- | ---- | ----------------- | ----- | ----- | ------------------- |
| 1    | Jalen Brunson           | NYK  | 64.91             | 22.4% | 31.5% | 0.2238              |
| 2    | Luka Dončić             | DAL  | 64.42             | 24.0% | 42.8% | 0.2385              |
| 3    | Anthony Edwards         | MIN  | 64.34             | 22.6% | 24.1% | 0.2250              |
| 4    | De'Aaron Fox            | SAC  | 64.27             | 20.8% | 24.4% | 0.2073              |
| 5    | Tyrese Maxey            | PHI  | 64.00             | 18.6% | 25.7% | 0.1851              |
| 6    | Dejounte Murray         | ATL  | 63.80             | 18.7% | 27.4% | 0.1861              |
| 7    | Shai Gilgeous-Alexander | OKC  | 63.73             | 21.2% | 28.7% | 0.2111              |
| 8    | Stephen Curry           | GSW  | 63.62             | 19.1% | 24.1% | 0.1905              |
| 9    | Jayson Tatum            | BOS  | 63.53             | 20.1% | 21.1% | 0.2009              |
| 10   | Nikola Vučević          | CHI  | 63.49             | 15.2% | 15.3% | 0.1522              |

**Key Insights:**

- **Jalen Brunson** ranks #1 in selfishness despite lower usage than Luka because he has moderate-to-low assist percentage combined with high shot volume
- **Luka Dončić** has the highest Self-Creation Index (raw usage adjusted by assists) but ranks #2 overall due to his high assist percentage (42.8%) offsetting some selfishness
- **Anthony Edwards** exemplifies high-usage, low-assist play (24.1% AST%) - classic "scorer, not facilitator"
- Players can rank high through different paths: high usage + low assists (Edwards) or moderate usage + very low assists (Vučević at 15.3%)

## References

<a name="ref1"></a>**[1]** Cleaning the Glass. (n.d.). _Player Offensive Overview Guide_. Retrieved from https://cleaningtheglass.com/stats/guide/player_offensive_overview

<a name="ref2"></a>**[2]** Oliver, D. (2004). _Basketball on Paper: Rules and Tools for Performance Analysis_. Potomac Books. Retrieved from https://www.amazon.com/Basketball-Paper-Rules-Performance-Analysis/dp/1574886886

<a name="ref3"></a>**[3]** Basketball-Reference.com. (n.d.). _Dean Oliver's Four Factors_. Retrieved from https://www.basketball-reference.com/about/factors.html

<a name="ref4"></a>**[4]** Burnt Orange Nation. (2011). _Advanced Basketball Statistics: Understanding Possession Estimation_. Retrieved from https://www.burntorangenation.com/2011/10/19/2464697/advanced-basketball-statistics-understanding-possession-estimation

<a name="ref5"></a>**[5]** ArXiv. (2023). _Dean Oliver's Four Factors Revisited_. Retrieved from https://arxiv.org/abs/2305.13032

<a name="ref6"></a>**[6]** Kubatko, J., Oliver, D., Pelton, K., & Rosenbaum, D. (2007). A Starting Point for Analyzing Basketball Statistics. _Journal of Quantitative Analysis in Sports_, 3(3). https://doi.org/10.2202/1559-0410.1070

<a name="ref7"></a>**[7]** FiveThirtyEight. (n.d.). _How Did Basketball End Up With Four Versions (And Counting) Of One Stat?_ Retrieved from https://fivethirtyeight.com/features/how-did-basketball-end-up-with-four-versions-and-counting-of-one-stat/

### Additional Resources

- **Basketball-Reference.com Glossary**: Comprehensive definitions of advanced statistics - https://www.basketball-reference.com/about/glossary.html
- **NBA.com Stats Glossary**: Official NBA stat definitions including tracking data - https://www.nba.com/stats/help/glossary
- **Squared Statistics**: In-depth explanations of Oliver's Four Factors - https://squared2020.com/2017/09/05/introduction-to-olivers-four-factors/
- **Nylon Calculus**: Academic-level basketball analytics articles - https://fansided.com/nylon-calculus/
