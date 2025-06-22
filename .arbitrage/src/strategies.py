# src/strategies.py
from abc import ABC, abstractmethod
import pandas as pd
from . import config


class BaseStrategy(ABC):
    """
    Abstract Base Class for all strategies. It defines the 'contract'
    that all strategy classes must follow.
    """
    def __init__(self):
        # Name for logging/reporting
        self.name = "Base Strategy"

    @abstractmethod
    def generate_signal(self, row, prev_pos):
        """
        The core method for any strategy.
        Must be implemented by any child class.
        """
        pass

class ArbStrategy(BaseStrategy):
    """
    Simple arbitrage strategy, now implemented as a class.
    """
    def __init__(self, entry_threshold=config.ENTRY_CONDITION):
        # Parameters are now instance attributes!
        self.entry_threshold = entry_threshold
        self.name = f"Arbitrage Strategy (threshold={entry_threshold})"

    def generate_signal(self, row, prev_pos):
        # Your set_instruction/crossover_strategy logic goes here.
        if pd.isna(row['Profit']) or pd.isna(row['Real']) or pd.isna(row['Synthetic']):
            return 'Hold'

        in_trade = prev_pos != (0, 0, 0)
        arbitrage_exists = row['Profit'] > self.entry_threshold # Use the instance parameter
        real_minus_synth = row['Real'] - row['Synthetic']

        if not in_trade and arbitrage_exists:
            return 'Trade'
        elif in_trade and (real_minus_synth * prev_pos[0] < 0):
            return 'Clear'
        else:
            return 'Hold'

# Can add alternative strategies here (here is a chatgpt generated one)
class SimpleThresholdStrategy(BaseStrategy):
    """A different, simpler strategy for demonstration."""
    def __init__(self, entry_threshold=config.ENTRY_CONDITION, exit_threshold=config.EXIT_CONDITION):
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.name = f"Simple Threshold (entry={entry_threshold}, exit={exit_threshold})"

    def generate_signal(self, row, prev_pos):
        in_trade = prev_pos != (0, 0, 0)
        
        if not in_trade and row['Profit'] > self.entry_threshold:
            return 'Trade'
        elif in_trade and row['Profit'] < self.exit_threshold:
            return 'Clear'
        else:
            return 'Hold'