import os
import ccxt

from dotenv import load_dotenv

load_dotenv(override=True)

binance_params = {
    'enableRateLimit': True,
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_SECRET'),
}

kucoin_params = {
    'enableRateLimit': True,
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_SECRET'),
    'password': os.getenv('KUCOIN_PASSWORD'),
}

phemex_params = {
    'enableRateLimit': True,
    'apiKey': os.getenv('PHEMEX_API_KEY'),
    'secret': os.getenv('PHEMEX_SECRET'),
}

def get_binance_connection():
    connection = ccxt.binance(binance_params)
    return connection


def get_phemex_connection():
    connection = ccxt.phemex(phemex_params)
    return connection


def get_kucoin_connection(is_futures=False):
    if is_futures:
        connection = ccxt.kucoinfutures(kucoin_params)
    else:
        connection = ccxt.kucoin(kucoin_params)
    return connection

