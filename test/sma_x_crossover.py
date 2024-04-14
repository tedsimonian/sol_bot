import backtrader as bt
import pandas as pd

from back_testing import run_back_test

class SmaCrossStrategy(bt.SignalStrategy):
    def __init__(self): 
        # when simple moving average crosses the price, can change the number
        sma = bt.ind.SMA(period=20)
        # this grabs the price data from the excel
        price = self.data
        # this defines the cross over.. price and sma
        crossover = bt.ind.CrossOver(price, sma)
        # this tells the code to LONG when it crossover, which is defined above
        self.signal_add(bt.SIGNAL_LONG, crossover)

data_path = 'test/data/storage_SOL-USD6h20.csv'

dataframe = pd.read_csv(data_path,
                        parse_dates=True,
                        index_col=0)
data = bt.feeds.PandasData(dataname=dataframe)

run_back_test(SmaCrossStrategy, data, 10000, 0.001, bt.sizers.AllInSizer, 95)