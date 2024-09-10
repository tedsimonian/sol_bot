"""
Strategy_004

Technical Indicators:
    - Simple Moving Average (SMA)
    - Volume Weighted Average Price (VWAP)

Strategy Description:
    This strategy aims to capitalize on the momentum shifts indicated by the relationship between the closing price, SMA, and VWAP. The strategy enters a long position when the closing price is below both the SMA and VWAP, suggesting a potential upward reversal. Conversely, it enters a short position when the closing price is above both indicators, indicating a potential downward reversal. The strategy exits positions when the closing price crosses back over these indicators, aiming to capture profits from short-term fluctuations in price.

Entry:
    - When the Closing Price is lower than both the 15-day VWAP and the 5-day SMA, and the Closing Price is lower than the Closing Price from the last two days.
    - Closing Price < 15-day VWAP
    - Closing Price < 5-day SMA
    - Closing Price < Closing Price from the last two days

Exit:
    - When the Closing Price is greater than both the 15 days VWAP and the 5 days SMA, and the Closing Price is greater than the Closing Price from the last two days.
    - Closing Price > 15-day VWAP
    - Closing Price > 5-day SMA
    - Closing Price > Closing Price from the last two days
"""


from backtesting import Backtest, Strategy
from talib import SMA

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import warnings
import ta

# filter all warnings
warnings.filterwarnings('ignore')  # Setting the warnings to be ignored

class Strategy_004(Strategy):
    sma_period = 14
    vwap_period = 30
    
    def init(self):
        def VWAP(df, window):
            high = df['High']
            low = df['Low']
            close = df['Close']
            volume = df['Volume']
            
            vwap = ta.volume.VolumeWeightedAveragePrice(high, low, close, volume, window)
            vwap_values = vwap.volume_weighted_average_price()
            
            return vwap_values
        
        # Initialize the indicators
        self.sma = self.I(SMA, self.data.Close, self.sma_period)
        self.vwap = self.I(VWAP, self.data.df, self.vwap_period)

    def next(self):
        # If the closing price is below the 5-day SMA and the 15-day VWAP, and we're not already in a long position
        if (self.data.Close[-1] < self.sma[-1]) and (self.data.Close[-1] < self.vwap[-1]) and (not self.position.is_long):
            self.buy()
        
        # If the closing price is above the 5-day SMA and the 15-day VWAP, and we're not already in a short position
        if (self.data.Close[-1] > self.sma[-1]) and (self.data.Close[-1] > self.vwap[-1]) and (not self.position.is_short):
            self.sell()
        
        # Close long position when the closing price is above the 5-day SMA and the 15-day VWAP
        if self.position.is_long and self.data.Close[-1] > self.sma[-1] and self.data.Close[-1] > self.vwap[-1]:
            self.position.close()
        
        # Close short position when the closing price is below the 5-day SMA and the 15-day VWAP
        if self.position.is_short and self.data.Close[-1] < self.sma[-1] and self.data.Close[-1] < self.vwap[-1]:
            self.position.close()


exchange = get_kucoin_connection()  # Establish connection to Kucoin
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)  # Fetch data from exchange

bt = Backtest(data_df, Strategy_004, cash=STARTING_CAPITAL, commission=COMMISSION)  # Set up the backtest
stats = bt.run()  # Run the backtest

bt.plot()  # Plot the backtest results

print(stats)  # Print the statistics of the backtest
