
import threading
from queue import Queue
import time

from models.open_position import OpenPosition
from models.trade_decision import TradeDecision
from scalperhelper import close_order, open_counter_order
# from streaming.trade_manager import place_trade

class AvengerWorker(threading.Thread):

    def __init__(self,mt5Api,offenders_work_queue,log_message ) :
        super().__init__()
        self.mt5Api  = mt5Api
        self.offenders_work_queue = offenders_work_queue
        self.log_message = log_message

    def assign_chaser(self,position:OpenPosition ):

        print("Avenger Worker: I am about to work on some counter attack...")
        try:
          close_order(self.mt5Api,position)
          open_counter_order(self.mt5Api,position,12345,2)
          
          print("Avenger Worker: I just launched a counter attack...")
          self.log_message(f"Opened a counter orders for  : {position.pair} with {position.profit} loss", 'main')
        except Exception as error:
            self.log_message(f"Exception in avenger: {error}", 'error')


    def run(self):
        while True:
            print("Avenger Worker: Hello I am watching...")
            recent_offender:OpenPosition = self.offenders_work_queue.get()
            self.assign_chaser(recent_offender)
            
        
           