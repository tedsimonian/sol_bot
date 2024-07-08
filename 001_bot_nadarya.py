import schedule 
from time import sleep

from trader.utilities import *
from trader.connector import get_phemex_connection

# connect to the phemex exchange
phemex = get_phemex_connection()
# phemex.verbose = True

# config settings for bot
rsi_targets = [10, 90] # set the oversold / overbought level in the stoch rsi
rsi_window = 14 # the n most recent amount of candles to check if stoch rsi suggest oversold / overbought
timeframe = '1h' # use m for minutes and h for hours, EX. 1m (1 minute) or 4h (4 hour)
symbol = 'BTCUSDT'
size = 10

def bot():
        # get your current position in the market
        position_info, in_position, long = get_position(phemex, symbol)
        
        # print(f"Position Info: {position_info}")
        
        candles = get_candle_df(phemex, symbol, timeframe) # get the last 55 candle data for the timeframe
        
        # add the nadarya indicator to the candles dataframe, along with its buy and sell signal columns
        nadarya_buy_signal, nadarya_sell_signal = calc_nadarya(candles) 
        
        # add the stoch_rsi indicator as a column to the candles dataframe
        calc_stoch_rsi(candles)
        
        # get the current bid
        bid = phemex.fetch_ticker(symbol)['bid']
        
        if not in_position:
            # place a long order if the nadarya indicator has said to buy OR if the stoch rsi indicator suggests it is oversold
            if nadarya_buy_signal or is_oversold(candles['stoch_rsi'], rsi_window, 1, rsi_targets[0]):
                params = {'timeInForce': 'PostOnly', 'posSide': 'Long'}
                order = phemex.create_limit_buy_order(symbol, size, price=bid, params=params)
                print(f"Placed a limit buy order: {order}")

            # place a short order if the nadarya indicator has said to sell OR if the stoch rsi indicator suggests it is overbought
            elif nadarya_sell_signal or is_overbought(candles['stoch_rsi'], rsi_window, 1, rsi_targets[1]):
                params = {'timeInForce': 'PostOnly', 'posSide': 'Short'}
                order = phemex.create_limit_sell_order(symbol, size, price=bid, params=params)
                print(f"Placed a limit sell order: {order}")
            
            else:
                print(f"No buy or sell signal for {symbol}")
        elif in_position:
            # close the position if you are in a long and the nadarya indicator suggests a sell OR the stoch rsi has shown overbought twice already
            if long:
                if nadarya_sell_signal or is_overbought(candles['stoch_rsi'], rsi_window, times=2, target=rsi_targets[1]):
                    close_position(phemex, symbol)
                    print(f"Closed long position for {symbol}")
                else:
                    print(f"No sell signal for {symbol}")
            # close the position if you are in a short and the nadarya indicator suggests a buy OR the stoch rsi has shown oversold twice already
            else:
                if nadarya_buy_signal or is_oversold(candles['stoch_rsi'], rsi_window, times=2, target=rsi_targets[0]):
                    close_position(phemex, symbol)
                    print(f"Closed short position for {symbol}")
                else:
                    print(f"No buy signal for {symbol}")

# run the bot every 20 seconds
schedule.every(20).seconds.do(bot)

while True:
    try:
        schedule.run_pending()
    except:
        print('+++++ ERROR RUNNING BOT, SLEEPING FOR 30 SECONDS BEFORE RETRY')
        sleep(30)
