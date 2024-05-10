"""
Strategy_007

Technical Indicators: 
    - Parabolic SAR
    - Exponential Moving Average (EMA) 
    - Moving Average Convergence Divergence (MACD)
    - Relative Strength Index (RSI)

Timeframe: 
    - 2h

Buy (Long) Entry:
    - Enter a buy trade when the price is above the EMA, indicating an upward trend.
    - Confirm the buy signal by observing the Parabolic SAR indicating an upward trend and the MACD Delta being positive.

Buy (Long) Exit:
    - Open a sell trade when the price is below the EMA, signaling a downward trend.
    - Confirm the sell signal by noting the Parabolic SAR indicating a downward trend and the MACD Delta being negative.
    
"""

from backtesting import Backtest, Strategy

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL

import pandas as pd
import pandas_ta as ta
import warnings

# filter all warnings
warnings.filterwarnings('ignore')  # Setting the warnings to be ignored

TIMEFRAME = '2h'

class Strategy_007(Strategy):
    ema_period = 200
    rsi_period = 14
    
    def init(self):
        close_series = pd.Series(self.data.Close)
        high_series = pd.Series(self.data.High)
        low_series = pd.Series(self.data.Low)
        
        self.ema = self.I(ta.ema, close_series, self.ema_period)
        self.macd = self.I(ta.macd, close_series)
        self.psar = self.I(ta.psar, high_series, low_series, close_series)
        self.rsi = self.I(ta.rsi, close_series, self.rsi_period)

    def next(self):        
        # If the price is above the EMA, 
        # confirm long by observing the Parabolic SAR indicating an upward trend (psar == 1) 
        # the MACD Delta being positive
        # and the RSI being above 70
        if self.data.Close[-1] > self.ema[-1] and self.psar[-1] == 1 and self.macd[-1] > 0 and self.rsi[-1] > 70:
            self.buy()

                
        # If the price is below the EMA,
        # confirm the sell signal by observing the Parabolic SAR indicating a downward trend (psar == 0)
        # the MACD Delta being negative
        # and the RSI being below 30
        if self.data.Close[-1] < self.ema[-1] and self.psar[-1] == 0 and self.macd[-1] < 0 and self.rsi[-1] < 30:
            self.position.close()
        


exchange = get_kucoin_connection()  # Establish connection to Kucoin
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)  # Fetch data from exchange

bt = Backtest(data_df, Strategy_007, cash=STARTING_CAPITAL, commission=COMMISSION)  # Set up the backtest
stats = bt.run()  # Run the backtest

bt.plot()  # Plot the backtest results

print(stats)  # Print the statistics of the backtest
