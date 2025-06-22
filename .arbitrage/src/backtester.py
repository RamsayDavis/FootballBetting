# src/backtester.py

class Backtester:
    def __init__(self, strategy_object):
        self.strategy = strategy_object

    def _update_position(self, instruction, prev_pos, row):
        """Updates the position based on the instruction from the strategy."""
        if instruction == 'Trade':
            return (row['Real Stake'], row['Synth Stake'], row['Profit'])
        elif instruction == 'Clear':
            return (0, 0, 0)
        else: # Hold
            return prev_pos

    def _update_pnl(self,instruction, prev_pnl, prev_pos):
        """Updates the cumulative Profit and Loss."""
        if instruction == 'Clear':
            return prev_pnl + abs(prev_pos[2])
        else:
            return prev_pnl

    def run(self, match_data):
        """
        Runs the backtest for a single match.
        Notice it doesn't care what the strategy is, it just calls .generate_signal()
        """
        pnl = 0.0
        position = (0, 0, 0)

        for i, row in match_data.iterrows():
            # Get signal from the STRATEGY OBJECT
            instruction = self.strategy.generate_signal(row, position)
            
            pnl = self._update_pnl(instruction, pnl, position)
            position = self._update_position(instruction, position, row)
            
        # Handle closing position at the end of the match
        if position != (0, 0, 0):
            pnl += abs(position[2])
            
        return pnl