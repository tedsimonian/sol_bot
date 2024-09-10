"""
Strategy_003

Technical Indicators:
    - Bollinger Bands

Strategy Description:
    This strategy is based on the Bollinger Bands indicator and uses it to identify potential trading opportunities.

Entry:
    - When the price of the asset nears the upper band, the strategy buys the asset. 

Exit:
    - When the price of the asset nears the lower band, the strategy sells the asset.
"""

from backtesting import Backtest, Strategy  # Importing Backtest and Strategy classes from backtesting module
from backtesting.lib import crossover  # Importing crossover function from backtesting.lib module
from backtesting.test import SMA  # Importing SMA (Simple Moving Average) function from backtesting.test module

from utilities import fetch_data_from_exchange  # Importing function to fetch data from exchange
from connector import get_kucoin_connection  # Importing function to connect to Kucoin API
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME  # Importing constants used in the strategy

import warnings  # Importing warnings module to control warning messages
import pandas as pd  # Importing pandas library for data manipulation

# filter all warnings
warnings.filterwarnings('ignore')  # Setting the warnings to be ignored

class Strategy_003(Strategy):  # Defining the strategy class inheriting from Strategy
    sma_period_1 = 20  # period for the SMA
    sma_period_2 = 50  # period for the trend filter SMA
    n_std_dev = 2 # number of standard deviations

    def init(self):  # Initialization method to define indicators
        self.sma_1 = self.I(SMA, self.data.Close, self.sma_period_1)  # Simple moving average of closing prices
        self.upper_band = self.I(lambda data: SMA(data, self.sma_period_1) + self.n_std_dev * pd.Series(data).rolling(self.sma_period_1).std(), self.data.Close)  # Upper Bollinger Band
        self.lower_band = self.I(lambda data: SMA(data, self.sma_period_1) - self.n_std_dev * pd.Series(data).rolling(self.sma_period_1).std(), self.data.Close)  # Lower Bollinger Band
        self.trend_sma = self.I(SMA, self.data.Close, self.sma_period_2)  # Secondary SMA for trend filtering

    def next(self):  # Method called for each new data point
        if crossover(self.data.Close, self.lower_band) and self.data.Close[-1] > self.trend_sma[-1]:  # Buy condition
            self.buy()
            
        if crossover(self.upper_band, self.data.Close) and self.data.Close[-1] < self.trend_sma[-1]:  # Sell condition
            self.sell()

        for trade in self.trades:  # Loop through active trades to check for exit condition
            if trade.is_long and crossover(self.sma_1, self.data.Close):  # Close long trades
                self.position.close()
            elif trade.is_short and crossover(self.data.Close, self.sma_1):  # Close short trades
                self.position.close()

exchange = get_kucoin_connection()  # Establish connection to Kucoin
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)  # Fetch data from exchange

bt = Backtest(data_df, Strategy_003, cash=STARTING_CAPITAL, commission=COMMISSION)  # Set up the backtest
stats = bt.run()  # Run the backtest

bt.plot()  # Plot the backtest results

print(stats)  # Print the statistics of the backtest
