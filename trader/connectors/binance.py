import ccxt;

params = {
    'enableRateLimit': True,
    'apiKey': 'YOUR_BINANCE_API_KEY',
    'secret': 'YOUR_BINANCE_SECRET',
}

def get_binance_connection():
    connection = ccxt.binance(params);
    return connection;