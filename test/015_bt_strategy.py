from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas as pd
import warnings

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_015(Strategy):
    tenkan_period = 9
    kijun_period = 26
    senkou_span_b_period = 52
    displacement = 26
    
    def init(self):
        self.tenkan_sen = self.I(lambda x: (x.high.rolling(self.tenkan_period).max() + x.low.rolling(self.tenkan_period).min()) / 2, self.data)
        self.kijun_sen = self.I(lambda x: (x.high.rolling(self.kijun_period).max() + x.low.rolling(self.kijun_period).min()) / 2, self.data)
        self.senkou_span_a = self.I(lambda x: ((self.tenkan_sen + self.kijun_sen) / 2).shift(self.displacement), self.data)
        self.senkou_span_b = self.I(lambda x: (x.high.rolling(self.senkou_span_b_period).max() + x.low.rolling(self.senkou_span_b_period).min()) / 2, self.data)
        self.chikou_span = self.I(lambda x: x.close.shift(-self.displacement), self.data)
        
    def next(self):
        # Conditions for a long trade
        if (self.data.Close[-1] > self.senkou_span_a[-1] and 
            self.data.Close[-1] > self.senkou_span_b[-1] and
            crossover(self.tenkan_sen, self.kijun_sen) and
            self.data.Close[-self.displacement] < self.chikou_span[-1]):
            self.buy()
            
        # Conditions for closing a long trade
        if (self.position.is_long and ((self.data.Close < self.kijun_sen or 
                                        self.data.Close < self.senkou_span_b) or
                                       crossover(self.kijun_sen, self.tenkan_sen))):
            self.position.close()
        
        # Conditions for a short trade
        if (self.data.Close[-1] < self.senkou_span_a[-1] and 
            self.data.Close[-1] < self.senkou_span_b[-1] and
            crossover(self.kijun_sen, self.tenkan_sen) and
            self.data.Close[-self.displacement] > self.chikou_span[-1]):
            self.sell()
            
        # Conditions for closing a short trade
        if (self.position.is_short and ((self.data.Close > self.kijun_sen or 
                                         self.data.Close > self.senkou_span_a) or
                                        crossover(self.tenkan_sen, self.kijun_sen))):
            self.position.close()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_015, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)