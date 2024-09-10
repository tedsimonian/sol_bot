"""
Strategy_001

Technical indicators:
    - Bollinger Bands
    - Stochastic RSI

Strategy Description:
    This strategy is based on the Bollinger Bands and the Stochastic RSI indicator. 
    The strategy is a long-only strategy and is designed to be used with a short-term investment horizon.

Entry:
    - When the price closes above the upper Bollinger Band and the stochastic RSI K crosses above the stochastic RSI D, a long position is entered.
    - When the price closes below the lower Bollinger Band and the stochastic RSI K crosses below the stochastic RSI D, a short position is entered.

Exit:
    - When the price closes below the lower Bollinger Band, a short position is exited.
    - When the price closes above the upper Bollinger Band, a long position is exited.
"""


from backtesting import Backtest, Strategy 
from backtesting.lib import crossover 

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas_ta as ta 
import warnings 

# filter all warnings
warnings.filterwarnings('ignore')

FACTOR = 1000 # conversion factor 

class Strategy_001(Strategy):
    rsi_window = 14 
    stochrsi_smooth1 = 3 
    stochrsi_smooth2 = 3 
    bbands_length = 20 
    stochrsi_length = 14 
    bbands_std = 2 

    def init(self):
        self.bbands = self.I(bands, self.data)
        self.stoch_rsi_k = self.I(stoch_rsi_k, self.data)
        self.stoch_rsi_d = self.I(stoch_rsi_d, self.data)
        self.buy_price = 0 

    def next(self):
        lower = self.bbands[0] # lower bollinger band 
        mid = self.bbands[1] # middle bollinger band
        upper = self.bbands[2] # upper bollinger band

        # check for entry long positions
        if (self.data.Close[-1] > lower[-1] and crossover(self.stoch_rsi_k, self.stoch_rsi_d)):
            self.buy(size=0.05, sl=self.data.Close[-1] * 0.85, tp=self.data.Close[-1] * 1.40)
            self.buy_price = self.data.Close[-1]


def bands(data):
    bbands = ta.bbands(close=data.Close.s, length=20, std=2)
    return bbands.to_numpy().T

def stoch_rsi_k(data):
    stochrsi = ta.stochrsi(close=data.Close.s, k=3, d=3)
    return stochrsi['STOCHRSIk_14_14_3_3'].to_numpy()

def stoch_rsi_d(data):
    stochrsi = ta.stochrsi(close=data.Close.s, k=3, d=3)
    return stochrsi['STOCHRSId_14_14_3_3'].to_numpy()


exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

data_df.Open /= FACTOR
data_df.High /= FACTOR 
data_df.Low /= FACTOR 
data_df.Close /= FACTOR 
data_df.Volume *= FACTOR 

bt = Backtest(data_df, Strategy_001, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)