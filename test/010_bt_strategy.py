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

class Strategy_010(Strategy):
    n1 = 20  # 20 day period for the SMA
    n2 = 50  # 50 day period for the trend filter SMA
    n_std_dev = 2

    def init(self):
        self.sma = self.I(SMA, self.data.Close, self.n1)
        self.upper_band = self.I(lambda data: SMA(data, self.n1) + self.n_std_dev * pd.Series(data).rolling(self.n1).std(), self.data.Close)
        self.lower_band = self.I(lambda data: SMA(data, self.n1) - self.n_std_dev * pd.Series(data).rolling(self.n1).std(), self.data.Close)
        self.trend_sma = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.data.Close, self.lower_band) and self.data.Close[-1] > self.trend_sma[-1]:
            self.buy()
            
        if crossover(self.upper_band, self.data.Close) and self.data.Close[-1] < self.trend_sma[-1]:
            self.sell()

        for trade in self.trades:
            if trade.is_long and crossover(self.sma, self.data.Close):
                self.position.close()
            elif trade.is_short and crossover(self.data.Close, self.sma):
                self.position.close()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_010, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)