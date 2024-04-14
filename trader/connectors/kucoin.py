import ccxt;

params = {
    'enableRateLimit': True,
    'apiKey': 'YOUR_BINANCE_API_KEY',
    'secret': 'YOUR_BINANCE_SECRET',
}

def get_kucoin_connection():
    connection = ccxt.kucoin(params);
    return connection;