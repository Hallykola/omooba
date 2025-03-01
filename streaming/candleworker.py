import threading
from queue import Queue
import datetime as dt
import time
import pytz

from constants import defs
from models.trade_decision import TradeDecision
from streaming.technical_analysis import process_candles, process_candles_for_harmonics, process_candles_for_neat, process_candles_get_crossover

from datetime import datetime
from mt5linux import MetaTrader5 as mt5
# import MetaTrader5 as mt5

import pandas as pd

from streaming.trade_manager import close_pair_trade


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

class CandleWorker(threading.Thread):
    def __init__(self,mt5Api,pair,trade_settings,candle_queue:Queue,trade_work_queue:Queue,granularity,techs,log_message):
        super().__init__()
        self.trade_settings= trade_settings
        self.candle_queue= candle_queue
        self.granularity= granularity
        self.log_message= log_message
        self.pair= pair
        self.mt5Api = mt5Api
        self.trade_work_queue = trade_work_queue
        self.techs = techs

    def getCandlesDf(self,pair,granularity,count):
        rates = self.mt5Api.copy_rates_from_pos(pair, mt5TimeFrame[granularity], 0, count)
        
        # create DataFrame out of the obtained data
        rates_frame = pd.DataFrame(rates)
        rates_frame = rates_frame.iloc[:-1]
        # convert time in seconds into the datetime format
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame['mid_h']=rates_frame['high']
        rates_frame['mid_l']=rates_frame['low']
        rates_frame['mid_c']=rates_frame['close']
        rates_frame['mid_o']=rates_frame['open']
        rates_frame['ask_h']=rates_frame['high']+ rates_frame['spread']*self.trade_settings.pip
        rates_frame['ask_l']=rates_frame['low']+ rates_frame['spread']*self.trade_settings.pip
        rates_frame['ask_c']=rates_frame['close']+ rates_frame['spread']*self.trade_settings.pip
        rates_frame['ask_o']=rates_frame['open']+ rates_frame['spread']*self.trade_settings.pip
        rates_frame['bid_h']=rates_frame['high']- rates_frame['spread']*self.trade_settings.pip
        rates_frame['bid_l']=rates_frame['low']- rates_frame['spread']*self.trade_settings.pip
        rates_frame['bid_c']=rates_frame['close']- rates_frame['spread']*self.trade_settings.pip
        rates_frame['bid_o']=rates_frame['open']- rates_frame['spread']*self.trade_settings.pip
        
        rates_frame['volume']=rates_frame['tick_volume']

        print("I just got my past data for analysis and for checking if last candle is recent")
        # print(rates_frame.tail())
        self.log_message(rates_frame,pair)
        return rates_frame
    
    def get_multi_timeframes(self):
        h4_candles_df = self.getCandlesDf(self.pair,'H4',70)
        h1_candles_df = self.getCandlesDf(self.pair,'H1',70)
        m30_candles_df = self.getCandlesDf(self.pair,'M30',70)
        m15_candles_df = self.getCandlesDf(self.pair,'M15',70)
        m5_candles_df = self.getCandlesDf(self.pair,'M5',70)
        h4_last_row = process_candles_get_crossover(h4_candles_df)
        h1_last_row = process_candles_get_crossover(h1_candles_df)
        m30_last_row = process_candles_get_crossover(m30_candles_df)
        m15_last_row = process_candles_get_crossover(m15_candles_df)
        m5_last_row = process_candles_get_crossover(m5_candles_df)
        print(f"CandleWorker {self.trade_settings.pair} SIGNALS m5: { m5_last_row.SIGNAL}, m15: { m15_last_row.SIGNAL}, m30: { m30_last_row.SIGNAL},h1: { h1_last_row.SIGNAL},h4: { h4_last_row.SIGNAL}",)
        if (h4_last_row.MA_50_CROSS_200 == h1_last_row.MA_50_CROSS_200 & h4_last_row.MA_50_CROSS_200 == m30_last_row.MA_50_CROSS_200 & h4_last_row.MA_50_CROSS_200 == m15_last_row.MA_50_CROSS_200 & h4_last_row.MA_50_CROSS_200 == m5_last_row.MA_50_CROSS_200):
            if m5_last_row is None:
                self.log_message("process_candles failed", "error")
                return
            
            print(f"CandleWorker {self.trade_settings.pair} SIGNAL", m5_last_row.SIGNAL)

            if m5_last_row.SIGNAL != defs.NONE:
                td: TradeDecision = TradeDecision(m5_last_row)
                print(f"CandleWorker {self.trade_settings.pair} TradeDecision", td)
                self.log_message(f"CandleWorker {self.trade_settings.pair} TradeDecision {td}", self.trade_settings.pair)
                self.trade_work_queue.put(td)

    def get_trade_decision(self,candles_df): 
        try:
            
            process_candles_for_harmonics(candles_df,self.trade_settings.pair,self.trade_settings,self.techs,self.mt5Api,self.log_message)
            print("Alajobo")
            return
            #  last_row = process_candles(
            #     candles_df, 
            #     self.trade_settings.pair,
            #     self.trade_settings,
            #     self.techs,
            #     self.log_message
            # )
            if last_row is None:
                self.log_message("process_candles failed", "error")
                return
            
            print(f"CandleWorker {self.trade_settings.pair} SIGNAL", last_row.SIGNAL)
            
            current_time = dt.datetime.now(pytz.timezone('UTC'))
            print(f"current time UTC is {current_time}")
            print(f"current time UTC+1 lagos hour is {current_time.hour +1}")
            
            # self.check_close_trade_ma_strategy(last_row)

            if last_row.SIGNAL != defs.NONE:
                td: TradeDecision = TradeDecision(last_row)
                print(f"CandleWorker {self.trade_settings.pair} TradeDecision", td)
                self.log_message(f"CandleWorker {self.trade_settings.pair} TradeDecision {td}", self.trade_settings.pair)
                if (current_time.hour+1>12 and current_time.hour+1<20):
                    print("Safe Trading period")
                    self.log_message("Safe Trading period")
                    self.trade_work_queue.put(td)
                else:
                    print("Unsafe Trading period. Trade Decision not passed for execution")
                    self.log_message("Unsafe Trading period. Trade Decision not passed for execution",'main')
            
        except Exception as error:
            self.log_message(f"Exception in get trade decision: {error}", "error")
        
    # def get_trade_decision(self,candles_df): 
    #     try:
    #         process_candles_for_neat(candles_df,self.trade_settings.pair,self.trade_settings,self.techs,self.mt5Api,self.log_message)
    #         return
    #         #  last_row = process_candles(
    #         #     candles_df, 
    #         #     self.trade_settings.pair,
    #         #     self.trade_settings,
    #         #     self.techs,
    #         #     self.log_message
    #         # )
    #         if last_row is None:
    #             self.log_message("process_candles failed", "error")
    #             return
            
    #         print(f"CandleWorker {self.trade_settings.pair} SIGNAL", last_row.SIGNAL)
            
    #         current_time = dt.datetime.now(pytz.timezone('UTC'))
    #         print(f"current time UTC is {current_time}")
    #         print(f"current time UTC+1 lagos hour is {current_time.hour +1}")
            
    #         # self.check_close_trade_ma_strategy(last_row)

    #         if last_row.SIGNAL != defs.NONE:
    #             td: TradeDecision = TradeDecision(last_row)
    #             print(f"CandleWorker {self.trade_settings.pair} TradeDecision", td)
    #             self.log_message(f"CandleWorker {self.trade_settings.pair} TradeDecision {td}", self.trade_settings.pair)
    #             if (current_time.hour+1>12 and current_time.hour+1<20):
    #                 print("Safe Trading period")
    #                 self.log_message("Safe Trading period")
    #                 self.trade_work_queue.put(td)
    #             else:
    #                 print("Unsafe Trading period. Trade Decision not passed for execution")
    #                 self.log_message("Unsafe Trading period. Trade Decision not passed for execution",'main')
            
    #     except Exception as error:
    #         self.log_message(f"Exception in get trade decision: {error}", "error")
        

    # def check_close_trade_ma_strategy(self,last_row):
    #     if last_row.PRICE_CROSS_BB_MA == 1:
    #         close_pair_trade(self.mt5Api,last_row.PAIR)

    def run_analysis(self,expected_time:dt.datetime):
        attempts = 0
        tries = 10
        try:
            while attempts < tries:
                # candles_df = self.api.get_candles_df(self.pair,granularity=self.granularity,count=50)
                print("See o",self.pair,self.granularity,200)
                candles_df = self.getCandlesDf(self.pair,self.granularity,200)
                
                if candles_df.shape[0] == 0:
                    self.log_message('No candles',"error")
                    print("NO CANDLES")
                elif str(candles_df.iloc[-1].time) != str(expected_time).split('+')[0]:
                    print("NO NEW CANDLE",candles_df.iloc[-1].time,str(expected_time).split('+')[0])
                    self.log_message('No new candles',"error")
                    time.sleep(0.5)
                    
                else:
                    self.get_trade_decision(candles_df)
                    # self.get_multi_timeframes()
                    break
                tries +=1
        except Exception as error:
            self.log_message(f"Exception in run_analysis: {error}", "error")
        # print("check time",candles_df.iloc[-1].time)
        # print("expected time",expected_time)
        # print("are they the same",candles_df.iloc[-1].time != expected_time)
        # print('I broke out')


    def run(self):
        while True:
            last_candle_time:dt.datetime = self.candle_queue.get()
            print(f"CandleWorker new candle : {last_candle_time} {self.trade_settings.pair}")
            self.run_analysis(last_candle_time)




