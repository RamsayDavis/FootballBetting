# src/analysis.py
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.style as style
from fpdf import FPDF
import os
from . import config

def plot_cumulative_profit(profit_df, output_path):
    """Generates and saves the cumulative profit plot."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 6))
    plt.plot(profit_df['profit'].cumsum(), marker='o', linestyle='-', markersize=4)
    plt.title('Cumulative Strategy Profit Over Season', fontsize=16)
    plt.xlabel('Match Number')
    plt.ylabel(f"Cumulative Profit (% of £{config.INITIAL_LIABILITY} Liability)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path) # Save the plot to a file
    plt.close() # Close the plot to prevent it from displaying
    return output_path

def plot_profit_distribution(profit_df, output_path):
    """Generates and saves the histogram of profits."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 6))
    plt.hist(profit_df['profit'], bins=50, color='skyblue', edgecolor='black')
    mean_profit = profit_df['profit'].mean()
    plt.axvline(mean_profit, color='red', linestyle='dashed', linewidth=2, label=f"Mean: {mean_profit:.4f}%")
    plt.title('Distribution of Profit Per Match', fontsize=16)
    plt.xlabel('Profit (%)')
    plt.ylabel('Number of Matches')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path) # Save the plot
    plt.close() # Close the plot
    return output_path

def plot_match_analysis(match_df, home_team, away_team,output_path):
    style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots(figsize=(15, 8))

    ax1.plot(match_df['plot_label'], match_df['Real'], color='royalblue', label='Real Odds (U2.5)', alpha=0.9)
    ax1.plot(match_df['plot_label'], match_df['Synthetic'], color='darkorange', label='Synthetic Odds (U2.5)', linestyle='--')
    ax1.set_xlabel('Match Time')
    ax1.set_ylabel('Odds')
    ax1.tick_params(axis='y')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(match_df['plot_label'], match_df['Profit'], color='mediumseagreen', label='Arbitrage Profit (%)', alpha=0.7)
    ax2.set_ylabel('Arbitrage Profit (% of £100 Liability)', color='mediumseagreen')
    ax2.tick_params(axis='y', labelcolor='mediumseagreen')
    ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')

    tick_indices = np.linspace(0, len(match_df['plot_label']) - 1, 15, dtype=int)
    plt.xticks(match_df['plot_label'][tick_indices], rotation=45, ha="right")
    
    goal_times = match_df[match_df['Goal Scored'] == 'Yes']
    for idx, goal in goal_times.iterrows():
        plt.axvline(x=goal['plot_label'], color='red', linestyle='--', alpha=0.8, label=f"Goal ({goal['Score']})")
    
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(list(by_label.values()), list(by_label.keys()), loc='best')

    plt.title(f'Match Analysis: {home_team} vs {away_team}', fontsize=16)
    fig.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path
def export_season_report_to_pdf(stats, plot_paths, strategy_name):
    """Creates a PDF report for the full season analysis."""
    # Ensure the Reports directory exists
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(0, 10, f'Season Performance Report: {strategy_name}', 0, 1, 'C')
    pdf.ln(10)
    
    # Stats section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Performance Summary:", 0, 1)
    pdf.set_font("Arial", '', 12)
    for key, value in stats.items():
        pdf.cell(0, 8, f"{key}: {value}", 0, 1)
    pdf.ln(10)

    # Images section
    for plot_path in plot_paths:
        pdf.image(str(plot_path), x=None, y=None, w=190) # w=190mm fits well on A4
        pdf.ln(5)

    # Save the PDF
    report_filename = f"SeasonReport_{strategy_name.replace(' ', '')}_{config.TIMESTAMP}.pdf"
    output_path = config.REPORTS_DIR / report_filename
    pdf.output(output_path)
    print(f"Season report saved to: {output_path}")

    # Clean up the temporary image files
    for plot_path in plot_paths:
        os.remove(plot_path)

