import pandas as pd 
from ccxt import Exchange


def fetch_data_from_exchange(exchange: Exchange, symbol: str, timeframe: str, limit: int = 2000, columns: list = ['timestamp', 'open', 'high', 'low', 'close', 'volume']) -> pd.DataFrame:
    """Fetch data from the exchange

    Args:
        exchange (Exchange): Exchange to fetch data from. I.e. ccxt.phemex()
        symbol (str): Symbol to fetch data for. I.e. 'BTCUSD' or 'SOL/USDT' (depends on your exchange)
        timeframe (str): Timeframe to fetch data for. I.e. '1m', '5m', '15m', '1h', '2h', '1d', '1w'
        limit (int, optional): Number of data points to fetch. Defaults to 2000.
        columns (list, optional): Columns to fetch. Defaults to ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    Returns:
        pd.DataFrame: DataFrame with the data with the columns
    """
    
    since = exchange.milliseconds() - (limit * 60 * 60 * 1000)
    
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
    
    df = pd.DataFrame(ohlcv, columns=columns)
    df['timestamp']  = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    # uppercase columns name
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    return df 