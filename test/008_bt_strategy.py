"""
Strategy_008

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

import talib
import warnings 

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_008(Strategy):
    sma_period = 20
    
    def init(self):
        close = self.data.Close
        
        # when simple moving average crosses the price
        self.sma = self.I(talib.SMA, close, self.sma_period)
    
    def next(self):
        # this tells the code to buy (LONG) when it crossover
        if crossover(self.data.Close, self.sma):
            self.buy()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_008, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)