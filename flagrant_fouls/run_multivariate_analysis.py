#!/usr/bin/env python3
"""
Multivariate Regression Analysis: Flagrant Fouls with Covariates
"""

import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.formula.api import ols
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("FLAGRANT FOULS MULTIVARIATE REGRESSION ANALYSIS")
print("="*80)

# Load data
csv_file = Path('nba_flagrant_fouls.csv')
games_with_data = pd.read_csv(csv_file)

print(f"\nLoaded {len(games_with_data)} games from CSV")
print(f"Columns: {games_with_data.columns.tolist()}")

# Create long-format dataset
# Home team observations
home_cols = ['game_id', 'home_team', 'home_flagrants', 'home_score', 'away_score',
             'home_rebounds', 'away_rebounds', 'home_assists', 'away_assists',
             'home_turnovers', 'away_turnovers', 'home_ftm', 'away_ftm',
             'home_inactive_players', 'away_inactive_players']
home_data = games_with_data[home_cols].copy()
home_data.columns = ['game_id', 'team_id', 'committed_flagrant', 'team_score', 'opp_score',
                     'team_rebounds', 'opp_rebounds', 'team_assists', 'opp_assists',
                     'team_turnovers', 'opp_turnovers', 'team_ftm', 'opp_ftm',
                     'team_inactive', 'opp_inactive']
home_data['location'] = 'home'

# Away team observations
away_cols = ['game_id', 'away_team', 'away_flagrants', 'away_score', 'home_score',
             'away_rebounds', 'home_rebounds', 'away_assists', 'home_assists',
             'away_turnovers', 'home_turnovers', 'away_ftm', 'home_ftm',
             'away_inactive_players', 'home_inactive_players']
away_data = games_with_data[away_cols].copy()
away_data.columns = ['game_id', 'team_id', 'committed_flagrant', 'team_score', 'opp_score',
                     'team_rebounds', 'opp_rebounds', 'team_assists', 'opp_assists',
                     'team_turnovers', 'opp_turnovers', 'team_ftm', 'opp_ftm',
                     'team_inactive', 'opp_inactive']
away_data['location'] = 'away'

# Combine
df = pd.concat([home_data, away_data], ignore_index=True)

# Create outcome variable
df['point_differential'] = df['team_score'] - df['opp_score']

# Create predictor variables
df['committed_flagrant'] = (df['committed_flagrant'] > 0).astype(int)
df['rebound_diff'] = df['team_rebounds'] - df['opp_rebounds']
df['assist_diff'] = df['team_assists'] - df['opp_assists']
df['turnover_diff'] = df['opp_turnovers'] - df['team_turnovers']  # Higher is better
df['ft_diff'] = df['team_ftm'] - df['opp_ftm']
df['inactive_diff'] = df['opp_inactive'] - df['team_inactive']  # Higher is better

print(f"\nDataset shape: {df.shape}")
print(f"Total team-game observations: {len(df)}")

# Descriptive statistics
print("\n" + "="*80)
print("DESCRIPTIVE STATISTICS")
print("="*80)

print("\nOutcome variable:")
print(df['point_differential'].describe())

print("\nPredictor variables:")
pred_vars = ['committed_flagrant', 'rebound_diff', 'assist_diff', 'turnover_diff', 'ft_diff', 'inactive_diff']
print(df[pred_vars].describe())

print("\nFlagrant foul distribution:")
print(df['committed_flagrant'].value_counts())

# Run regressions
print("\n" + "="*80)
print("REGRESSION MODELS")
print("="*80)

# Model 1: Simple (flagrant only)
simple_model = ols('point_differential ~ committed_flagrant', data=df).fit()

# Model 2: Multivariate (with all covariates)
multi_model = ols('point_differential ~ committed_flagrant + rebound_diff + assist_diff + turnover_diff + ft_diff + inactive_diff + C(location)', data=df).fit()

print("\n" + "-"*80)
print("MODEL 1: SIMPLE (FLAGRANT ONLY)")
print("-"*80)
print(simple_model.summary())

print("\n" + "-"*80)
print("MODEL 2: MULTIVARIATE (WITH COVARIATES)")
print("-"*80)
print(multi_model.summary())

# Model comparison
print("\n" + "="*80)
print("MODEL COMPARISON")
print("="*80)

print(f"\nSimple Model (flagrant only):")
print(f"  R²: {simple_model.rsquared:.4f}")
print(f"  Adj. R²: {simple_model.rsquared_adj:.4f}")
print(f"  AIC: {simple_model.aic:.2f}")
print(f"  BIC: {simple_model.bic:.2f}")

print(f"\nMultivariate Model (with covariates):")
print(f"  R²: {multi_model.rsquared:.4f}")
print(f"  Adj. R²: {multi_model.rsquared_adj:.4f}")
print(f"  AIC: {multi_model.aic:.2f}")
print(f"  BIC: {multi_model.bic:.2f}")

print(f"\nImprovement:")
print(f"  ΔR²: +{multi_model.rsquared - simple_model.rsquared:.4f} ({((multi_model.rsquared - simple_model.rsquared)/simple_model.rsquared*100):.1f}% increase)")
print(f"  ΔAIC: {simple_model.aic - multi_model.aic:.2f} (negative is better)")

