import backtrader as bt
import pandas as pd

from back_testing import run_back_test

class SolanaStrategy(bt.Strategy):
    def __init__(self):
        self.rsi = bt.ind.RSI(self.data.close, period=14)
        self.bb = bt.ind.BollingerBands(self.data.close, period=14)
        self.ema_short = bt.ind.ExponentialMovingAverage(self.data.close, period=5)
        self.ema_medium = bt.ind.ExponentialMovingAverage(self.data.close, period=20)
        self.stoploss = 0
        self.takeprofit = 0

    def next(self):

        if not self.position:
            if self.data.close <= self.stoploss or self.data.close >= self.takeprofit:
                self.close()
            if (self.ema_short > self.ema_medium or self.data.close < self.bb.lines.bot) and self.rsi <= 31:
                self.buy()
                self.stoploss = self.data.close * 0.925
                self.takeprofit = self.data.close * 1.25
        else:
            if (self.ema_short < self.ema_medium or self.data.close > self.bb.lines.top) and self.rsi >= 68:
                self.close()

data_path = 'test/data/storage_SOL-USD6h20.csv'

dataframe = pd.read_csv(data_path,
                        parse_dates=True,
                        index_col=0)
data = bt.feeds.PandasData(dataname=dataframe)

run_back_test(SolanaStrategy, data, 10000, 0.001, bt.sizers.AllInSizer, 95)