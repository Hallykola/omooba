
import threading
from queue import Queue
import time

from constants import defs
from models.trade_decision import TradeDecision
from scalperhelper import close_order, close_order_partially, hedge_position_if_needed, use_fireworks_if_possible
# from streaming.trade_manager import place_trade

class ScalperBaby(threading.Thread):

    def __init__(self,mt5Api,position,offenders_work_queue,hedger_and_hedged_positions,fireworks_and_positions,trade_settings,techs,log_message ) :
        super().__init__()
        self.mt5Api  = mt5Api
        self.position  = position
        self.offenders_work_queue = offenders_work_queue
        self.hedger_and_hedged_positions = hedger_and_hedged_positions
        self.fireworks_and_positions = fireworks_and_positions
        self.trade_settings = trade_settings
        self.techs = techs
        self.log_message = log_message

    def monitor_profit(self, position,max_loss,min_gain):
        # print(f'fireworks record {self.fireworks_and_positions.get("abc","yaya")}')

        #adjust monitor for differeent lot sizes especially for avenger trades
        lot_multiple = (self.position.volume)/defs.my_lot_size
        print(f"profit: {position.profit}  and exit: {max_loss*lot_multiple} from => maxloss :{max_loss} and  lot multiple:{lot_multiple} ")
        # print(f'techs in scalper {self.techs["ATR"]}')
        try:
            positions = self.mt5Api.positions_get(ticket=position.ticket)
            if positions == None:
                return
            position= positions[0]
            
            max_profit = position.profit
            count = 0
            loss=0
            percent_loss = 0
            while True:
                
                maxpips = 8*self.trade_settings.pip  # self.techs["ATR"] * 2.0   #10
                print(f'max pip for avenging in scalper {self.techs["ATR"]} times 2.0 {maxpips}')
                # hedge_position_if_needed(self.mt5Api,position,self.hedger_and_hedged_positions,maxpips)
                count = count + 1
                time.sleep(1)
                # allpositions=self.mt5Api.positions_get(symbol=position.symbol)
                positions=self.mt5Api.positions_get(ticket=position.ticket)
                if positions == None:
                    return
                position= positions[0]
                pip_diff = abs(position.price_open - position.price_current)

                #handle negative profit to wait while not less than bearable threashold
                if position.profit < 0: 
                    print(f" i am in monitor profit for {position.symbol}'s but its  profit is less than 0")
                    if  pip_diff > maxpips:
                        break     #position.profit < (defs.report_loss_threashold*lot_multiple) :
                        # pass
                        # # avoid a counter counter
                        # if position.comment.find("avenger") == -1:  #lot_multiple < 2:  #27 if len(allpositions) < 2
                        #     print(f"Putting offender {position.symbol} in queue")
                        #     self.offenders_work_queue.put(position)
                        #     break
                            # time.sleep(3)
                    # elif position.profit  > (max_loss*lot_multiple):
                    #     continue
                    else:
                        # break
                        continue

                if position.profit > max_profit:
                    max_profit = position.profit
                    loss = 0
                    use_fireworks_if_possible(self.mt5Api,position,self.fireworks_and_positions,self.log_message,4)


                elif position.profit < (min_gain*lot_multiple):   #pip_diff < 3*self.trade_settings.pip:        #(self.techs["ATR"] * 0.5):       # # #  #
                    continue
                else:
                    loss = max_profit - position.profit
                    percent_loss = ((abs(loss)/max_profit)*100)
                    if percent_loss > 15:
                        break
                if count % 2 == 0:
                    print(f"current profit: {position.profit}, max profit: {max_profit}...loss{loss} ... percentage loss {percent_loss}")
                
            close_order(self.mt5Api,position)
            # self.handle_hedged_position_if_hedger(position)
            
            # i may need to clean or reset variables for next use

        except Exception as error:
            self.log_message(f"Exception in monitor profit: {error}", 'error')

    def handle_hedged_position_if_hedger(self,position):
        hedged_ticket = self.hedger_and_hedged_positions[position.ticket]
        if (position.profit > 0) and hedged_ticket != None:
            hedged_position = self.mt5Api.positions_get(ticket=hedged_ticket)[0]
            close_order_partially(self.mt5Api,hedged_position, 0.01)
            self.hedger_and_hedged_positions[position.ticket]= None

    def run(self):
        while True:
            # pass
            # self.log_message(f"ScalperWorker : ", 'main')
            # self.log_message(f"ScalperWorker : ", self.pair)
            # print("Scalper Worker: Hello")
            #paused scalperworker
            
            self.monitor_profit(self.position,-1.3,0.5)   # -0.9,0.30)  #0.35
            
        
           