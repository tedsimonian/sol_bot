"""
Strategy_008

Technical Indicators:
    - Moving Average Convergence Divergence (MACD)
    - Exponential Moving Average (EMA)

Strategy Description:
    This strategy combines the MACD and EMA indicators to identify potential trading opportunities. 
    It utilizes the MACD histogram to generate buy and sell signals based on crossovers between the MACD and its signal line. 
    Additionally, it incorporates a moving average filter to confirm entry signals. 
    The strategy implements stop-loss and take-profit mechanisms to manage risk and maximize profits.

Entry:
    - Buy signal: MACD line crosses above the signal line and the MACD histogram is positive for a certain number of periods. Additionally, the closing price is above a moving average filter.
    - Sell signal: Signal line crosses above the MACD line and the MACD histogram is negative for a certain number of periods.

Exit:
    - Stop Loss: Close position if the current price falls below a certain percentage of the entry price for long positions or rises above a certain percentage for short positions.
    - Take Profit: Close position if the current price rises above a certain percentage of the entry price for long positions or falls below a certain percentage for short positions.
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from utilities import fetch_data_from_exchange
from connector import get_kucoin_connection
from constants import COMMISSION, LIMIT, STARTING_CAPITAL, SYMBOL, TIMEFRAME

import warnings
import pandas_ta as ta
import pandas as pd

# filter all warnings
warnings.filterwarnings('ignore')  # Setting the warnings to be ignored

class Strategy_008(Strategy):
    short_ema_period = 12
    long_ema_period = 26
    signal_ema_period = 9
    buy_confirmation_periods = 2
    sell_confirmation_periods = 2
    additional_ma_filter_period = 50
    stop_loss_percent = 5
    take_profit_percent = 10
    
    def init(self):
        closing_prices = self.data.Close
        
        self.macd = self.I(self.MACD, closing_prices,
                           self.short_ema_period,
                           self.long_ema_period)
        
        self.signal = self.I(self.EMA, self.macd, self.signal_ema_period)
        
        self.histogram = self.macd - self.signal
        
        self.ma_filter = self.I(self.EMA, closing_prices,
                                self.additional_ma_filter_period)
    
    def next(self):
        if crossover(self.macd, self.signal) and all(self.histogram[-self.buy_confirmation_periods:] > 0):
            if self.data.Close[-1] > self.ma_filter[-1]:
                self.buy()
        elif crossover(self.signal, self.macd) and all(self.histogram[-self.sell_confirmation_periods:] < 0):
            self.sell()
    
    @staticmethod
    def MACD(prices, n_fast, n_slow):
        ema_fast = pd.Series(prices).ewm(span=n_fast, adjust=False).mean()
        ema_slow = pd.Series(prices).ewm(span=n_slow, adjust=False).mean()
        return ema_fast - ema_slow
    
    @staticmethod
    def EMA(prices, n):
        return pd.Series(prices).ewm(span=n, adjust=False).mean()
    
    def stop(self):
        # Implement Stop Loss and Take Profit
        for trade in self.trades:
            if trade.is_long:
                if self.data.Close[-1] < trade.entry_price * (1 - self.stop_loss_percent / 100):
                    self.position.close()
                elif self.data.Close[-1] > trade.entry_price * (1 + self.take_profit_percent / 100):
                    self.position.close()
            elif trade.is_short:
                if self.data.Close[-1] > trade.entry_price * (1 + self.stop_loss_percent / 100):
                    self.position.close()
                elif self.data.Close[-1] < trade.entry_price * (1 - self.take_profit_percent / 100):
                    self.position.close()



exchange = get_kucoin_connection()  # Establish connection to Kucoin
data_df = fetch_data_from_exchange(exchange, SYMBOL, TIMEFRAME, LIMIT)  # Fetch data from exchange

bt = Backtest(data_df, Strategy_008, cash=STARTING_CAPITAL, commission=COMMISSION)  # Set up the backtest
stats = bt.run()  # Run the backtest

bt.plot()  # Plot the backtest results

print(stats)  # Print the statistics of the backtest
