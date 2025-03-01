# from mt5linux import MetaTrader5
import MetaTrader5 as mt5
import time
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)
import datetime
import pytz


# mt5 = MetaTrader5(host='35.238.227.85',port=8001)
mt5.initialize()

print(mt5.version())
account_info=mt5.account_info()
if account_info!=None:
    # display trading account data 'as is'
    print(account_info)
# i=0
# while i<50:
#     lasttick=mt5.symbol_info_tick("GBPUSD")
#     print(lasttick._asdict())
#     time.sleep(20)
#     i += 1




mt5TimeFrame = {"M1":"mt5.TIMEFRAME_M1",
"M2":"mt5.TIMEFRAME_M2",
"M3":"mt5.TIMEFRAME_M3",
"M4":"mt5.TIMEFRAME_M4",
"M5":"mt5.TIMEFRAME_M5",
"M6":"mt5.TIMEFRAME_M6",

"M10":"mt5.TIMEFRAME_M10",

"M12":"mt5.TIMEFRAME_M12",

"M15":"mt5.TIMEFRAME_M15",

"M20":"mt5.TIMEFRAME_M20",

"M30":"mt5.TIMEFRAME_M30",
"H1":"mt5.TIMEFRAME_H1",

"H2":"mt5.TIMEFRAME_H2",
"H3":"mt5.TIMEFRAME_H3",
"H4":"mt5.TIMEFRAME_H4",
"H6":"mt5.TIMEFRAME_H6",

"H8":"mt5.TIMEFRAME_H8",

"H12":"mt5.TIMEFRAME_H12",

"D1":"mt5.TIMEFRAME_D1",

"W1":"mt5.TIMEFRAME_W1",

"MN1":"mt5.TIMEFRAME_MN1"
}
def getCandlesDf(pair,granularity,count):
        rates = mt5.copy_rates_from_pos(pair, mt5TimeFrame[granularity], 0, count)
        # create DataFrame out of the obtained data
        rates_frame = pd.DataFrame(rates)
        # convert time in seconds into the datetime format
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame['mid_h']=rates_frame['high']
        rates_frame['mid_l']=rates_frame['low']
        rates_frame['mid_c']=rates_frame['close']
        rates_frame['mid_o']=rates_frame['open']
        rates_frame['ask_h']=rates_frame['high']+ rates_frame['spread']*0.0001
        rates_frame['ask_l']=rates_frame['low']+ rates_frame['spread']*0.0001
        rates_frame['ask_c']=rates_frame['close']+ rates_frame['spread']*0.0001
        rates_frame['ask_o']=rates_frame['open']+ rates_frame['spread']*0.0001
        rates_frame['bid_h']=rates_frame['high']- rates_frame['spread']*0.0001
        rates_frame['bid_l']=rates_frame['low']- rates_frame['spread']*0.0001
        rates_frame['bid_c']=rates_frame['close']- rates_frame['spread']*0.0001
        rates_frame['bid_o']=rates_frame['open']- rates_frame['spread']*0.0001
        #wok on handling jpy spreads
        return rates_frame

# def getHistoricalCandles(granularity,pair):
#      # set time zone to UTC
#     timezone = pytz.timezone("Etc/UTC")
#     # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
#     utc_from = datetime.datetime(2020, 1, 10)
#     utc_to = datetime.datetime(2020, 12, 11)
#     # get bars from USDJPY M5 within the interval of 2020.01.10 00:00 - 2020.01.11 13:00 in UTC time zone
#     rates = mt5.copy_rates_range(pair, mt5TimeFrame[granularity], utc_from, utc_to)

#     rates_frame = pd.DataFrame(rates)
#     # convert time in seconds into the 'datetime' format
#     rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
#     rates_frame.to_json(f'/mt5data/{pair}-{granularity}.json')

# data = getCandlesDf("EURUSD","M1",10)
# getHistoricalCandles("M1","EURUSD")

# orders=mt5.orders_total()
# if orders>0:
#     print("Total orders=",orders)
# else:
#     print("Orders not found")

def close_order(position):
    # create a close request
    position_id=position.ticket
    price=mt5.symbol_info_tick(position.symbol).bid
    deviation=20
    if position.type == mt5.ORDER_TYPE_BUY:
        type = mt5.ORDER_TYPE_SELL
    else:
        type = mt5.ORDER_TYPE_BUY
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": type,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK  
    }
    # send a trading request "magic": 234000, #mt5.ORDER_FILLING_RETURN,
    result=mt5.order_send(request)
    print(result)


