from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas as pd
import warnings

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_017(Strategy):
    def init(self):
        # Here you can precalculate any indicators or any heavy computations
        # Since the theory is based on price levels divisible by 0.25,
        # we do not need to precalculate any technical indicators.
        pass

    def next(self):
        price = self.data.Close[-1]  # Current closing price
        quarter_levels = [round(price - (price % 0.25)), round(price - (price % 0.25) + 0.25, 2)]
        
        # Long Entry
        if price > quarter_levels[1] and not self.position.is_long:
            self.buy(sl=quarter_levels[0], tp=quarter_levels[1] + 0.25)

        # Short Entry
        elif price < quarter_levels[0] and not self.position.is_short:
            self.sell(sl=quarter_levels[1], tp=quarter_levels[0] - 0.25)

        # Here you might add additional logic to handle trailing stop loss, etc.

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_017, cash=STARTING_CAPITAL, commission=COMMISSION, exclusive_orders=True)
stats = bt.run()

bt.plot()

print(stats)