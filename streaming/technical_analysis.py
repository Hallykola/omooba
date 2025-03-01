import pandas as pd
import sys
import math

import pickle
import neat
import numpy as np


from constants import defs
from scalperhelper import close_order
from streaming.trade_manager import close_pair_trade, get_open_trades, send_neutral_mt5_order, send_neutral_mt5_order_with_exit
from technicals.indicators import BollingerBands, ATR
from technicals.patternfinder import PatternFinder
sys.path.append("../")
from models.tradesettings import TradeSettings
pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

def apply_SL(row,trade_settings: TradeSettings ):
    if row.SIGNAL == defs.BUY:
        return row.mid_c - row.GAIN   #*0.1)   #/trade_settings.riskreward)
    if row.SIGNAL == defs.SELL:
        return row.mid_c + row.GAIN   #*0.1) #/trade_settings.riskreward)
    return 0.0

def apply_mysignal(row, tradeSettings:TradeSettings):
    if row.SPREAD <= tradeSettings.maxspread:
        if row.MA_50_CROSS_200 == 1 and row.PREV_MA_50_CROSS_200 != 1:   # == 1 and row.mid_c < row.BB_UP:
            return defs.BUY
        elif row.MA_50_CROSS_200 == -1 and row.PREV_MA_50_CROSS_200 != -1:   #row.mid_c < row.BB_LW and row.mid_o > row.BB_LW:
            return defs.SELL
    return defs.NONE

def apply_TP(row):
    if row.SIGNAL == defs.BUY:
        return row.mid_c + row.GAIN
    if row.SIGNAL == defs.SELL:
        return row.mid_c - row.GAIN
    return 0.0

# def apply_signal(row, tradeSettings:TradeSettings):
#     if row.SPREAD <= tradeSettings.maxspread:    #and row.GAIN >= tradeSettings.mingain:
#         if row.MA_50_CROSS_200 == 1: #and row.PREV_MA_50_CROSS_200 != 1:   # == 1 and row.mid_c < row.BB_UP:
#             return defs.BUY
#         elif row.MA_50_CROSS_200 == -1: # and row.PREV_MA_50_CROSS_200 != -1:   #row.mid_c < row.BB_LW and row.mid_o > row.BB_LW:
#             return defs.SELL
#     return defs.NONE

def apply_MA_CROSS(row):
    if row.MA_50 > row.MA_200:   #and row.PREV_MA_50 < row.PREV_MA_200:
        return 1
    elif row.MA_200 > row.MA_50:  # and row.PREV_MA_200 < row.PREV_MA_50:
        return -1
    else:
        return 0

def apply_BB_MA_CROSS(row):
    if (row.mid_c > row.BB_MA and row.mid_o < row.BB_MA) or (row.mid_c < row.BB_MA and row.mid_o > row.BB_MA):
        #one candle cross
        return 1
    else:
        return 0
    
# def apply_signal(row, tradeSettings:TradeSettings):
#     if row.SPREAD <= tradeSettings.maxspread and row.GAIN >= tradeSettings.mingain:
#         if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
#             return defs.SELL
#         elif row.mid_c < row.BB_LW and row.mid_o > row.BB_LW:
#             return defs.BUY
#     return defs.SELL  #defs.NONE

    # if row.GAIN >= tradeSettings.mingain and row.spread <= tradeSettings.maxspread:
    #     if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
    #         return defs.SELL
    #     if row.mid_o > row.BB_LW and row.mid_c < row.BB_LW:
    #         return defs.BUY
    # return defs.NONE
 

def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings,techs, log_message):
    df_an = df.copy()
    df_an.reset_index(drop=True, inplace=True)
    df_an["PAIR"] = pair
    df_an["MA_50"] = df_an.mid_c.rolling(window = 20).mean()        
    df_an["MA_200"] = df_an.mid_c.rolling(window = 55).mean()
    df_an["PREV_MA_50"] = df_an["MA_50"].shift(1)       
    df_an["PREV_MA_200"] = df_an["MA_200"].shift(1)
    df_an["MA_50_CROSS_200"]= df_an.apply(apply_MA_CROSS,axis=1)
    df_an["PREV_MA_50_CROSS_200"]= df_an["MA_50_CROSS_200"].shift(1)
    df_an.dropna(inplace=True)
    # changed spread to small letters cos of mt5 format
    df_an["SPREAD"] = df_an["spread"]*trade_settings.pip #df_an.ask_c -df_an.bid_c
    # print( df_an["SPREAD"])
    df_an = BollingerBands(df_an,trade_settings.n_ma,trade_settings.n_std)

    df_an["PRICE_CROSS_BB_MA"]= df_an.apply(apply_BB_MA_CROSS,axis=1)

    df_an = ATR(df_an,14)
    df_an["GAIN"] =  20*trade_settings.pip  #abs(df_an.mid_c - df_an.BB_MA)*0.6   #*0.56 #df_an.mid_c - df_an.BB_MA
    df_an['SIGNAL'] = df_an.apply(apply_mysignal, axis=1,  args=(trade_settings,))
    df_an["SL"] = df_an.apply(apply_SL, axis=1, args=(trade_settings,))
    df_an["TP"] = df_an.apply(apply_TP,axis=1)
    df_an["LOSS"] = abs(df_an.mid_c - df_an.SL)

    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o','ATR_14','BB_UP' ,'BB_MA','BB_LW','SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']

    # log_cols = ['PAIR', 'time', 'mid_c', 'mid_o', 'SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']
    lastrow = df_an.iloc[-1]
    # print(f"Current spread: {lastrow.SPREAD} with settings spread: {trade_settings.maxspread} and current est. gain is: {lastrow.GAIN} with settings mingain as: {trade_settings.mingain}")
    print(f"Current spread: {lastrow.SPREAD} with settings spread: {trade_settings.maxspread}")
    log_message(f"process_candles:\n{df_an[log_cols].tail()}", pair)
    # log_message(f"{pair} --> Current spread: {lastrow.SPREAD} with settings spread: {trade_settings.maxspread} and current est. gain is: {lastrow.GAIN} with settings mingain as: {trade_settings.mingain}","main")
    techs["ATR"] = df_an[log_cols].iloc[-1].ATR_14
    # print(f'Technical analysis: ATR for {pair} is currently {df_an[log_cols].iloc[-1].ATR_14}and tech for pair is {techs}')
    return df_an[log_cols].iloc[-1]






