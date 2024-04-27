from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas as pd
import warnings

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_016(Strategy):
    def init(self):
        super().init()
        # This strategy requires previous day's high, low and close values
        # These would likely be obtained from an external source such as a CSV file or database
        # Assuming that we've loaded this data into our strategy
        self.previous_high = self.data.High.shift(1)
        self.previous_low = self.data.Low.shift(1)
        self.previous_close = self.data.Close.shift(1)

    def next(self):
        super().next()

        # Formulas for Pivot Points
        PP = (self.previous_high + self.previous_low + self.previous_close) / 3
        R1 = (2 * PP) - self.previous_low
        S1 = (2 * PP) - self.previous_high
        R2 = PP + (self.previous_high - self.previous_low)
        S2 = PP - (self.previous_high - self.previous_low)

        if not self.position:
            # Buy Signal: Price moves above pivot point and consolidates
            if self.data.Close > PP and not self.position.is_long:
                self.buy(sl=S1, tp=R1)

            # Sell Signal: Price moves below pivot point and consolidates
            elif self.data.Close < PP and not self.position.is_short:
                self.sell(sl=R1, tp=S1)

        else:
            # Adjust stop loss and take profit for long position
            if self.position.is_long:
                if self.data.High >= R1:
                    self.position.close()
                else:
                    if self.data.Low < S1:
                        self.position.close()
            # Adjust stop loss and take profit for short position
            elif self.position.is_short:
                if self.data.Low <= S1:
                    self.position.close()
                else:
                    if self.data.High > R1:
                        self.position.close()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_016, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)