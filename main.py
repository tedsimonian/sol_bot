import schedule 
import time

from trader.utilities import *
from trader.connector import get_kucoin_connection

# connect to the kucoin exchange
kucoin = get_kucoin_connection()

# config settings for bot
rsi_targets = [10,90] # set the oversold / overbought level in the stoch rsi
rsi_window = 14 # the n most recent amount of candles to check if stoch rsi suggest oversold / overbought
timeframe = '1h' # use m for minutes and h for hours, EX. 1m (1 minute) or 4h (4 hour)
symbol = 'BTC/USDT'
size = 1000
params = {'timeInForce': 'PostOnly'}

def bot():
        # get your current position in the market
        position_info, in_position, long = get_position(kucoin, symbol)
        
        candles = get_candle_df(kucoin, symbol, timeframe) # get the last 55 candle data for the timeframe
        
        # add the nadarya indicator to the candles dataframe, along with its buy and sell signal columns
        nadarya_buy_signal, nadarya_sell_signal = calc_nadarya(candles)
        
        # add the stoch_rsi indicator as a column to the candles dataframe
        calc_stoch_rsi(candles)
        
        # get the current bid
        bid = kucoin.fetch_ticker(symbol)['bid'] 

        if not in_position:
            # place a long order if the nadarya indicator has said to buy OR if the stoch rsi indicator suggests it is oversold
            if nadarya_buy_signal or is_oversold(candles['stoch_rsi'], rsi_window, 1, rsi_targets[0]):
                order = kucoin.create_limit_buy_order(symbol, size, price=bid, params=params)

            # place a short order if the nadarya indicator has said to sell OR if the stoch rsi indicator suggests it is overbought
            elif nadarya_sell_signal or is_overbought(candles['stoch_rsi'], rsi_window, 1, rsi_targets[1]):
                order = kucoin.create_limit_sell_order(symbol, size, price=bid, params=params)
        elif in_position:
            # close the position if you are in a long and the nadarya indicator suggests a sell OR the stoch rsi has shown overbought twice already
            if long:
                if nadarya_sell_signal or is_overbought(candles['stoch_rsi'], rsi_window, times=2, target=rsi_targets[1]):
                    close_position(kucoin, symbol)

            # close the position if you are in a short and the nadarya indicator suggests a buy OR the stoch rsi has shown oversold twice already
            else:
                if nadarya_buy_signal or is_oversold(candles['stoch_rsi'], rsi_window, times=2, target=rsi_targets[0]):
                    close_position(kucoin, symbol)

# run the bot every 20 seconds
schedule.every(20).seconds.do(bot)

while True:
    try:
        schedule.run_pending()
    except:
        print('+++++ ERROR RUNNING BOT, SLEEPING FOR 30 SECONDS BEFORE RETRY')
        time.sleep(30)
