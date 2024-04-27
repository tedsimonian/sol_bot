"""
Strategy_006

Technical Indicators: 
    - Bollinger Bands (BB)
    - Average True Range (ATR)

Strategy Description:
    This strategy utilizes Bollinger Bands and Average True Range (ATR) to identify potential trading opportunities.
    When the closing price crosses below the upper Bollinger Band and the ATR is above a certain threshold, the strategy enters a long position.
    When the closing price crosses above the lower Bollinger Band and the ATR is above a certain threshold, the strategy enters a short position.
    The strategy includes mechanisms to exit trades when the closing price crosses above the lower Bollinger Band for long positions or below the upper Bollinger Band for short positions.

Entry:
    - Closing price crosses below the upper Bollinger Band and ATR is above a certain threshold, a long position is entered.
    - Closing price crosses above the lower Bollinger Band and ATR is above a certain threshold, a short position is entered.

Exit:
    - Closing price crosses above the lower Bollinger Band, a long position is exited.
    - Closing price crosses below the upper Bollinger Band, a short position is exited.
"""

from backtesting import Backtest, Strategy

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas as pd
import pandas_ta as ta
import warnings

# filter all warnings
warnings.filterwarnings('ignore')  # Setting the warnings to be ignored

class Strategy_006(Strategy):
    bb_period = 20
    atr_period = 14
    
    def init(self):
        close_series = pd.Series(self.data.Close)
        high_series = pd.Series(self.data.High)
        low_series = pd.Series(self.data.Low)
        # Initialize the indicators
        self.bb = self.I(ta.bbands, close_series, self.bb_period)
        self.atr = self.I(ta.atr, high_series, low_series, close_series, self.atr_period)

    def next(self):
        # If the closing price crosses below the upper Bollinger Band and the ATR is above a certain threshold, and we're not already in a long position
        if (self.bb[-1] == 1) and (self.atr[-1] > 0.5 * self.data.Close[-1]) and (not self.position.is_long):
            self.buy()
        
        # If the closing price crosses above the lower Bollinger Band and the ATR is above a certain threshold, and we're not already in a short position
        if (self.bb[-1] == -1) and (self.atr[-1] > 0.5 * self.data.Close[-1]) and (not self.position.is_short):
            self.sell()
        
        # Close long position when the closing price crosses above the lower Bollinger Band
        if self.position.is_long and (self.bb[-1] == -1):
            self.position.close()
        
        # Close short position when the closing price crosses below the upper Bollinger Band
        if self.position.is_short and (self.bb[-1] == 1):
            self.position.close()



exchange = get_kucoin_connection()  # Establish connection to Kucoin
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)  # Fetch data from exchange

bt = Backtest(data_df, Strategy_006, cash=STARTING_CAPITAL, commission=COMMISSION)  # Set up the backtest
stats = bt.run()  # Run the backtest

bt.plot()  # Plot the backtest results

print(stats)  # Print the statistics of the backtest
