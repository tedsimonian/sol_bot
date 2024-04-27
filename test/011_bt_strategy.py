from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import warnings

# filter all warnings
warnings.filterwarnings('ignore')

# Dummy implementation of Elliott Wave and Pivot Points as these are complex algorithms not directly provided by backtesting.py.
# These would need to be implemented using price patterns and/or integrating with additional libraries or custom logic.
def identify_elliott_wave_pattern(data):
    """ Identify Elliott Wave pattern (dummy function, need actual implementation) """
    # Note: In a real implementation, you would use price action and possibly other technical indicators
    # to identify where the asset is in its Elliott Wave pattern.
    data['ElliottWave'] = 1  # Assume it's always in a wave suitable for trading for demo purposes.
    return data

def calculate_pivot_points(data):
    """ Calculate daily pivot points (dummy function, need actual implementation) """
    # Note: In a real implementation, you'll calculate pivot points based on past price data.
    # Here, we'll just make it static for demonstration purposes.
    data['Pivot'] = (data['High'] + data['Low'] + data['Close']) / 3
    data['R1'] = 2 * data['Pivot'] - data['Low']
    data['S1'] = 2 * data['Pivot'] - data['High']
    return data

class Strategy_011(Strategy):
    def init(self):
        # Prepare the data with necessary indicators and patterns
        self.data = calculate_pivot_points(self.data)
        self.data = identify_elliott_wave_pattern(self.data)
        
    def next(self):
        # Assuming there's only one ongoing trade at a time
        if not self.position:
            
            # Bullish scenario - Looking to buy
            if self.data.ElliottWave[-1] and self.data.Close[-1] > self.data.Pivot[-1] and self.data.Close[-1] < self.data.S1[-1]:
                self.buy(sl=self.data.S1[-1], tp=self.data.R1[-1])
            
            # Bearish scenario - Looking to sell
            elif not self.data.ElliottWave[-1] and self.data.Close[-1] < self.data.Pivot[-1] and self.data.Close[-1] > self.data.R1[-1]:
                self.sell(sl=self.data.R1[-1], tp=self.data.S1[-1])

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_011, cash=STARTING_CAPITAL, commission=COMMISSION)
stats = bt.run()

bt.plot()

print(stats)