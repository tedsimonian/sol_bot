"""
Strategy_007

Technical Indicators: 
    - Moving Average Convergence Divergence (MACD)

Strategy Description:
    This strategy is based on the Moving Average Convergence Divergence (MACD) indicator to identify potential trading opportunities.
    When the MACD line crosses above the signal line, the strategy enters a long position.
    When the MACD line crosses below the signal line, the strategy enters a short position.
    The strategy includes mechanisms to exit trades when the MACD line crosses below the signal line for long positions or above the signal line for short positions.

Entry:
    - MACD line crosses above the signal line, a long position is entered.
    - MACD line crosses below the signal line, a short position is entered.

Exit:
    - MACD line crosses below the signal line, a long position is exited.
    - MACD line crosses above the signal line, a short position is exited.
"""

from backtesting import Backtest, Strategy

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import warnings
import pandas_ta as ta
import pandas as pd

# filter all warnings
warnings.filterwarnings('ignore')  # Setting the warnings to be ignored

class Strategy_007(Strategy):
    macd_short_period = 12
    macd_long_period = 26
    
    def init(self):
        close_series = pd.Series(self.data.Close)
        # Initialize the indicators
        self.macd = self.I(ta.macd, close_series, self.macd_short_period, self.macd_long_period)

    def next(self):
        # If the MACD line crosses above the signal line, and we're not already in a long position
        if (self.macd[-1] > 0) and (not self.position.is_long):
            self.buy()
        
        # If the MACD line crosses below the signal line, and we're not already in a short position
        if (self.macd[-1] < 0) and (not self.position.is_short):
            self.sell()
        
        # Close long position when the MACD line crosses below the signal line
        if self.position.is_long and (self.macd[-1] < 0):
            self.position.close()
        
        # Close short position when the MACD line crosses above the signal line
        if self.position.is_short and (self.macd[-1] > 0):
            self.position.close()



exchange = get_kucoin_connection()  # Establish connection to Kucoin
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)  # Fetch data from exchange

bt = Backtest(data_df, Strategy_007, cash=STARTING_CAPITAL, commission=COMMISSION)  # Set up the backtest
stats = bt.run()  # Run the backtest

bt.plot()  # Plot the backtest results

print(stats)  # Print the statistics of the backtest