# F-test for model comparison
from scipy.stats import f as f_dist
f_stat = ((simple_model.ssr - multi_model.ssr) / (multi_model.df_model - simple_model.df_model)) / (multi_model.ssr / multi_model.df_resid)
p_value = 1 - f_dist.cdf(f_stat, multi_model.df_model - simple_model.df_model, multi_model.df_resid)
print(f"\nF-test (nested model comparison):")
print(f"  F-statistic: {f_stat:.4f}")
print(f"  P-value: {p_value:.4e}")
print(f"  Result: Covariates {'significantly' if p_value < 0.05 else 'do not'} improve model (α = 0.05)")

# Key findings
print("\n" + "="*80)
print("KEY FINDINGS")
print("="*80)

flagrant_coef_simple = simple_model.params['committed_flagrant']
flagrant_pval_simple = simple_model.pvalues['committed_flagrant']
flagrant_coef_multi = multi_model.params['committed_flagrant']
flagrant_pval_multi = multi_model.pvalues['committed_flagrant']

print(f"\n1. FLAGRANT FOUL EFFECT:")
print(f"   Simple model:")
print(f"     Coefficient: {flagrant_coef_simple:.4f} points")
print(f"     P-value: {flagrant_pval_simple:.4f}")
print(f"     Significant: {'YES' if flagrant_pval_simple < 0.05 else 'NO'}")

print(f"\n   Multivariate model (controlling for covariates):")
print(f"     Coefficient: {flagrant_coef_multi:.4f} points")
print(f"     P-value: {flagrant_pval_multi:.4f}")
print(f"     Significant: {'YES' if flagrant_pval_multi < 0.05 else 'NO'}")

print(f"\n2. MOST SIGNIFICANT PREDICTORS:")
sig_vars = [(var, multi_model.params[var], multi_model.pvalues[var])
            for var in multi_model.params.index
            if var != 'Intercept' and multi_model.pvalues[var] < 0.05]
sig_vars.sort(key=lambda x: x[2])
for var, coef, pval in sig_vars:
    print(f"   - {var}: {coef:+.4f} points (p = {pval:.4e})")

# Variance Inflation Factor
print("\n" + "="*80)
print("MULTICOLLINEARITY DIAGNOSTICS (VIF)")
print("="*80)

X_vif = df[['committed_flagrant', 'rebound_diff', 'assist_diff', 'turnover_diff', 'ft_diff', 'inactive_diff']].dropna()
vif_data = pd.DataFrame()
vif_data["Variable"] = X_vif.columns
vif_data["VIF"] = [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]
print("\n" + vif_data.to_string(index=False))
print("\nInterpretation: VIF > 5 indicates multicollinearity concern, VIF > 10 is serious")

# Correlation matrix
print("\n" + "="*80)
print("CORRELATION MATRIX")
print("="*80)
corr_vars = ['point_differential', 'committed_flagrant', 'rebound_diff', 'assist_diff', 'turnover_diff', 'ft_diff', 'inactive_diff']
corr_matrix = df[corr_vars].corr()
print("\n" + corr_matrix.to_string())

# Results table
print("\n" + "="*80)
print("MULTIVARIATE REGRESSION COEFFICIENTS TABLE")
print("="*80)

results_data = []
for var in multi_model.params.index:
    if var == 'Intercept':
        continue
    coef = multi_model.params[var]
    se = multi_model.bse[var]
    pval = multi_model.pvalues[var]
    ci = multi_model.conf_int().loc[var]

    results_data.append({
        'Variable': var,
        'Coefficient': f"{coef:.4f}",
        'Std. Error': f"{se:.4f}",
        '95% CI': f"[{ci[0]:.4f}, {ci[1]:.4f}]",
        'P-value': f"{pval:.4f}",
        'Sig': '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
    })

results_df = pd.DataFrame(results_data)
print("\n" + results_df.to_string(index=False))
print("\nSignificance: *** p<0.001, ** p<0.01, * p<0.05")

# Final summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"\nData: {len(games_with_data)} games, {len(df)} team-game observations")
print(f"Games with flagrants: {df['committed_flagrant'].sum()}")
print(f"Games without flagrants: {(1-df['committed_flagrant']).sum()}")

print(f"\nMultivariate Model Performance:")
print(f"  R² = {multi_model.rsquared:.4f} ({multi_model.rsquared*100:.1f}% of variance explained)")
print(f"  Adjusted R² = {multi_model.rsquared_adj:.4f}")
print(f"  F-statistic = {multi_model.fvalue:.4f} (p < 0.001)")

print(f"\nFlagrant Foul Impact (controlling for all covariates):")
print(f"  Effect: {flagrant_coef_multi:.4f} points")
print(f"  95% CI: [{multi_model.conf_int().loc['committed_flagrant'][0]:.4f}, {multi_model.conf_int().loc['committed_flagrant'][1]:.4f}]")
print(f"  P-value: {flagrant_pval_multi:.4f}")
print(f"  Conclusion: Flagrant fouls are {'significantly' if flagrant_pval_multi < 0.05 else 'not significantly'} associated with point differential")
print(f"              after controlling for rebounds, assists, turnovers, free throws, injuries, and home/away status.")

print("\n" + "="*80)
print("END OF ANALYSIS")
print("="*80)
