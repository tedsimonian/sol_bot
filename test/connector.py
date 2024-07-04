import os
import ccxt

from dotenv import load_dotenv

load_dotenv()

binance_params = {
    'enableRateLimit': True,
    'apiKey': os.getenv('BINANCE_BACKTEST_API_KEY'),
    'secret': os.getenv('BINANCE_BACKTEST_SECRET'),
}

kucoin_params = {
    'enableRateLimit': True,
    'apiKey': os.getenv('KUCOIN_BACKTEST_API_KEY'),
    'secret': os.getenv('KUCOIN_BACKTEST_SECRET'),
}

def get_binance_connection():
    connection = ccxt.binance(binance_params)
    return connection

def get_kucoin_connection():
    connection = ccxt.kucoin(kucoin_params);
    return connection;

