from pytz import timezone
from time import sleep, time
from ccxt import Exchange

import pandas as pd
import pandas_ta as ta
import math

symbol = 'BTC/USDT'
index_pos = 4 # CHANGE BASED ON WHAT ASSET

# the time between trades
pause_time = 60

# for volume calc Vol_repeat * vol_time == TIME of volume collection
vol_repeat=11
vol_time=5

pos_size = 100 # 125, 75, 
params = {'timeInForce': 'PostOnly'}
target = 35
max_loss = -55
vol_decimal = .4

# for df 
timeframe = '4h'
limit = 100
sma = 20


def df_sma(exchange: Exchange, symbol: str, timeframe: str, limit: int, sma: int) -> pd.DataFrame:

    """
    Fetches data from the exchange and calculates the SMA of the given symbol.

    Returns:
        pd.DataFrame: DataFrame with the data with the columns
    """

    print('starting indicator...')

    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df_sma = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_sma['timestamp'] = pd.to_datetime(df_sma['timestamp'], unit='ms')

    # DAILY SMA - 20 day
    df_sma[f'sma{sma}_{timeframe}'] = df_sma.close.rolling(sma).mean()

    # if bid < the 20 day sma then = BEARISH, if bid > 20 day sma = BULLISH
    bid = ask_bid(symbol)[1]
    
    # if sma > bid = SELL, if sma < bid = BUY
    df_sma.loc[df_sma[f'sma{sma}_{timeframe}']>bid, 'sig'] = 'SELL'
    df_sma.loc[df_sma[f'sma{sma}_{timeframe}']<bid, 'sig'] = 'BUY'

    df_sma['support'] = df_sma[:-2]['close'].min()
    df_sma['resistance'] = df_sma[:-2]['close'].max()
    df_sma['PC'] = df_sma['close'].shift(1)

    # last close Bigger than Previous close
    # going to add this to order to ensure we only open
    # order on reversal confirmation
    df_sma.loc[df_sma['close']>df_sma['PC'], 'lcBpc'] = True
                # 2.981       > 2.966 == True
    df_sma.loc[df_sma['close']<df_sma['PC'], 'lcBpc'] = False
                # 2.980       < 2.981 == False
                # 2.966       < 2.967 == False

    return df_sma


def order_book(exchange: Exchange, symbol: str) -> bool:

    print(f'fetching order book data for {symbol}... ')

    df = pd.DataFrame()
    temp_df = pd.DataFrame()

    ob = exchange.fetch_order_book(symbol)
    #print(ob)
    bids = ob['bids']
    asks = ob['asks']

    first_bid = bids[0]
    first_ask = asks[0]

    bid_vol_list = []
    ask_vol_list = []

    # if SELL vol > Buy vol AND profit target hit, exit
    # get last 1 min of volume.. and if sell > buy vol do x
    
    for x in range(11):

        for set in bids:
        #print(set)
            price = set[0]
            vol = set[1]
            bid_vol_list.append(vol)
            # print(price)
            # print(vol)

            #print(bid_vol_list)
            sum_bid_vol = sum(bid_vol_list)
            #print(sum_bid_vol)
            temp_df['bid_vol'] = [sum_bid_vol]

        for set in asks:
            #print(set)
            price = set[0] # [40000, 344]
            vol = set[1]
            ask_vol_list.append(vol)
            # print(price)
            # print(vol)

            sum_ask_vol = sum(ask_vol_list)
            temp_df['ask_vol'] = [sum_ask_vol]

        #print(temp_df)
        time.sleep(5) # change back to 5 later
        df = df.append(temp_df)
        print(df)
        print(' ')
        print('------')
        print(' ')
    print('done collecting volume data for bids and asks.. ')
    print('calculating the sums...')
    total_bid_vol = df['bid_vol'].sum()
    total_ask_vol = df['ask_vol'].sum()
    print(f'last 1m this is total Bid Vol: {total_bid_vol} | ask vol: {total_ask_vol}')

    if total_bid_vol > total_ask_vol:
        control_dec = (total_ask_vol/total_bid_vol )
        print(f'Bulls are in control: {control_dec}...')
        # if bulls are in control, use regular target
        bullish = True
    else:

        control_dec = (total_bid_vol / total_ask_vol)
        print(f'Bears are in control: {control_dec}...')
        bullish = False
        # .2 , .36, .2, .18, .4, .74, .24, .76

    # open_positions() open_positions, open_pos_bool, open_pos_size, long

    open_position = open_positions(exchange, symbol)
    open_pos_tf = open_position[1]
    long = open_position[3]
    print(f'open_pos_tf: {open_pos_tf} || long: {long}')

    if open_pos_tf == True:
        if long == True:
            print('we are in a long position...')
            if control_dec < vol_decimal: # vol_decimal set to .4 at top
                vol_under_dec = True
                
            else:
                print('volume is not under dec so setting vol_under_dec to False')
                vol_under_dec = False
        else:
            print('we are in a short position...')
            if control_dec < vol_decimal: # vol_decimal set to .4 at top
                vol_under_dec = True
                #print('going to sleep for a minute.. cuz under vol decimal')
                #time.sleep(6) # change to 60
            else:
                print('volume is not under dec so setting vol_under_dec to False')
                vol_under_dec = False
    else:
        print('we are not in position...')

    # when vol_under_dec == FALSE AND target hit, then exit
    print(vol_under_dec)

    return vol_under_dec


