"""
Strategy_009

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

from utilities import fetch_data_from_exchange
from connector import get_phemex_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL

import talib
import warnings

# filter all warnings
warnings.filterwarnings('ignore')

TIMEFRAME = "1d"

class Strategy_009(Strategy):
    bb_length = 20
    bb_mult = 2.0
    kc_length = 20
    kc_mult = 1.5
    use_true_range = True

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        self.bb_basis = self.I(talib.SMA, close, self.bb_length)
        self.bb_dev = self.I(lambda x: talib.STDDEV(x, self.bb_length) * self.kc_mult, close)
        self.bb_upper = self.bb_basis + self.bb_dev
        self.bb_lower = self.bb_basis - self.bb_dev

        self.kc_ma = self.I(talib.SMA, close, self.kc_length)
        if self.use_true_range:
            self.kc_range = self.I(talib.TRANGE, high, low, close)
        else:
            self.kc_range = high - low
        self.kc_range_ma = self.I(talib.SMA, self.kc_range, self.kc_length)
        self.kc_upper = self.kc_ma + self.kc_range_ma * self.kc_mult
        self.kc_lower = self.kc_ma - self.kc_range_ma * self.kc_mult

        def linreg_val():
            highest_high = talib.MAX(high, self.kc_length)
            lowest_low = talib.MIN(low, self.kc_length)
            avg_price = (highest_high + lowest_low + talib.SMA(close, self.kc_length)) / 3
            return talib.LINEARREG(close - talib.SMA(avg_price, self.kc_length), self.kc_length)
        
        self.linreg_val = self.I(linreg_val)
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

exchange = get_phemex_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_009, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)
