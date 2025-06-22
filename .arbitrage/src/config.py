# src/config.py
from pathlib import Path
import datetime

# --- File Paths ---
# Using pathlib is a modern way to handle paths that works on any OS
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ODDS_DATA_PATH = DATA_DIR / "odds_2022-2023.csv"
GOALS_DATA_PATH = DATA_DIR / "goals_2022-2023.csv"
REPORTS_DIR = BASE_DIR / "reports" 

# --- Fixed Parameters ---
BETFAIR_COMMISSION = 0.02
INITIAL_LIABILITY = 100.0

# --- Backtesting Parameters ---
ENTRY_CONDITION = 0.0
EXIT_CONDITION = 0.0

# --- Report Configuration ---

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")