from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas as pd
import warnings

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_014(Strategy):
    def init(self):
        # Your strategy initialization logic
        # Calculate Fibonacci levels here and initialize grid levels

        self.high = self.data.High.max()
        self.low = self.data.Low.min()
        
        self.fib_levels = [self.low + (self.high - self.low) * retracement for retracement in [0.236, 0.382, 0.5, 0.618, 0.786]]
        
        self.grid_levels_buy = [level for level in self.fib_levels if level < self.data.Close[-1]]
        self.grid_levels_sell = [level for level in self.fib_levels if level > self.data.Close[-1]]

        # Assume uniform position size for simplicity; this can be adjusted as needed.
        self.position_size = self.broker.equity * 0.01  # 1% of current equity

    def next(self):
        # Your strategy's step logic
        # Execute trades and manage positions according to the strategy rules
        
        # Cancel unfilled orders at the end of each step
        for trade in self.trades:
            if trade.is_open:
                self.broker.cancel(trade)

        # Place buy orders at each retracement level below the current price with stop loss and take profit
        for level in self.grid_levels_buy:
            self.buy(size=self.position_size, sl=level*0.99, tp=level*1.01, limit=level)

        # Place sell orders at each retracement level above the current price with stop loss and take profit
        for level in self.grid_levels_sell:
            self.sell(size=self.position_size, sl=level*1.01, tp=level*0.99, limit=level)

        # Adjust the grid as the market moves over time
        new_high = self.data.High[-1]
        new_low = self.data.Low[-1]
        
        # Update and recalibrate if new highs and lows are found
        if new_high > self.high or new_low < self.low:
            self.high = max(self.high, new_high)
            self.low = min(self.low, new_low)
            
            self.fib_levels = [self.low + (self.high - self.low) * retracement for retracement in [0.236, 0.382, 0.5, 0.618, 0.786]]
            
            self.grid_levels_buy = [level for level in self.fib_levels if level < self.data.Close[-1]]
            self.grid_levels_sell = [level for level in self.fib_levels if level > self.data.Close[-1]]
    
exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_014, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)