
import threading
from queue import Queue
import time

from constants import defs
from models.trade_decision import TradeDecision
from scalperhelper import close_order
from streaming.scalper_baby import ScalperBaby
# from streaming.trade_manager import place_trade

class ScalperWorker(threading.Thread):

    def __init__(self,mt5Api,pair,monitored_positions,offenders_work_queue,threads,hedger_and_hedged_positions,fireworks_and_positions,trade_settings,techs,log_message ) :
        super().__init__()
        self.mt5Api  = mt5Api
        self.pair  = pair
        self.monitored_positions = monitored_positions
        self.offenders_work_queue = offenders_work_queue
        self.threads = threads
        self.hedger_and_hedged_positions = hedger_and_hedged_positions
        self.fireworks_and_positions = fireworks_and_positions
        self.trade_settings = trade_settings
        self.techs = techs
        self.log_message = log_message


    def run(self):
        while True:
            try:
                positions=self.mt5Api.positions_get(symbol=self.pair)
                # print(f"see positions {positions} ")
                for position in positions:
                        if position.ticket not in self.monitored_positions:
                            scalperbaby_thread = ScalperBaby(self.mt5Api,position,self.offenders_work_queue,self.hedger_and_hedged_positions,self.fireworks_and_positions,self.trade_settings,self.techs,self.log_message)
                            scalperbaby_thread.daemon = True
                            self.threads.append(scalperbaby_thread)
                            scalperbaby_thread.start()

                            self.monitored_positions[position.ticket] = position
                            print(f'{position.symbol} ticket id:{position.ticket} is now being monitored')
                            self.log_message(f'{position.symbol} ticket id:{position.ticket} is now being monitored','main')
                            self.log_message(f'{position.symbol} ticket id:{position.ticket} is now being monitored',position.symbol)
            except Exception as error:
                self.log_message(f"Exception in Scalpworker: {error}", 'error')
            time.sleep(2)
        
           