import schedule 
import pandas as pd
from time import sleep
from ta.momentum import *

from trader.utilities import *
from trader.connector import get_phemex_connection

# connect to the phemex exchange
phemex = get_phemex_connection()
# phemex.verbose = True

# config settings for bot
symbol = 'BTCUSDT'
pos_size = 10 # 125, 75, 
target = 8
max_loss = -9
vol_decimal = .4
params = {'timeInForce': 'PostOnly'}

def bot():
    get_pnl_close(phemex, symbol, target, max_loss) # checking if we hit our pnl
    sleep_on_close(phemex, symbol) # checking sleep on close

    df_d = daily_sma(phemex, symbol) # determines LONG/SHORT
    df_f = f15_sma(phemex, symbol) # provides prices bp_1, bp_2, sp_1, sp_2
    ask, bid = ask_bid(phemex, symbol)

    # MAKE OPEN ORDER
    # LONG OR SHORT?
    signal = df_d.iloc[-1]['sig']
    #print(sig)

    open_size = pos_size / 2

    # ONLY RUN IF NOT IN POSITION
    pnl_close, in_pos, size, long = get_pnl_close(phemex, symbol, target, max_loss)
    print(in_pos)
    open_positions, open_pos_bool, open_pos_size, long, index_pos, balance = get_open_positions(phemex, symbol)
    curr_size = int(open_pos_size)
    print(curr_size)

    curr_p = bid 
    last_sma15 = df_f.iloc[-1]['sma20_15']
    # pos_size = 50 , if inpos == False

    # never get in a position bigger than pos_size (52)

    if (in_pos == False) and (curr_size < pos_size):

        phemex.cancel_all_orders(symbol)

        # fix order function so i stop sending orders in if price > sma 

        if (signal == 'BUY') and (curr_p > last_sma15):

            # buy sma daily is < price == BUY
            print('making an opening order as a BUY')
            bp_1 = df_f.iloc[-1]['bp_1']
            bp_2 = df_f.iloc[-1]['bp_2']
            print(f'this is bp_1: {bp_1} this is bp_2: {bp_2}')
            phemex.cancel_all_orders(symbol)
            phemex.create_limit_buy_order(symbol, open_size, bp_1, params)
            phemex.create_limit_buy_order(symbol, open_size, bp_2, params)

            print('just made opening order so going to sleep for 2mins..')
            sleep(120)
        elif (signal == 'SELL') and (curr_p < last_sma15):
            print('making an opening order as a SELL')
            sp_1 = df_f.iloc[-1]['sp_1']
            sp_2 = df_f.iloc[-1]['sp_2']
            print(f'this is sp_1: {sp_1} this is sp_2: {sp_2}')
            phemex.cancel_all_orders(symbol)
            phemex.create_limit_sell_order(symbol, open_size, sp_1, params)
            phemex.create_limit_sell_order(symbol, open_size, sp_2, params)

            print('just made opening order so going to sleep for 2mins..')
            sleep(120)
        else:
            print('not submitting orders.. price prob higher or lower than sma.. 10m sleep...')
            sleep(600)
    else:
        print('we are in position already so not making new orders..')


# run the bot every 28 seconds
schedule.every(28).seconds.do(bot)

while True:
    try:
        schedule.run_pending()
    except:
        print('+++++ ERROR RUNNING BOT, SLEEPING FOR 30 SECONDS BEFORE RETRY')
        sleep(30)

# bot()