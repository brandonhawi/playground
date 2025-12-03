# NBA API Issue Validations

This folder contains validation notebooks for open issues in the [nba_api](https://github.com/swar/nba_api) repository.

## Purpose

These notebooks provide executable proof of issue resolutions or reproductions, making it easier for maintainers to validate bug fixes and community contributions.

## Validated Issues

### Issue #98: `get_data_frames()` not working on shot location endpoints
- **Notebook**: [`issue_98_get_data_frames_fix.ipynb`](issue_98_get_data_frames_fix.ipynb)
- **Status**: ✅ Resolved
- **Description**: Validates that `LeagueDashTeamShotLocations` and `LeagueDashPlayerShotLocations` now correctly return DataFrames via `get_data_frames()`
- **Run in Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/brandonhawi/playground/blob/main/nba_api_issue_validations/issue_98_get_data_frames_fix.ipynb)

## How to Use

### Run Locally
```bash
uv run jupyter notebook nba_api_issue_validations/
```

### Run in Google Colab
Click the "Open in Colab" badge above any notebook to run it in your browser without any setup.

## Contributing

If you find or validate other nba_api issues, feel free to add notebooks here following the naming convention:
- `issue_[NUMBER]_[brief_description].ipynb`
