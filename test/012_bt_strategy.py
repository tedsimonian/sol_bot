from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import warnings

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_012(Strategy):
    def init(self):
        # Initialization logic, e.g.:
        # self.waves = self.I(self.detect_waves, self.data['Close'])
        pass

    def detect_waves(self, data):
        # This function should implement Elliott Wave detection,
        # which requires in-depth pattern recognition and analysis.
        pass

    def next(self):
        # In a real strategy, we would analyze waves here and make trade decisions
        
        # Example (simplified trade logic for illustration only):
        if len(self.trades) == 0:
            # Trying to buy at the end of what might be a Wave 2
            # For the actual strategy, a Fibonacci retracement could be used to determine entry
            if self.data.Close[-1] > self.data.Close[-2]:
                self.buy()

        elif self.trades:
            # Exiting the trade at the end of what might be a Wave 5
            # The actual strategy should use Elliott Wave and Fibonacci extension to determine exit
            if self.data.Close[-1] < self.data.Close[-2]:
                self.position.close()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_012, cash=STARTING_CAPITAL, commission=COMMISSION, exclusive_orders=True)
stats = bt.run()

bt.plot()

print(stats)