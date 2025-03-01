import threading
from queue import Queue

from models.trade_decision import TradeDecision
from streaming.trade_manager import place_trade

import datetime as dt
import pytz



class TradeWorker(threading.Thread):

    def __init__(self,mt5Api,trade_work_queue:Queue,trade_risk: float,log_message ) :
        super().__init__()
        self.mt5Api  = mt5Api
        self.trade_work_queue  = trade_work_queue
        self.log_message = log_message
        self.trade_risk = trade_risk

    def work_on_trade(self,trade_decision):
        try:
            current_time = dt.datetime.now(pytz.timezone('UTC'))
            
            place_trade(
                self.mt5Api, 
                trade_decision,
                self.trade_risk, 
                self.log_message)
        except Exception as error:
            self.log_message(f"Exception in work_on_trade: {error}", 'error')

    def run(self):
        while True:
            trade_decision:TradeDecision  = self.trade_work_queue.get()
            self.log_message(f"TradeWorker : {trade_decision}", 'main')
            self.log_message(f"TradeWorker : {trade_decision}", trade_decision.pair)
            self.work_on_trade(trade_decision)
            print("TradeWorker : ", trade_decision)
        
           