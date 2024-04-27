from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas as pd
import warnings

# filter all warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

class Strategy_019(Strategy):
    # Define the parameters for the strategy
    sma_period = 20
    adx_period = 14
    bollinger_period = 20
    bollinger_std_dev = 2
    volume_threshold = 1000000
    minimum_adx = 20
    
    def init(self):
        # Initialize indicators
        self.sma = self.I(SMA, self.data.Close, self.sma_period)
        self.adx = self.I(adx_indicator, self.data.High, 
                          self.data.Low, self.data.Close, self.adx_period)
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(bollinger_bands, 
                                                              self.data.Close, 
                                                              self.bollinger_period, 
                                                              self.bollinger_std_dev)
        self.bb_width = self.I(bollinger_band_width, 
                               self.bb_upper, self.bb_lower)
        self.avg_bb_width = self.I(SMA, self.bb_width, self.bollinger_period)
        
    def next(self):
        # Long Entry Condition
        if (crossover(self.data.Close, self.sma) and
                self.adx[-1] > self.minimum_adx and
                self.bb_width[-1] < self.avg_bb_width[-1] and
                self.data.Volume[-1] > self.volume_threshold):
            self.buy()
            
        # Short Entry Condition
        elif (crossover(self.sma, self.data.Close) and
                self.adx[-1] > self.minimum_adx and
                self.bb_width[-1] < self.avg_bb_width[-1] and
                self.data.Volume[-1] > self.volume_threshold):
            self.sell()
        
        # Long Exit Condition
        for trade in self.trades:
            if trade.is_long:
                if (crossover(self.sma, self.data.Close) or
                        self.adx[-1] < self.minimum_adx or
                        self.bb_width[-1] > self.avg_bb_width[-1]):
                    self.position.close()
                    
        # Short Exit Condition
            if trade.is_short:
                if (crossover(self.data.Close, self.sma) or
                        self.adx[-1] < self.minimum_adx or
                        self.bb_width[-1] > self.avg_bb_width[-1]):
                    self.position.close()


def adx_indicator(high, low, close, n):
    """Calculate ADX with the given parameter n"""
    # Implementation of the ADX indicator
    # ...

def bollinger_bands(close, n, k):
    """Calculate Bollinger Bands with the given parameters n and k"""
    # Implementation of Bollinger Bands
    # ...

def bollinger_band_width(upper, lower):
    """Calculate the width between Bollinger Bands"""
    # Implementation to calculate the width
    # ...


exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_019, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)