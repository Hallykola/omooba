

from models.trade_decision import TradeDecision
from scalperhelper import close_order
from streaming.trade_risk_calculator import get_trade_units
from constants import defs


# def get_open_trades(api,pair):
#     open_trades = api.get_open_trades()
#     for ot in open_trades:
#        if ot.instrument == pair:   #if ot['instrument'] == pair:
#          return ot
#     return None
def get_open_trades(mt5Api,pair):
    open_trades = mt5Api.positions_get(symbol=pair)
    print("open trades",open_trades)

    return open_trades

def send_mt5_order(mt5Api,trade_decision,log_message):
    # prepare the buy request structure
    print("i'm in send order")
    symbol = trade_decision.pair
    symbol_info = mt5Api.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        log_message("Could not place trade", "error")
    
    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5Api.symbol_select(symbol,True):
            print("symbol_select({}}) failed",symbol)
            log_message(f"Could not place trade: symbol_select({symbol}) failed", "error")
    
    lot = defs.my_lot_size
    point = mt5Api.symbol_info(trade_decision.pair).point
    price = mt5Api.symbol_info_tick(trade_decision.pair).ask
    if trade_decision.signal == defs.SELL:
        type = mt5Api.ORDER_TYPE_SELL
    else:
        type = mt5Api.ORDER_TYPE_BUY
    deviation = 20
    request = {
        "action": mt5Api.TRADE_ACTION_DEAL,
        "symbol": trade_decision.pair,
        "volume": lot,
        "type": type,
        "price": price,
        # "sl":  trade_decision.sl,   #price + 100 * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python * normal open",
        "type_time": mt5Api.ORDER_TIME_GTC,
        
        "type_filling":mt5Api.ORDER_FILLING_FOK
    }
    # "tp": price - 100 * point,
    

    # "type_filling": mt5Api.ORDER_FILLING_RETURN, FOK
    # send a trading request
    result = mt5Api.order_send(request)
    # check the execution result
    print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation))
    log_message("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation), trade_decision.pair)
    if result.retcode != mt5Api.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        print(result)
        log_message(f"Could not place trade: order_send failed,retcode={result.retcode}", "error")
        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field,result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


def place_trade(mt5Api,trade_decision:TradeDecision,trade_risk,log_message):
    open_trade =  get_open_trades(mt5Api,trade_decision.pair)
    print("Im trying to place trade")

    

    if open_trade != None and open_trade != ():
        opentrade = mt5Api.positions_get(symbol=trade_decision.pair)[0]
        # close_order(mt5Api,opentrade)

        # log_message(f"Failed to place trade {trade_decision}, already open: {open_trade}", trade_decision.pair)
        # print(f"Failed to place trade {trade_decision}, already open: {open_trade}")
        # return None
    
    
    # trade_units = get_trade_units(mt5Api, trade_decision.pair, trade_decision.signal, 
    #                         trade_decision.loss, trade_risk, log_message)

    send_mt5_order(mt5Api,trade_decision,log_message)


    # ok,response = mt5Api.place_trade(
    #     trade_decision.pair, 
    #     trade_units,
    #     trade_decision.signal,
    #     trade_decision.sl,
    #     trade_decision.tp
    # )
    
    # if not ok:
    #     log_message(f"ERROR placing {trade_decision}..error:{response}",'error')
    #     log_message(f"ERROR placing {trade_decision}...error:{response}", trade_decision.pair)
    
    # else:
    #     trade_id = response
    #     log_message(f"placed trade_id:{trade_id} for {trade_decision}", trade_decision.pair)
    #     print(f"placed trade_id:{trade_id} for {trade_decision}")

def close_pair_trade(mt5Api,pair):
    try:
        opentrade = mt5Api.positions_get(symbol=pair)[0]
        close_order(mt5Api,opentrade)
    except Exception as error:
        print(f"Error occurred: {error} ")

def send_neutral_mt5_order_with_exit(mt5Api,pair,tradetype,exit,sl):
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
        "tp": exit,
        "sl": sl,
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

def send_neutral_mt5_order(mt5Api,pair,tradetype):
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