def get_candle_df(exchange: Exchange, symbol: str, timeframe: str, limit: int = 500, columns: list = ['time','open','high','low','close','volume']) -> pd.DataFrame:
    """Fetch data from the exchange

    Args:
        exchange (Exchange): Exchange to fetch data from. I.e. ccxt.phemex()
        symbol (str): Symbol to fetch data for. I.e. 'BTCUSD' or 'SOL/USDT' (depends on your exchange)
        timeframe (str): Timeframe to fetch data for. I.e. '1m', '5m', '15m', '1h', '2h', 'day', 'week'
        limit (int, optional): Number of data points to fetch. Defaults to 200.
        columns (list, optional): Columns to fetch. Defaults to ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    Returns:
        pd.DataFrame: DataFrame with the data with the columns
    """
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=columns)
    df.set_index('time')
    
    return df


def calc_stoch_rsi(df: pd.DataFrame, lookback: int = 14) -> None:
    """
    calculate and add the stock_rsi to the input dataframe
    """
    #use pandas_ta to calculate the rsi
    rsi = df.ta.rsi(length = lookback)
    
    # convert rsi to stoch rsi, equation: (current rsi - min rsi) / (max rsi - min rsi)
    df['stoch_rsi'] = (rsi.iloc[-1] - rsi.tail(lookback).min()) / (rsi.tail(lookback).max() - rsi.tail(lookback).min())


def calc_nadarya(df: pd.DataFrame, bandwidth: int = 8, source: str = 'close') -> tuple[bool, bool]:
    """
    calculate the nadarya indicator and return the most recent buy/sell signals
    """
    src = df[source]
    out = []
    
    for i, _v1 in src.items():
        tsum = 0
        sumw = 0
        for j, v2 in src.items():
            w = math.exp(-(math.pow(i-j,2)/(bandwidth * bandwidth * 2)))
            tsum += v2*w
            sumw += w
        out.append(tsum/sumw)
        
    df['nadarya'] = out
    d = df['nadarya'].rolling(window=2).apply(lambda x: x.iloc[1] - x.iloc[0])
    df['nadarya_buy'] = (d > 0) & (d.shift(1) < 0)
    df['nadarya_sell'] = (d < 0) & (d.shift(1) > 0)

    # returns buy signal, sell signal
    buy_signal = df['nadarya_buy'].iloc[-1]
    sell_signal = df['nadarya_sell'].iloc[-1]
    
    return buy_signal, sell_signal


def is_oversold(rsi: pd.Series, window: int = 14, times: int = 1, target: int = 10) -> bool:
    """
    returns True if the rsi in the given window has gone below 10.
    Times variable is how many times you want the oversold mark to be hit before returning True
    """
    rsi = rsi.tail(window)

    # get a list of the values when the rsi has crossed under 20
    rsi_crossed = [v for ind,v in enumerate(rsi.values) if v <= target and rsi.values[ind-1] >= target and ind > 0]
    
    # return True if the rsi has crossed under 10 more than wanted
    if len(rsi_crossed) >= times:
        return True
    
    return False


def is_overbought(rsi: pd.Series, window: int = 14, times: int = 1, target: int = 90) -> bool:
    """
    returns True if the rsi in the given window has gone above 90. 
    Times variable is how many times you want the overbought mark to be hit before returning True
    """
    rsi = rsi.tail(window)

    # get a list of the values when the rsi has crossed over 80
    rsi_crossed = [v for ind,v in enumerate(rsi.values) if v >= target and rsi.values[ind-1] <= target and ind > 0]

    # return True if the rsi has crossed over 90 more than wanted
    if len(rsi_crossed) >= times:
        return True
    
    return False


def get_position(exchange: Exchange, symbol: str) -> tuple[dict, bool, bool]:
    """
    get the info of your position for the given symbol.
    """
    params = {'type':'swap', 'code':'USDT'}
    balance = exchange.fetch_balance(params=params)
    # print('balance', balance)
    
    # Check if 'positions' key exists and is not empty
    if 'positions' in balance['info']['data']:
        positions = balance['info']['data']['positions']
        matching_positions = [pos for pos in positions if pos['symbol'] == symbol]
        
        if matching_positions:
            position_info = matching_positions[0]
            in_position = position_info['size'] != '0'
            long = position_info['posSide'] == 'Long'
            return position_info, in_position, long
        else:
            print(f"No positions found for symbol: {symbol}")
            return None, False, False
    else:
        print("No positions data available in balance")
        return None, False, False


