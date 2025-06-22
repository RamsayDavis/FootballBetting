# main.py
import pandas as pd
from tqdm import tqdm
from src.analysis import export_season_report_to_pdf, export_single_match_report, plot_cumulative_profit, plot_profit_distribution
from src.backtester import Backtester
from src.data_handler import get_unique_matches, get_match_data, load_data
from src.strategies import ArbStrategy
from src.config import TIMESTAMP,REPORTS_DIR

def run_season_analysis(strategy_object, odds_df, goals_df):
    """Orchestrates a full season backtest for a given strategy object."""
    backtester = Backtester(strategy_object)
    matches = get_unique_matches(odds_df)
    
    profits = []
    for index, row in tqdm(matches.iterrows(), total=matches.shape[0], desc=f"Testing {strategy_object.name}"):
        match_data = get_match_data(row['Home Team'], row['Away Team'], odds_df, goals_df)
        if match_data is not None:
            pnl = backtester.run(match_data)
            profits.append({'profit': pnl})

    profit_df = pd.DataFrame(profits)

    # --- Generate Stats and Plots for the Report ---
    stats = {
        "Total Matches Analyzed": len(profit_df),
        "Total Net Profit (%)": f"{profit_df['profit'].sum():.2f}",
        "Average Profit per Match (%)": f"{profit_df['profit'].mean():.4f}",
        "Win Rate (%)": f"{(len(profit_df[profit_df['profit'] > 0]) / len(profit_df)) * 100:.2f}"
    }

    # Create plot files and get their paths
    p1_path = REPORTS_DIR / f"temp_cum_profit_{TIMESTAMP}.png"
    p2_path = REPORTS_DIR / f"temp_dist_profit_{TIMESTAMP}.png"
    plot_paths = [
        plot_cumulative_profit(profit_df, p1_path),
        plot_profit_distribution(profit_df, p2_path)
    ]
    
    # Export everything to a single PDF
    export_season_report_to_pdf(stats, plot_paths, strategy_object.name)

def run_single_match_analysis(strategy_object, home_team, away_team, odds_df, goals_df):
    """Orchestrates an analysis of a single match and exports reports."""
    print(f"\n--- Analyzing Single Match: {home_team} vs {away_team} ---")
    
    match_data = get_match_data(home_team, away_team, odds_df, goals_df)
    if match_data is None:
        print("Match data not found.")
        return

    backtester = Backtester(strategy_object)
    pnl = backtester.run(match_data)
    
    # Export the CSV and PDF report
    export_single_match_report(match_data, pnl, home_team, away_team, strategy_object.name)

'''def run_season_analysis(strategy_object, odds_df, goals_df):
    """
    Orchestrates a full season backtest for a given strategy.
    This is mostly the same as the run_season_backtest function from the doc.
    """
    backtester = Backtester(strategy_object)
    matches = get_unique_matches(odds_df)
    
    profits = []
    for index, row in tqdm(matches.iterrows(), total=matches.shape[0], desc="Backtesting All Matches"):
        home, away = row['Home Team'], row['Away Team']
        # The date is carried through but not used in the backtest itself
        match_data = get_match_data(home, away, odds_df, goals_df)
        if match_data is not None:
            profit = backtester.run(match_data)
            profits.append({'match_id': f"{home}_vs_{away}", 'profit': profit, 'date': row['date']})
            
    profit_df = pd.DataFrame(profits)
    
    # This is the call to the analysis module for a full season
    generate_performance_report(profit_df, strategy_object.name)


def run_single_match_analysis(strategy_object, home_team, away_team, odds_df, goals_df):
    """Orchestrates an analysis of a single match."""
    print(f"\n--- Analyzing Single Match: {home_team} vs {away_team} ---")
    
    # 1. Get the data for just one match
    match_data = get_match_data(home_team, away_team, odds_df, goals_df)
    if match_data is None:
        print("Match data not found.")
        return

    # 2. Run the backtester on that single match
    backtester = Backtester(strategy_object)
    pnl = backtester.run(match_data)
    print(f"Calculated Profit using '{strategy_object.name}': {pnl:.2f}%")

    # 3. Call the analysis module to visualize the single match
    # (Here, the analysis function is the detailed plot)
    plot_match_analysis(match_data, home_team, away_team)
'''

def main():
    """Main execution function."""
    # --- Load data once ---
    print("Loading data...")
    odds_df, goals_df = load_data()
    print("Data loaded successfully.")

    # --- Define Strategy and Parameters Here ---
    strategy_to_test = ArbStrategy()

    # --- CHOOSE YOUR ANALYSIS MODE ---
    # Un-comment the mode you want to run.
    
    # OPTION 1: Run a full season analysis
    
    run_season_analysis(strategy_to_test, odds_df, goals_df)

    # OPTION 2: Run a single match analysis
    #run_single_match_analysis(strategy_object=strategy_to_test, home_team="Fulham", away_team="Brentford",odds_df=odds_df, goals_df=goals_df)


if __name__ == "__main__":
    main()