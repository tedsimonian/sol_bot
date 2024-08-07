"""
Strategy_010

Technical indicators:
    - Bollinger Bands
    - Keltner Channels
    - Linear Regression

Strategy Description:
    This strategy uses the Squeeze Momentum Indicator to determine entry and exit points based on Bollinger Bands and Keltner Channels.
    The strategy enters a long position when the squeeze momentum turns positive and exits when the squeeze condition changes.
    It enters a short position when the squeeze momentum turns negative and exits when the squeeze condition changes.

Entry:
    - Long: When the squeeze condition changes from "on" to "off" and the squeeze momentum is positive.
    - Short: When the squeeze condition changes from "on" to "off" and the squeeze momentum is negative.

Exit:
    - Long: When the squeeze condition changes and the current position is long.
    - Short: When the squeeze condition changes and the current position is short.
"""

from backtesting import Backtest, Strategy 
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import talib
import numpy as np
import pandas as pd
import warnings 

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_010(Strategy):
    bb_length = 20
    bb_mult = 2.0
    kc_length = 20
    kc_mult = 1.5

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        self.bb_basis = self.I(talib.SMA, close, self.bb_length)
        self.bb_dev = self.I(lambda x: talib.STDDEV(x, self.bb_length) * self.kc_mult, close)
        self.bb_upper = self.bb_basis + self.bb_dev
        self.bb_lower = self.bb_basis - self.bb_dev

        self.kc_ma = self.I(talib.SMA, close, self.kc_length)
        self.kc_range = self.I(lambda x: talib.TRANGE(high, low, close) if useTrueRange else (high - low))
        self.kc_range_ma = self.I(talib.SMA, self.kc_range, self.kc_length)
        self.kc_upper = self.kc_ma + self.kc_range_ma * self.kc_mult
        self.kc_lower = self.kc_ma - self.kc_range_ma * self.kc_mult

        self.linreg_val = self.I(lambda x: talib.LINEARREG(close - talib.SMA((talib.MAX(high, self.kc_length) + talib.MIN(low, self.kc_length) + talib.SMA(close, self.kc_length)) / 3, self.kc_length), self.kc_length), close)
        self.sqz_on = self.I(lambda: (self.bb_lower > self.kc_lower) & (self.bb_upper < self.kc_upper))
        self.sqz_off = self.I(lambda: (self.bb_lower < self.kc_lower) & (self.bb_upper > self.kc_upper))
        self.no_sqz = self.I(lambda: ~(self.sqz_on | self.sqz_off))

    def next(self):
        long_entry_condition = (self.no_sqz[-1] == 1) & (self.sqz_on == 1) & (self.linreg_val > 0)
        long_exit_condition = (self.no_sqz[-1] != self.no_sqz) & (self.position.is_long)

        short_entry_condition = (self.no_sqz[-1] == 1) & (self.sqz_on == 1) & (self.linreg_val < 0)
        short_exit_condition = (self.no_sqz[-1] != self.no_sqz) & (self.position.is_short)

        if long_entry_condition:
            self.buy()

        if long_exit_condition:
            self.position.close()

        if short_entry_condition:
            self.sell()

        if short_exit_condition:
            self.position.close()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_010, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)
