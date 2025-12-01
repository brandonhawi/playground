# Playground

This repository is a lightweight playground for exploring how flagrant fouls correlate with NBA outcomes. The `flagrant_fouls/` subdirectory holds the core dataset plus the notebooks used for data collection and the current point differential regression.

## Layout
- `flagrant_fouls/nba_flagrant_fouls.csv` – one row per game, recording the home/away teams, flagrant fouls, and final scores.
- `flagrant_fouls/data_collection.ipynb` – helper notebook that pulls box-score data from the NBA API.
- `flagrant_fouls/point_differential_analysis.ipynb` – linear regression modeling of point differential against foul counts.
- `AGENTS.md` – operating guidelines for contributors (especially AI agents).

## Data snapshot
- Dataset stored in `flagrant_fouls/nba_flagrant_fouls.csv`; refer to that file for the current row count and season coverage.
- Seasons captured: game IDs with leading prefixes `0012`, `0022`, `0032`, `0042`, and `0052`.
- Games with no play-by-play data are tracked in `flagrant_fouls/nba_skipped_games.csv`.
- Schema: `game_id, home_team, away_team, home_flagrants, away_flagrants, home_score, away_score`.

## Getting started
1. From the project root, install dependencies with `uv sync`.
2. Inspect `AGENTS.md` for repository conventions.
3. Change into `flagrant_fouls/` and open the notebooks with `jupyter notebook` (or `lab`).
4. Re-run `point_differential_analysis.ipynb` any time the CSV is updated.
