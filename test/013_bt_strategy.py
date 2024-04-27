from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import pandas as pd
import warnings

# filter all warnings
warnings.filterwarnings('ignore')

class Strategy_013(Strategy):
    short_ema_period = 50
    long_ema_period = 200
    bb_period = 20
    bb_std_num = 2
    
    def init(self):
        # Initialize the indicators
        self.short_ema = self.I(pd.Series.ewm, self.data.Close, span=self.short_ema_period, min_periods=self.short_ema_period)
        self.long_ema = self.I(pd.Series.ewm, self.data.Close, span=self.long_ema_period, min_periods=self.long_ema_period)
        
        self.bb_mid = self.I(pd.Series.rolling, self.data.Close, self.bb_period).mean()
        self.bb_upper = self.bb_mid + self.data.Close.rolling(self.bb_period).std() * self.bb_std_num
        self.bb_lower = self.bb_mid - self.data.Close.rolling(self.bb_period).std() * self.bb_std_num
        
    def next(self):
        # Check for long entry
        if crossover(self.short_ema, self.long_ema) and self.data.Close[-1] < self.bb_lower[-1]:
            self.buy()
            
        # Check for short entry
        elif crossover(self.long_ema, self.short_ema) and self.data.Close[-1] > self.bb_upper[-1]:
            self.sell()
        
        # Check for long exit
        for trade in self.trades:
            if trade.is_long:
                if self.data.Close[-1] > self.bb_upper[-1]:
                    trade.close()
                elif crossover(self.long_ema, self.short_ema):
                    trade.close()
            elif trade.is_short:
                if self.data.Close[-1] < self.bb_lower[-1]:
                    trade.close()
                elif crossover(self.short_ema, self.long_ema):
                    trade.close()

exchange = get_kucoin_connection()
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)

bt = Backtest(data_df, Strategy_013, cash=STARTING_CAPITAL, commission=COMMISSION, exclusive_orders=True)
stats = bt.run()

bt.plot()

print(stats)