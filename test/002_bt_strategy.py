"""
Strategy_002

Technical Indicators: 
    - Average Directional Index (ADX)

Strategy Description:
    This strategy is based on the Average Directional Index (ADX) indicator to identify potential trading opportunities.
    When the ADX rises above a certain threshold, the strategy buys the market. When the ADX falls below a certain threshold, the strategy sells the market.
    The strategy also includes a mechanism to exit trades when the ADX drops below a certain threshold.

Entry:
    - ADX rises above a certain threshold and +DI crosses above -DI, a long position is entered.
    - ADX rises above a certain threshold and -DI crosses above +DI, a short position is entered.

Exit:
    - When ADX drops below a certain threshold, a long position is exited.
    - When ADX drops below a certain threshold, a short position is exited.
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

class Strategy_002(Strategy):
    adx_period = 14
    di_period = 14
    adx_threshold = 25
    exit_threshold = 20

    def init(self):
        high = self.data.High
        low = self.data.Low
        close = self.data.Close
        
        self.adx = self.I(talib.ADX, high, low, close, self.adx_period)
        self.plus_di = self.I(talib.PLUS_DI, high, low, close, self.di_period)
        self.minus_di = self.I(talib.MINUS_DI, high, low, close, self.di_period)

    def next(self):
        if crossover(self.plus_di, self.minus_di) and self.adx[-1] > self.adx_threshold:
            self.buy()
        elif crossover(self.minus_di, self.plus_di) and self.adx[-1] > self.adx_threshold:
            self.sell()

        for trade in self.trades:
            if trade.is_long and (
                crossover(self.minus_di, self.plus_di)
                or self.adx[-1] < self.exit_threshold
            ):
                trade.close()
            elif trade.is_short and (
                crossover(self.plus_di, self.minus_di)
                or self.adx[-1] < self.exit_threshold
            ):
                trade.close()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_002, cash=STARTING_CAPITAL, commission=COMMISSION, exclusive_orders=True)
stats = bt.run()

bt.plot()

print(stats)