def export_single_match_report(match_df, pnl, home, away, strategy_name):
    """Exports a CSV of the match data and creates a PDF report."""
    # Ensure the Reports directory exists
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Save the detailed CSV data
    csv_filename = f"MatchData_{home}_vs_{away}_{config.TIMESTAMP}.csv"
    csv_path = config.REPORTS_DIR / csv_filename
    match_df.to_csv(csv_path, index=False)
    print(f"Detailed match data saved to: {csv_path}")

    # 2. Create the plot image
    plot_filename = f"temp_match_plot_{config.TIMESTAMP}.png"
    plot_path = config.REPORTS_DIR / plot_filename
    plot_match_analysis(match_df, home, away, plot_path)

    # 3. Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f'Single Match Analysis: {home} vs {away}', 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Strategy Used: {strategy_name}", 0, 1)
    pdf.cell(0, 8, f"Calculated PnL: {pnl:.2f}%", 0, 1)
    pdf.ln(10)

    pdf.image(str(plot_path), x=None, y=None, w=190)
    
    report_filename = f"MatchReport_{home}_vs_{away}_{config.TIMESTAMP}.pdf"
    output_path = config.REPORTS_DIR / report_filename
    pdf.output(output_path)
    print(f"Single match report saved to: {output_path}")

    # 4. Clean up the plot image file
    os.remove(plot_path)

def generate_performance_report(profit_df, strategy_name):
    # --- Statistical Summary (on ALL processed matches) ---
    print(f"--- Performance Report for: {strategy_name} ---")

    total_profit = profit_df['profit'].sum()
    num_matches = len(profit_df)
    profitable_matches = profit_df[profit_df['profit'] > 0]
    num_profitable = len(profitable_matches)

    # Sort by profit in descending order to get the top matches
    profit_df.sort_values(by="profit", ascending=False, inplace=True)

    # --- Print Summary ---
    print(f"Total Matches Analyzed: {num_matches}")
    print(f"Total Net Profit: {total_profit:.2f}%")
    print(f"Average Profit per Match: {profit_df['profit'].mean():.4f}%")
    print(f"Profitable Matches: {num_profitable} ({(num_profitable/num_matches)*100:.2f}%)")

    print("\n--- Top 3 Most Profitable Matches ---")
    # Reset index to ensure .loc[i] works as expected
    profit_df.reset_index(drop=True, inplace=True) 

    # Loop through the top 3 rows of the sorted DataFrame
    for i in range(3):
        # Check if there are enough matches to display
        if i < len(profit_df):
            match_id = profit_df["match_id"].loc[i]
            profit = profit_df["profit"].loc[i]
            print(f"Top {i+1} profit was for match {match_id} with {profit:.2f}%")
    if num_matches > 0:
        print(f"Win Rate: {(num_profitable / num_matches) * 100:.2f}%")
    sharpe_ratio = profit_df['profit'].mean() / profit_df['profit'].std() if profit_df['profit'].std() != 0 else 0
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

    # --- Chronological & Visual Analysis (on matches WITH dates) ---
    
    # FIX: Create a clean dataframe for plotting, removing rows with no date.
    plot_df = profit_df.dropna(subset=['date']).copy()
    plot_df = plot_df.sort_values('date')

    if not plot_df.empty:
        # a) Cumulative Profit Over Time
        plot_df['cumulative_profit'] = plot_df['profit'].cumsum()
        plt.figure(figsize=(15, 7))
        # Use the clean plot_df for plotting
        plt.plot(plot_df['date'], plot_df['cumulative_profit'], marker='o', linestyle='-')
        plt.title('Cumulative Strategy Profit Over Season', fontsize=16)
        plt.xlabel('Date'); plt.ylabel('Cumulative Profit (%)'); plt.grid(True); plt.xticks(rotation=45); plt.tight_layout(); plt.show()
    else:
        print("\nNo matches with valid dates found to create a cumulative profit plot.")

    # b) Histogram of Profit per Match (can use all data)
    plt.figure(figsize=(15, 7))
    plt.hist(profit_df['profit'], bins=50, color='skyblue', edgecolor='black')
    plt.axvline(profit_df['profit'].mean(), color='red', linestyle='dashed', linewidth=2, label=f"Mean: {profit_df['profit'].mean():.4f}%")
    plt.title('Distribution of Profit Per Match', fontsize=16)
    plt.xlabel('Profit (%)'); plt.ylabel('Number of Matches'); plt.legend(); plt.grid(True); plt.show()