def close_bad_positions(symbol):
    positions=mt5.positions_get(symbol=symbol)

    # print(positions)
    if positions==None:
        print("No positions on EURUSD, error code={}".format(mt5.last_error()))
    elif len(positions)>0:
        print("Total positions on EURUSD =",len(positions))
        # display all open positions get highest profit position
        highest_profit_ticket_id = None
        highest_profit = -100
        for position in positions:
            print(f'ticket id:{position.ticket}')
            print(f'profit:{position.profit}')
            if position.profit > highest_profit:
                highest_profit = position.profit
                highest_profit_ticket_id = position.ticket
        #close all lower profit/losing position
        for position in positions:
            if position.ticket != highest_profit_ticket_id:
                print(f" current ticket:{position.ticket}, highest :{highest_profit_ticket_id}")
                close_order(position)
                # mt5.Close(position.symbol,ticket=position.ticket)
                print(f'ticket with id:{position.ticket} closed at {position.profit}')

def monitor_profit(symbol,max_loss):
    # Handle negative values ok..... TODO
    firstposition=mt5.positions_get(symbol=symbol)[0]
    max_profit = firstposition.profit
    count = 0
    loss=0
    percent_loss = 0
    while True:
        count = count + 1
        time.sleep(2)
        position=mt5.positions_get(symbol=symbol)[0]
        print(position)
        #handle negative profit to wait while nnot less than bearable threashold
        if position.profit < 0: 
            if position.profit  > max_loss:
                continue
            else:
                break

        if position.profit > max_profit:
            max_profit = position.profit
            loss = 0
        else:
            loss = max_profit - position.profit
            percent_loss = ((abs(loss)/max_profit)*100)
            if percent_loss > 15:
                break
        if count % 2 == 0:
            print(f"current profit: {position.profit}, max profit: {max_profit}...loss{loss} ... percentage loss {percent_loss}")
    close_order(position)

# close_bad_positions("EURUSD")
def check_for_any_profitable_position(symbol):
    positions=mt5.positions_get(symbol=symbol)
    profitable_seen = False
    while not profitable_seen:
        positions=mt5.positions_get(symbol=symbol)
        for position in positions:
                if position.profit >= 0:
                    profitable_seen = True
                    print(f'ticket id:{position.ticket} is profitable')
                    break
        print(f'No ticket is profitable yet')
        time.sleep(3)
    return True
        
def send_mt5_order(mt5Api,pair,tradetype):
    # prepare the buy request structure
    print("i'm in send order")
    symbol = pair
    if tradetype == 'sell':
        type = mt5Api.ORDER_TYPE_SELL
    else:
        type = mt5Api.ORDER_TYPE_BUY
    symbol_info = mt5Api.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
    
    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5Api.symbol_select(symbol,True):
            print("symbol_select({}}) failed",symbol)
    
    lot = 0.1
    point = mt5Api.symbol_info(pair).point
    price = mt5Api.symbol_info_tick(pair).ask
    deviation = 20
    request = {
        "action": mt5Api.TRADE_ACTION_DEAL,
        "symbol": pair,
        "volume": lot,
        "type": type,
        "price": price,
        "deviation": deviation,
        "comment": "python script open",
        "type_time": mt5Api.ORDER_TIME_GTC,
        "type_filling":mt5Api.ORDER_FILLING_FOK
    }
    # "type_filling": mt5Api.ORDER_FILLING_RETURN, "sl": price - 100 * point "tp": price + 100 * point,"magic": 234000,
    # send a trading request
    result = mt5Api.order_send(request)
    # check the execution result
    print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation))
    if result.retcode != mt5Api.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field,result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


def open_twin_trades_kill_and_chase_profit(symbol):
    timeframe = 60
    send_mt5_order(mt5,symbol,'buy')
    send_mt5_order(mt5,symbol,'sell')
    oneprofitable = check_for_any_profitable_position(symbol)
    if oneprofitable:
        # time.sleep(timeframe*3)
        close_bad_positions(symbol)
        monitor_profit(symbol, 1)
    
# open_twin_trades_kill_and_chase_profit("USDJPY")

send_mt5_order(mt5,"EURUSD",'sell')
monitor_profit("EURUSD", -2.5)
# monitor_profit("EURUSD")
