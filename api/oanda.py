import json
import requests
import sys

from models.api_price import ApiPrice
from models.open_trade import OpenTrade
sys.path.append('../')
import constants.defs as defs
import pandas as pd
import datetime as dt
from dateutil import parser
from infrastructure.instrument_collection import instrumentCollection as ic


class OandaApi:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({
            'Authorization': f"Bearer {defs.API_KEY}",
            "Content-Type":"application/json"
        })
    def makeRequest(self,url,params=None, headers=None, data=None, reqmethod='get', code=200):
        full_url = f"{defs.OANDA_URL}/{url}"
        try:
            if reqmethod == "get":
                response = self.session.get(full_url,params=params,data=data, headers=headers,)
            elif reqmethod == "post":
                response = self.session.post(full_url,params=params,data=data, headers=headers,)
            elif reqmethod == "put":
                response = self.session.put(full_url,params=params,data=data, headers=headers,)
            elif reqmethod == "delete":
                response = self.session.delete(full_url,params=params,data=data, headers=headers,)
            else:
                print("Method not found or implemented")
                return
            # print(response.json())
            if response.status_code == code:
                
                return True, response.json()
            else:
                return False,  response.json
        except Exception as error:
            print("An error occured")
            return False, error
        
    def getEndPoint(self,endpoint,keyOfInterest, section='accounts' ):
        url = f"{section}/{defs.ACCOUNT_ID}/{endpoint}" 
        ok,data = self.makeRequest(url)
        if ok:
            # print(data[keyOfInterest])
            return data[keyOfInterest]
        else:
            return {"Error":data}

    def getAccountSummary(self):
        return self.getEndPoint('summary','account')
    
    def getAccountInstruments(self):
        return self.getEndPoint('instruments','instruments')
    
    def fetch_candles(self, pair_name, count=10, granularity="H1",
                            price="MBA", date_f=None, date_t=None):
        url = f"instruments/{pair_name}/candles"
        params = dict(
            granularity = granularity,
            price = price
        )

        if date_f is not None and date_t is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params["from"] = dt.strftime(date_f, date_format)
            params["to"] = dt.strftime(date_t, date_format)
        else:
            params["count"] = count

        ok, data = self.makeRequest(url, params=params)
    
        if ok == True and 'candles' in data:
            return data['candles']
        else:
            print("ERROR fetch_candles()", params, data)
            return None

    def get_candles_df(self, pair_name, **kwargs):

        data = self.fetch_candles(pair_name, **kwargs)

        if data is None:
            return None
        if len(data) == 0:
            return pd.DataFrame()
        
        prices = ['mid', 'bid', 'ask']
        ohlc = ['o', 'h', 'l', 'c']
        
        final_data = []
        for candle in data:
            if candle['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = parser.parse(candle['time'])
            new_dict['volume'] = candle['volume']
            for p in prices:
                if p in candle:
                    for o in ohlc:
                        new_dict[f"{p}_{o}"] = float(candle[p][o])
            final_data.append(new_dict)
        df = pd.DataFrame.from_dict(final_data)
        return df

    def place_trade(self, pair_name: str, units: float, direction: int,
                        stop_loss: float=None, take_profit: float=None):

        url = f"accounts/{defs.ACCOUNT_ID}/orders"

        instrument = ic.instruments_dict[pair_name]
        units = round(units, instrument.tradeUnitsPrecision)

        if direction == defs.SELL:
            units = units * -1        

        data = dict(
            order=dict(
                units=str(units),
                instrument=pair_name,
                type="MARKET"
            )
        )

        if stop_loss is not None:
            sld = dict(price=str(round(stop_loss, instrument.displayPrecision)))
            data['order']['stopLossOnFill'] = sld

        if take_profit is not None:
            tpd = dict(price=str(round(take_profit, instrument.displayPrecision)))
            data['order']['takeProfitOnFill'] = tpd

        #print(data)
        data = json.dumps(data)

        ok, response = self.makeRequest(url, reqmethod="post", data=data, code=201)

        # print(ok, response)

        if ok == True and 'orderFillTransaction' in response:
            return ok, response['orderFillTransaction']['id']
        else:
            return ok, response
            
    def close_trade(self, trade_id):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}/close"
        ok, _ = self.makeRequest(url, reqmethod="put", code=200)

        if ok == True:
            print(f"Closed {trade_id} successfully")
        else:
            print(f"Failed to close {trade_id}")

        return ok

    def get_open_trade(self, trade_id):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}"
        ok, response = self.makeRequest(url)

        if ok == True and 'trade' in response:
            return OpenTrade(response['trade'])

    def get_open_trades(self):
        url = f"accounts/{defs.ACCOUNT_ID}/openTrades"
        ok, response = self.makeRequest(url)

        if ok == True and 'trades' in response:
            return [OpenTrade(x) for x in response['trades']]

    def get_prices(self, instruments_list):
        url = f"accounts/{defs.ACCOUNT_ID}/pricing"

        params = dict(
            instruments=','.join(instruments_list),
            includeHomeConversions=True
        )

        ok, response = self.makeRequest(url, params=params)

        if ok == True and 'prices' in response and 'homeConversions' in response:
            return [ApiPrice(x, response['homeConversions']) for x in response['prices']]

        return None
