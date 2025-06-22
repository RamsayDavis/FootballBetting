# src/data_handler.py
import pandas as pd
import numpy as np
import math
from . import config # Relative import from the same package

def load_data():
    """
    Loads and performs the initial cleaning of the odds and goals data.
    This is where your initial processing code goes.
    """
    # Load odds data using the path from the config file
    odds_df = pd.read_csv(config.ODDS_DATA_PATH)
    if 'Unnamed: 0' in odds_df.columns:
        odds_df = odds_df.drop('Unnamed: 0', axis=1)

    # Load goals data using the path from the config file
    goals_df = pd.read_csv(config.GOALS_DATA_PATH)
    goals_df['date'] = pd.to_datetime(goals_df['date']).dt.date
    goals_df['Half Time'] = '0'
    goals_df['Goal Scored'] = 'Yes'

    return odds_df, goals_df

def get_unique_matches(odds_df):
    """Returns a DataFrame of unique matches."""
    return odds_df[['Home Team', 'Away Team','date']].drop_duplicates()

# --- Match Data Processing ---
def get_match_data(home_team, away_team, odds_data, goals_data):
    """
    Creates a detailed, minute-by-minute dataframe for a single match,
    including odds, goals, and strategy signals.
    """
    match_odds = odds_data[(odds_data['Home Team'] == home_team) & (odds_data['Away Team'] == away_team)].copy()
    
    if match_odds.empty:
        return None

    match_odds['time_key'] = list(zip(match_odds['Elapsed Time'].astype(int), match_odds['Added Time'].astype(int), match_odds['Half Time'].astype(int)))

    norm_mins = [(x, 0, 0) for x in range(0, 91)]
    extra_times = set(match_odds['time_key']) - set(norm_mins)
    all_times = sorted(norm_mins + list(extra_times)) # Combine first, then sort.
    match_timeline = pd.DataFrame(all_times, columns=['Elapsed Time', 'Added Time', 'Half Time'])
    match_timeline['time_key'] = list(zip(match_timeline['Elapsed Time'], match_timeline['Added Time'], match_timeline['Half Time']))


    odds_pivot = match_odds.pivot_table(index='time_key', columns='Selection', values='Last Traded Price')
    
    market_cols = {
        'Real': 'Under 2.5 Goals', 'Over 2.5 Odds': 'Over 2.5 Goals',
        '1-1 Odds': '1 - 1', '2-0 Odds': '2 - 0', '0-2 Odds': '0 - 2',
        '1-0 Odds': '1 - 0', '0-1 Odds': '0 - 1', '0-0 Odds': '0 - 0'
    }
    
    for new_col, original_col in market_cols.items():
        if original_col in odds_pivot.columns:
            match_timeline = match_timeline.merge(odds_pivot[[original_col]], on='time_key', how='left').rename(columns={original_col: new_col})
        else:
            match_timeline[new_col] = np.nan
    
    for col in market_cols.keys():
        still_live = match_timeline[col].notna() & (match_timeline[col] != 1000)
        if still_live.any():
            last_live_idx = still_live[still_live].index[-1]
            match_timeline.loc[last_live_idx + 1:, col] = 1000
        match_timeline[col] = match_timeline[col].ffill().bfill()
        match_timeline[col] = match_timeline[col].replace(1000.0, np.nan)

    synth_components = ['1-1 Odds', '2-0 Odds', '0-2 Odds', '1-0 Odds', '0-1 Odds', '0-0 Odds']
    match_timeline['Synthetic'] = match_timeline[synth_components].apply(calc_synth, axis=1)
    
    match_goals = goals_data[(goals_data['Home Team'] == home_team) & (goals_data['Away Team'] == away_team)].copy()
    if not match_goals.empty:
        match_goals['time_key'] = list(zip(match_goals['Elapsed Time'].astype(int), match_goals['Added Time'].astype(int), match_goals['Half Time'].astype(int)))
        match_timeline = match_timeline.merge(match_goals[['time_key', 'Goal Scored', 'Player', 'Score']], on='time_key', how='left')
    else:
        match_timeline[['Goal Scored', 'Player', 'Score']] = [np.nan, np.nan, np.nan]
        
    match_timeline['Score'] = match_timeline['Score'].ffill().fillna('0-0')
    match_timeline['Goal Scored'] = match_timeline['Goal Scored'].fillna('No')

    # === YOUR STAKING LOGIC RE-IMPLEMENTED (VECTORIZED) ===
    comm = config.BETFAIR_COMMISSION
    budget = config.INITIAL_LIABILITY
    BackOdds = match_timeline['Back Odds'] = match_timeline[['Real', 'Synthetic']].max(axis=1)
    LayOdds = match_timeline['Lay Odds'] = match_timeline[['Real', 'Synthetic']].min(axis=1)

    # To avoid division by zero or other errors if odds are missing
    valid_odds = (BackOdds.notna()) & (LayOdds.notna()) & (LayOdds > 1.0) & (BackOdds > 0)
    
    # Pre-calculate common terms for clarity
    term1 = (LayOdds - comm)
    term2 = ((1 - comm) * BackOdds + comm)
    
    # Calculate stakes only for valid rows
    match_timeline.loc[valid_odds, 'Lay Stake'] = (budget / ((term1 / term2) + LayOdds - 1)).round(1)
    match_timeline.loc[valid_odds, 'Back Stake'] = (budget / (1 + (LayOdds - 1) * (term2 / term1))).round(1)

    match_timeline['Lay'] = np.where(match_timeline['Real'] >= match_timeline['Synthetic'], 'Synthetic', 'Real')
    match_timeline['Real Stake'] = np.where(match_timeline['Lay'] == 'Real', -1 * match_timeline['Lay Stake'], match_timeline['Back Stake'])
    match_timeline['Synth Stake'] = np.where(match_timeline['Lay'] == 'Synthetic', -1 * match_timeline['Lay Stake'], match_timeline['Back Stake'])

    # Calculate profit based on your formula
    match_timeline['Profit'] = ((1 - comm) * match_timeline['Lay Stake'] - match_timeline['Back Stake']).round(2)
    # This profit represents the percentage gain on your £100 liability (called budget, can change in the config file)
    
    def format_time(row):
        if row['Half Time'] > 0: return f"HT+{row['Half Time']}'"
        if row['Added Time'] > 0: return f"{row['Elapsed Time']}+{row['Added Time']}'"
        return f"{row['Elapsed Time']}'"
    match_timeline['plot_label'] = match_timeline.apply(format_time, axis=1)

    return match_timeline

# --- Utility Functions ---
def calc_synth(odds_series):
    """Calculates the harmonic mean for a series of odds."""
    inv_sum = (1 / odds_series).sum()
    if inv_sum == 0:
        return np.nan
    return max(1, 1 / inv_sum)