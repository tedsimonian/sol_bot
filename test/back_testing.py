import logging
import inspect
import os
import sys

import pandas as pd
import backtrader as bt
import backtrader.analyzers as analyzers

def run_back_test(strategy: bt.Strategy, data: pd.DataFrame | bt.feeds.PandasData, start_amount: float, commission_rate: float, sizer: bt.Sizer, sizer_percentage: float):
    """
    Starts a back test with the given strategy, data, parameters and then plot it on a graph.

    Args:
        strategy (bt.Strategy): The strategy to use for the back test.
        data (pd.DataFrame): The data to use for the back test.
        start_amount (float): The starting amount to use for the back test.
        commission_rate (float): The commission rate to use for the back test.
        sizer (bt.Sizer): The sizer to use for the back test.
        sizer_percentage (float): The percentage of the account to use for the sizer.
    """
    
    # Get the name of the file calling this function
    caller_file_name = inspect.stack()[1].filename
    logger = logging.getLogger(caller_file_name)
    log_file_name = f"./test/logs/{os.path.basename(caller_file_name).replace('.py', '')}_backtest.log"
    # Ensure the logs directory exists
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)
    # Set up logger configuration
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=[
            logging.FileHandler(log_file_name),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Activate the engine
    cerebro = bt.Cerebro()
    
    # Add the strategy
    cerebro.addstrategy(strategy)
    
    # Add the data to the engine
    cerebro.adddata(data)
    
    # Set the starting cash
    cerebro.broker.setcash(start_amount)
    
    # Divide the percentage commission rate by 100 to get the decimal
    commission = commission_rate / 100
    
    # Set the commission rate
    cerebro.broker.setcommission(commission)
    
    # Set the sizer
    cerebro.addsizer(sizer, percents=sizer_percentage)
    
    # Add the analyzers
    cerebro.addanalyzer(analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(analyzers.Transactions, _name='tx')
    cerebro.addanalyzer(analyzers.TradeAnalyzer, _name='trades')
    
    # Run the engine
    analysis_result = cerebro.run()
    
    # Get the account balance
    final_account_balance = cerebro.broker.getvalue()
    
    # Get the results of our analyzers
    sharpe = analysis_result[0].analyzers.sharpe.get_analysis()
    transactions = analysis_result[0].analyzers.tx.get_analysis()
    trades = analysis_result[0].analyzers.trades.get_analysis()
    
    # We don't need all the transaction data, just how many there were
    tx_count = len(transactions)
    trade_count = len(trades)

    # Print the our info
    logger.info(f"""
        sharpe_ratio:          {sharpe['sharperatio']}
        tx_count:              {tx_count}
        trade_count:           {trade_count}
        start_account_balance: {start_amount}
        final_account_balance: {final_account_balance}
    """)
    
    # Plot the results onto a graph and display
    cerebro.plot()