def apply_plain_signal(row, tradeSettings:TradeSettings):
    if row.SPREAD <= tradeSettings.maxspread:
        if row.MA_50_CROSS_200 == 1:
            return defs.BUY
        elif row.MA_50_CROSS_200 == -1:   
            return defs.SELL
    return defs.NONE

def process_candles_get_crossover(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):
    df_an = df.copy()
    df_an.reset_index(drop=True, inplace=True)
    df_an["PAIR"] = pair
    
    df_an["MA_50"] = df_an.mid_c.rolling(window = 20).mean()        
    df_an["MA_200"] = df_an.mid_c.rolling(window = 55).mean()
    df_an["MA_50_CROSS_200"]= df_an.apply(apply_MA_CROSS,axis=1)
    df_an["SPREAD"] = df_an["spread"]*trade_settings.pip
    df_an.dropna(inplace=True)

    df_an = ATR(df_an)

    df_an["GAIN"] = df["ATR_14"]*3   #20*trade_settings.pip  #abs(df_an.mid_c - df_an.BB_MA)*0.6   #*0.56 #df_an.mid_c - df_an.BB_MA
    df_an['SIGNAL'] = df_an.apply(apply_plain_signal, axis=1,  args=(trade_settings,))
    df_an["SL"] = df_an.mid_c - df["ATR_14"]*1.5
    df_an["TP"] =  df_an.mid_c + df["ATR_14"]*3
    df_an["LOSS"] = df["ATR_14"]*1.5  
    
    log_cols = ['time', 'mid_c', 'MA_50','MA_200' , 'MA_50_CROSS_200']
    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o','SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']


    return df_an[log_cols].iloc[-1]


def check_if_open_trades(mt5Api,pair):
    open_trades = mt5Api.positions_get(symbol=pair)
    if len(open_trades)> 0:
        return 1
    else:
        return 0


    return open_trades
def process_candles_for_neat(df: pd.DataFrame, pair, trade_settings: TradeSettings,techs,mt5Api, log_message):
    df_an = df.copy()
    df_an.reset_index(drop=True, inplace=True)
    df_an["PAIR"] = pair

    #add 10 close values trend angle
    angles = [0,0,0,0,0,0,0,0,0,0]

    for (i,row) in df_an.iterrows():
        if i < 10:
            continue
        tan = (row['mid_c'] - df_an.iloc[i-10]['mid_c'])/10
        arctan = math.atan(tan)
        angles.append(arctan)
    
    df_an['trendAngle'] = angles
    df_an['diff'] = df_an.mid_c.diff() 
    
    trading = check_if_open_trades(mt5Api,pair)
    
    trade = trading
    trendAngle = df_an['trendAngle'].iloc[-1]
    diff = df_an['diff'].iloc[-1]
    volume = df_an['volume'].iloc[-1]
    print(f"TrendAngle: {trendAngle}, Price Difference: {diff}, Volume: {volume} Trading: {trade}")
    try:
        with open("./streaming/neat/winner.pkl", "rb") as f:
            genome = pickle.load(f)
    except Exception as error:
        print(f'na thee error be this {error}')

    print('hello boy')

    config_file = "./streaming/neat/config.txt"
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)

    net = neat.nn.FeedForwardNetwork.create(genome, config)
    print('hello boy 2')

    action = net.activate(np.array([trendAngle, diff,volume,trade]))
    action = int(np.argmax(action))
    print("Action:",action)
    if action == 1:
        send_neutral_mt5_order(mt5Api,pair,'buy')
        log_message(f"buying {pair}", pair)
        print(f"buying {pair}")
    else:
        close_pair_trade(mt5Api,pair)
        log_message(f"not trading {pair}", pair)
        print(f"not trading {pair}")

def process_candles_for_harmonics(df: pd.DataFrame, pair, trade_settings: TradeSettings,techs,mt5Api, log_message):
    df_an = df.copy()
   
    df_an.reset_index(drop=True, inplace=True)
    df_an = df_an.set_index('time')
    df_an["PAIR"] = pair
    
    pf = PatternFinder()
    
    tag = "Not needed"
    
    found_recent,entry,exit,sl = pf.show_recent_patterns(df,tag)
    
    change = exit-entry
    if found_recent:
        open_trade = get_open_trades(mt5Api,pair)
        if open_trade != None and open_trade != ():
            opentrade = mt5Api.positions_get(symbol=pair)[0]
            print(opentrade)
            if (opentrade.type == mt5Api.ORDER_TYPE_SELL and change > 0) or (opentrade.type == mt5Api.ORDER_TYPE_BUY and change < 0):
                close_order(opentrade)
            
        if change > 0:
            
            send_neutral_mt5_order_with_exit(mt5Api,pair,'buy',exit,sl)
            log_message(f"buying {pair}", pair)
            print(f"buying {pair}")
        else:
            
            send_neutral_mt5_order_with_exit(mt5Api,pair,'sell',exit,sl)
            log_message(f"selling {pair}", pair)
            print(f"selling {pair}")
   