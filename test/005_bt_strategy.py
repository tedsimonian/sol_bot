"""
Strategy_005

Technical Indicators: 
    - Exponential Moving Average (EMA)
    - Relative Strength Index (RSI)

Strategy Description:
    This strategy combines the EMA and RSI indicators to identify potential trading opportunities.
    When the closing price is above the EMA and the RSI is above 70, the strategy enters a long position.
    When the closing price is below the EMA and the RSI is below 30, the strategy enters a short position.
    The strategy includes mechanisms to exit trades when the closing price crosses below the EMA for long positions or above the EMA for short positions.

Entry:
    - Closing price is above the EMA and RSI is above 70, a long position is entered.
    - Closing price is below the EMA and RSI is below 30, a short position is entered.

Exit:
    - Closing price crosses below the EMA, a long position is exited.
    - Closing price crosses above the EMA, a short position is exited.
"""

from backtesting import Backtest, Strategy

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import warnings
import pandas as pd
import pandas_ta as ta

# filter all warnings
warnings.filterwarnings('ignore')  # Setting the warnings to be ignored

class Strategy_005(Strategy):
    ema_period = 20
    rsi_period = 14
    
    def init(self):
        close_series = pd.Series(self.data.Close)
        # Initialize the indicators
        self.ema = self.I(ta.ema, close_series, self.ema_period)
        self.rsi = self.I(ta.rsi, close_series, self.rsi_period)

    def next(self):
        # If the closing price is above the EMA and the RSI is above 70, and we're not already in a long position
        if (self.data.Close[-1] > self.ema[-1]) and (self.rsi[-1] > 70) and (not self.position.is_long):
            self.buy()
        
        # If the closing price is below the EMA and the RSI is below 30, and we're not already in a short position
        if (self.data.Close[-1] < self.ema[-1]) and (self.rsi[-1] < 30) and (not self.position.is_short):
            self.sell()
        
        # Close long position when the closing price crosses below the EMA
        if self.position.is_long and self.data.Close[-1] < self.ema[-1]:
            self.position.close()
        
        # Close short position when the closing price crosses above the EMA
        if self.position.is_short and self.data.Close[-1] > self.ema[-1]:
            self.position.close()



exchange = get_kucoin_connection()  # Establish connection to Kucoin
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)  # Fetch data from exchange

bt = Backtest(data_df, Strategy_005, cash=STARTING_CAPITAL, commission=COMMISSION)  # Set up the backtest
stats = bt.run()  # Run the backtest

bt.plot()  # Plot the backtest results

print(stats)  # Print the statistics of the backtest
