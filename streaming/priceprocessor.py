import threading
import copy
from queue import Queue
import pytz
import datetime as dt

from models.mt5liveapiprice import Mt5LiveApiPrice


GRANULARITIES = {
    "M1": 1,
    "M5": 5,
    "M15": 15,
    "M30": 30,
    "H1": 60,
}

class PriceProcessor(threading.Thread):

    def __init__(self,prices,price_event,price_lock:threading.Lock,pair,candle_queue: Queue, granularity,log_message):
        super().__init__()
        self.shared_prices = prices
        self.price_events = price_event
        self.price_lock  = price_lock
        self.log_message  = log_message
        self.pair = pair
        self.candle_queue = candle_queue
        self.granularity = GRANULARITIES[granularity]
        now = dt.datetime.now(pytz.timezone('UTC'))
        self.set_last_complete_candle_time(now)
        print(f" PriceProcessor : {self.last_complete_candle_time} {now}")

    def set_last_complete_candle_time(self, time:dt.datetime):
        print('Fixing timey',time)
        self.last_complete_candle_time = self.round_time_down(time-dt.timedelta(minutes=self.granularity))
    def round_time_down(self, round_me:dt.datetime):
        remainder = round_me.minute % self.granularity
        candle_time = dt.datetime(round_me.year,
                                  round_me.month,
                                  round_me.day,
                                  round_me.hour,
                                  round_me.minute-remainder,tzinfo=pytz.timezone('UTC'))
        return  candle_time
    
    def detect_new_candle(self, price:Mt5LiveApiPrice):
        old = self.last_complete_candle_time
        self.set_last_complete_candle_time(price.time)
        if old < self.last_complete_candle_time:
            msg = f"--->>>> {self.pair} New Candle : {self.last_complete_candle_time} {price.time}"
            print(msg)
            # self.candle_queue.put(self.last_complete_candle_time)
            #moved action to caller
            return True
        else:
            return False
    
    def process_price(self):
        price = None
        try:
            self.price_lock.acquire()
            price  = copy.deepcopy(self.shared_prices[self.pair])
            
        except Exception as error:
            self.log_message(f"An exception occured in process price: {error}","error")
        finally:
            self.price_lock.release()
        if price == None:
                self.log_message("NO PRICE error in process price", "error")
        else:
            # self.log_message(f"Found price : {price}",self.pair)
            new_candle = self.detect_new_candle(price)
        if (new_candle):
            self.log_message(f"Adding work : {price}",self.pair)
            self.candle_queue.put(self.last_complete_candle_time)

    def run(self):
        while True:
            self.price_events[self.pair].wait()
            self.process_price()
            self.price_events[self.pair].clear()
