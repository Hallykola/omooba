def close_order(mt5,position):
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
        
        "comment": "python monitor close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK  
    }
    # send a trading request "magic": 234000, #mt5.ORDER_FILLING_RETURN,FOK
    result=mt5.order_send(request)
    print(result)

def open_counter_order(mt5,position,magic=1234,lot_size_mult=3):
    # create a close request
    # position_id=position.ticket  "position": position_id,
    price=mt5.symbol_info_tick(position.symbol).bid
    deviation=20
    if position.price_open > position.price_current: # oti yiwo.  It went down, you thought it will go up, if not why was it reported?
        type_was  = mt5.ORDER_TYPE_BUY
    else:
        type_was  = mt5.ORDER_TYPE_SELL

    if type_was == mt5.ORDER_TYPE_BUY:
        type = mt5.ORDER_TYPE_SELL
    else:
        type = mt5.ORDER_TYPE_BUY
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume*lot_size_mult,
        "type": type,
        "magic": magic,
        "price": price,
        "deviation": deviation,
        
        "comment": "python avenger counter order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK  
    }
    # send a trading request "magic": 234000, #mt5.ORDER_FILLING_RETURN,FOK
    result=mt5.order_send(request)
    print(result)


# def open_diff_order(mt5,position,magic=1234):
#     # create a close request
#     # position_id=position.ticket  "position": position_id,
#     price=mt5.symbol_info_tick(position.symbol).bid
#     deviation=20
#     if position.price_open > position.price_current: # oti yiwo.  It went down, you thought it will go up, if not why was it reported?
#         type_was  = mt5.ORDER_TYPE_BUY
#     else:
#         type_was  = mt5.ORDER_TYPE_SELL

#     if type_was == mt5.ORDER_TYPE_BUY:
#         type = mt5.ORDER_TYPE_SELL
#     else:
#         type = mt5.ORDER_TYPE_BUY
#     request={
#         "action": mt5.TRADE_ACTION_DEAL,
#         "symbol": position.symbol,
#         "volume": position.volume,
#         "type": type,
#         "magic": magic,
#         "price": price,
#         "deviation": deviation,
        
#         "comment": "python script counter",
#         "type_time": mt5.ORDER_TIME_GTC,
#         "type_filling": mt5.ORDER_FILLING_FOK  
#     }
#     # send a trading request "magic": 234000, #mt5.ORDER_FILLING_RETURN,FOK
#     result=mt5.order_send(request)
#     print(result)

def send_mt5_order(mt5Api,pair,tradetype,lot = 0.03,comment="python script open"):
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
        "comment": comment,
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
    else:
        return result.order
def send_mt5_hedge_order(mt5Api,pair,tradetype,ticket,lot = 0.03):
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
        "comment": f"hedging {ticket} python script open",
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
    else:
        return result.order
    
def close_order_partially(mt5,position, volume):
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
        "volume": volume,
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

# def close_part_of_order(mt5,position,volume):
#     # create a close request
#     position_id=position.ticket
#     price=mt5.symbol_info_tick(position.symbol).bid
#     deviation=20
#     if position.type == mt5.ORDER_TYPE_BUY:
#         type = mt5.ORDER_TYPE_SELL
#     else:
#         type = mt5.ORDER_TYPE_BUY
#     request={
#         "action": mt5.TRADE_ACTION_DEAL,
#         "symbol": position.symbol,
#         "volume": volume, #position.volume,
#         "type": type,
#         "position": position_id,
#         "price": price,
#         "deviation": deviation,

#         "comment": f"{volume}- python script close",
#         "type_time": mt5.ORDER_TIME_GTC,
#         "type_filling": mt5.ORDER_FILLING_FOK
#     }
#     # send a trading request "magic": 234000, #mt5.ORDER_FILLING_RETURN,
#     result=mt5.order_send(request)
#     print(result)
def use_fireworks_if_possible(mt5Api,position,fireworks_and_positions,log_message,max=4):
        print('checking if fireworks go dey')
        if position.profit > 0 and fireworks_and_positions.get(position.ticket,0) < max and position.comment.find('fireworks') == -1:  # and position.comment.find('avenger') == -1:
            if position.type ==1:
                    print(' fireworks go dey sell')
                    resa=send_mt5_order(mt5Api,position.symbol,'sell',0.01,f"fireworks {position.ticket} order")
                    resb=send_mt5_order(mt5Api,position.symbol,'sell',0.01,f"fireworks {position.ticket} order")
                    # resc=send_mt5_order(mt5Api,position.symbol,'sell',0.01,f"fireworks {position.ticket} order")
            else:
                    print(' fireworks go dey buy')
                    resa=send_mt5_order(mt5Api,position.symbol,'buy',0.01,f"fireworks {position.ticket} order")
                    resb=send_mt5_order(mt5Api,position.symbol,'buy',0.01,f"fireworks {position.ticket} order")
                    # resc=send_mt5_order(mt5Api,position.symbol,'buy',0.01,f"fireworks {position.ticket} order")

            if fireworks_and_positions.get(position.ticket,0)==0:
                fireworks_and_positions[position.ticket]= 2
            else:
                fireworks_and_positions[position.ticket]= fireworks_and_positions[position.ticket]+2
            print(f'I have thrown 2 fireworks for {position.symbol} to make {fireworks_and_positions[position.ticket]} fireworks')
            log_message(f'I have thrown 3 fireworks for {position.symbol} to make {fireworks_and_positions[position.ticket]} fireworks',"main")
            log_message(f'I have thrown 3 fireworks for {position.symbol} to make {fireworks_and_positions[position.ticket]} fireworks',"error")
            log_message(f'I have thrown 3 fireworks for {position.symbol} to make {fireworks_and_positions[position.ticket]} fireworks',position.symbol)



def hedge_position_if_needed(mt5Api,position,hedger_and_hedged_positions, diff=0.0005):
        
        if position.ticket in hedger_and_hedged_positions.values():
            return 
        else:
            position=mt5Api.positions_get(ticket=position.ticket)[0]
            pip_diff = abs(position.price_open - position.price_current)
            print(f'Pip difference is {pip_diff}')

            if position.profit < 0 and pip_diff > diff :
                if position.type ==1:
                    res=send_mt5_hedge_order(mt5Api,position.symbol,'buy',position.ticket,position.volume)
                else:
                    res=send_mt5_hedge_order(mt5Api,position.symbol,'sell',position.ticket,position.volume)
                hedger_and_hedged_positions[res] = position.ticket
                print(f'I have hedged {position.ticket}')