def close_position(exchange: Exchange, symbol: str) -> None:
    """
    close your position for the given symbol
    """

    # close all pending orders
    exchange.cancel_all_orders(symbol)

    # get your current position information (position is a dict of position information)
    position,in_position,long = get_position(exchange, symbol)
    
    # keep trying to close position every 30 seconds until successfully closed
    while in_position:

        # if position is a long create an equal size short to close. 
        # use reduceOnly to make sure you dont create a trade in the opposite direction
        # sleep for 30 seconds to give order a chance to fill
        if long:
            bid = exchange.fetch_ticker(symbol)['bid'] # get current bid price
            order = exchange.create_limit_sell_order(symbol, position['size'], bid, {'timeInForce': 'PostOnly', 'reduceOnly':True})
            print(f'just made a BUY to CLOSE order of {position["size"]} {symbol} at ${bid}')
            sleep(30)

        # if position is a short create an equal size long to close. 
        # use reduceOnly to make sure you dont create a trade in the opposite direction
        # sleep for 30 seconds to give order a chance to fill
        else:
            # get current ask price
            ask = exchange.fetch_ticker(symbol)['ask'] 
            
            # create a limit buy order
            order = exchange.create_limit_buy_order(symbol, position['size'], ask, {'timeInForce': 'PostOnly', 'reduceOnly':True})
            print(f'just made a SELL to CLOSE order of {position["size"]} {symbol} at ${ask}')
            sleep(30)

        # get your current position information (position is a dict of position information)
        position,in_position,long = get_position(exchange, symbol)


    # cancel all outstanding orders
    exchange.cancel_all_orders(symbol)

    # sleep for a minute to avoid running twice
    sleep(60)

def has_hit_target(price: float, tp: float, sl: float, long: bool) -> bool:
    '''
    returns True if a stop loss or a take profit price is reached
    '''
    if long:
        if price >= tp:
            print('TAKE PROFIT REACHED, CLOSING POSITION')
            return True
        elif price <= sl:
            print('STOP LOSS REACHED, CLOSING POSITION')
            return True
    else:
        if price <= tp:
            print('TAKE PROFIT REACHED, CLOSING POSITION')
            return True
        elif price >= sl:
            print('STOP LOSS REACHED, CLOSING POSITION')
            return True

    return False


def ask_bid(exchange: Exchange, symbol: str) -> tuple[float, float]:

    """
    returns the ask and bid for the given symbol

    Returns:
        ask: float - the current ask price
        bid: float - the current bid price
    """
    order_book = exchange.fetch_order_book(symbol)

    bid = order_book['bids'][0][0]
    ask = order_book['asks'][0][0]

    print(f'this is the ask for {symbol} {ask}')

    return ask, bid


def open_positions(exchange: Exchange, symbol: str) -> tuple[list, bool, float, bool, int, dict]:

    # what is the position index for that symbol?
    if symbol == 'BTC/USDT':
        index_pos = 4
    elif symbol == 'SOL/USDT':
        index_pos = 2
    elif symbol == 'ETH/USDT':
        index_pos = 3
    elif symbol == 'DOGE/USDT':
        index_pos = 1
    elif symbol == 'SHIB/USDT':
        index_pos = 0
    else:
        index_pos = None # just break it... 

    params = {'type':'swap', 'code':'USD'}
    balance = exchange.fetch_balance(params=params)
    open_positions = balance['info']['data']['positions']
    #print(open_positions)

    open_pos_side = open_positions[index_pos]['side'] # btc [3] [0] = doge, [1] ape
    open_pos_size = open_positions[index_pos]['size']
    #print(open_positions)

    if open_pos_side == ('Buy'):
        open_pos_bool = True 
        long = True 
    elif open_pos_side == ('Sell'):
        open_pos_bool = True
        long = False
    else:
        open_pos_bool = False
        long = None 

    print(f'open_positions... | open_pos_bool {open_pos_bool} | open_pos_size {open_pos_size} | long {long} | index_pos {index_pos}')

    return open_positions, open_pos_bool, open_pos_size, long, index_pos, balance


