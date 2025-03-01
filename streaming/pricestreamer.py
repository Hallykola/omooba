import json
import threading

import pandas as pd
import requests

from constants import defs
from models.mt5liveapiprice import Mt5LiveApiPrice 
from timeit import default_timer as timer

from mt5linux import MetaTrader5 
# import MetaTraderpython –m venv env5 


import time

# STREAM_URL = f"https://stream-fxpractice.oanda.com/v3"

class PriceStreamer(threading.Thread):

    LOG_FREQ = 60

    def __init__(self,mt5Api,prices,price_event,price_lock:threading.Lock,log_message):
        super().__init__()
        self.shared_prices = prices
        self.price_event = price_event
        self.price_lock  = price_lock
        self.log_message  = log_message
        self.pairs_list = prices.keys()
        self.mt5Api = mt5Api
        

    def fire_new_price_event(self,instrument):
        if (self.price_event[instrument].is_set() == False):
            self.price_event[instrument].set()
    def update_new_price(self,live_price:Mt5LiveApiPrice):
        try:
            self.price_lock.acquire()
            self.shared_prices[live_price.instrument] = live_price
            self.fire_new_price_event(live_price.instrument)
        except Exception as error:
            self.log_message(f" Exception in update_new_price: {error}", error)
        finally:
            self.price_lock.release()

    def run(self):
        start = timer()-PriceStreamer.LOG_FREQ+10
        # params = dict(
        #     instruments = ",".join(self.pairs_list)
        # )
        # url = f"{STREAM_URL}/accounts/{defs.ACCOUNT_ID}/pricing/stream"

        # resp = requests.get(url, params=params, headers=defs.SECURE_HEADER, stream=True)
        while True:
            
            for i in self.pairs_list:
                time.sleep(2)
                try:
                    # lasttickprice=self.mt5Api.symbol_info_tick(i)
                    # if lasttickprice is not None:
                    #     print("currency:",i,lasttickprice._asdict())
                    #     # lasttickprice = lasttickprice._asdict()
                    #     new_price = Mt5LiveApiPrice(i,lasttickprice._asdict())
                    #     print(new_price)
                        # self.update_new_price(new_price)
                    # time.sleep(2)
                # try:
                    lasttickprice=self.mt5Api.symbol_info_tick(i)
                    if lasttickprice is not None:
                        lasttickprice = lasttickprice._asdict()
                        new_price = Mt5LiveApiPrice(i,lasttickprice)
                        
                        self.update_new_price(new_price)
                        
                    # time.sleep(2)
                except Exception as error:
                    print(f"Error with currency {i} : {error}")
            if (timer()- start) > PriceStreamer.LOG_FREQ:
                try:
                    self.log_message(f"\n{pd.DataFrame.from_dict([v.get_dict() for _, v in self.shared_prices.items()])}",'main')
                except Exception as error:
                    print(self.shared_prices)
                    print(f"Error with currency while logging {i} : {error}")
            time.sleep(15)

        # for price in resp.iter_lines():
        #     decoded_price = json.loads(price.decode("utf-8"))
        #     if 'type' in decoded_price  and decoded_price["type"] == "PRICE":
        #         new_price = LiveApiPrice(decoded_price)
        #         # print(self.shared_prices.items())
        #         self.update_new_price(new_price)
        #         if (timer()- start) > PriceStreamer.LOG_FREQ:
        #             self.log_message(f"\n{pd.DataFrame.from_dict([v.get_dict() for _, v in self.shared_prices.items()])}",'main')