#NOTE - i marked out 2 orders below and the cancel, need to unmark before live
# kill_switch: pass in (symbol) if no symbol just uses default
def kill_switch(exchange: Exchange, symbol: str) -> None:

    print(f'starting the kill switch for {symbol}')
    open_position = open_positions(exchange, symbol)[1] # true or false
    long = open_positions(exchange, symbol)[3]# t or false
    kill_size = open_positions(exchange, symbol)[2] # size thats open  

    print(f'open_position {open_position}, long {long}, size {kill_size}')

    while open_position == True:

        print('starting kill switch loop til limit fil..')
        temp_df = pd.DataFrame()
        print('just made a temp df')

        exchange.cancel_all_orders(symbol)
        open_position = open_positions(exchange, symbol)[1]
        long = open_positions(exchange, symbol)[3] # true or false
        kill_size = open_positions(exchange, symbol)[2]
        kill_size = int(kill_size)
        
        ask = ask_bid(exchange, symbol)[0]
        bid = ask_bid(exchange, symbol)[1]

        if long == False:
            exchange.create_limit_buy_order(symbol, kill_size, bid, params)
            print(f'just made a BUY to CLOSE order of {kill_size} {symbol} at ${bid}')
            print('sleeping for 30 seconds to see if it fills..')
            time.sleep(30)
        elif long == True:
            exchange.create_limit_sell_order(symbol, kill_size, ask, params)
            print(f'just made a SELL to CLOSE order of {kill_size} {symbol} at ${ask}')
            print('sleeping for 30 seconds to see if it fills..')
            time.sleep(30)
        else:
            print('++++++ SOMETHING I DIDN\'T EXCEPT IN KILL SWITCH FUNCTION')
            
        open_position = open_positions(exchange, symbol)[1]

# pnl_close() [0] pnl_close and [1] in_pos [2]size [3]long TF
# takes in symbol, target, max loss
def pnl_close(exchange: Exchange, symbol: str, target: float, max_loss: float) -> tuple[bool, bool, float, bool]:

    #     target = 35
    # max_loss = -55
    
    print(f'checking to see if its time to exit for {symbol}... ')

    params = {'type':"swap", 'code':'USD'}
    pos_dict = exchange.fetch_positions(params=params)
    #print(pos_dict)

    index_pos = open_positions(exchange, symbol)[4]
    pos_dict = pos_dict[index_pos] # btc [3] [0] = doge, [1] ape
    side = pos_dict['side']
    size = pos_dict['contracts']
    entry_price = float(pos_dict['entryPrice'])
    leverage = float(pos_dict['leverage'])

    current_price = ask_bid(exchange, symbol)[1]

    print(f'side: {side} | entry_price: {entry_price} | lev: {leverage}')
    # short or long

    if side == 'long':
        diff = current_price - entry_price
        long = True
    else: 
        diff = entry_price - current_price
        long = False

    try: 
        percentage = round(((diff/entry_price) * leverage), 10)
    except:
        percentage = 0

    percentage = 100 * percentage
    print(f'for {symbol} this is our PNL percentage: {(percentage)}%')

    pnl_close = False 
    in_pos = False

    if percentage > 0:
        in_pos = True
        print(f'for {symbol} we are in a winning position')
        if percentage > target:
            print(':) :) we are in profit & hit target.. checking volume to see if we should start kill switch')
            pnl_close = True
            vol_under_dec = order_book(exchange, symbol) # return TF
            if vol_under_dec == True:
                print(f'volume is under the decimal threshold we set of {vol_decimal}.. so sleeping 30s')
                time.sleep(30)
            else:
                print(f'starting the kill switch because we hit our target of {target}% and already checked vol...')
                kill_switch(exchange, symbol)
        else:
            print(f'we have not hit our target yet of {target}%')

    elif percentage < 0: # -10, -20, 
        
        in_pos = True
        print(f'we are in a losing position of {percentage}..')
        if percentage <= max_loss: # under -55 , -56
            print(f'we need to exit now down {percentage}... so starting the kill switch.. max loss {max_loss}')
            kill_switch(exchange, symbol)
        else:
            print(f'we are in a losing position of {percentage}.. but we are fine because max loss is {max_loss}')

    else:
        print('we are not in position')

    if in_pos == True:

        #if breaks over .8% over 15m sma, then close pos (STOP LOSS)

        # pull in 15m sma
        #call: df_sma(symbol, timeframe, limit, sma)
        timeframe = '15m'
        df_f = df_sma(exchange, symbol, timeframe, 100, 20)
        
        #print(df_f)
        #df_f['sma20_15'] # last value of this
        last_sma15 = df_f.iloc[-1][f'sma{sma}_{timeframe}']
        last_sma15 = int(last_sma15)
        #print(last_sma15)
        # pull current bid
        curr_bid = ask_bid(exchange, symbol)[1]
        curr_bid = int(curr_bid)
        #print(curr_bid)

        sl_val = last_sma15 * 1.008
        #print(sl_val)

    else:
        print('we are not in position.. ')

    print(f' for {symbol} just finished checking PNL close..')

    return pnl_close, in_pos, size, long