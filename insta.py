import requests


from zeep import Client
from zeep.exceptions import Fault
from datetime import datetime


class InstaApi:
    def __init__(self):
        self.quoteURL = "https://quotes.instaforex.com/api/quotesTick"
        self.wsdl = 'https://client-api.instaforex.com/soapservices/charts.svc?wsdl'

    
    def sendRequest(self,url,code=200):
        response = requests.get(url)
        if response.status_code == code:
            data = response.json()
            print(data)
            ok = True
            return ok,data  
        else:
            print(f"Error fetching data. Status code: {response.status_code}")
            ok = False
            return ok,response  


    def getQuotes(self,symbol_list:list):
        mysymbol_list = ',,'.join(symbol_list)
        url = f"{self.quoteURL}?q={mysymbol_list}"
        ok, response = self.sendRequest(url)
        if (ok):
            print(response)
            return response
        else:
            print(response)

    def datetime_to_unix(self,dt):
        time =  int(dt.timestamp())
        print(time)
        return time

    def getHistoricalCandles(self,pair,granularity,from_time:datetime,to_time:datetime):
        # from_time = datetime(2012, 1, 1)  # Example start date
        # to_time = datetime(2012, 10, 30)  # Example end date

        # Convert to Unix timestamps
        from_unix = self.datetime_to_unix(from_time)
        to_unix = self.datetime_to_unix(to_time)
        client = Client(self.wsdl)
        params = {
            'chartRequest': {
                'From': from_unix,  # Start timestamp
                'To': to_unix,  # End timestamp
                'Symbol': pair,  # Currency pair
                'Type': "MN"  # Candlestick type (MN, W1, D1, H4, H1, M30, M15, M5, and M1)
            }
        }
        try:
            response = client.service.GetCharts(params)
            print(response)
        except Fault as fault:
            print(f"SOAP Fault: {fault}")


api= InstaApi()
# api.getQuotes(["EURUSD","USDJPY"])
api.getHistoricalCandles("USDJPY","MN",datetime(2024, 1, 1),datetime(2024, 4, 30))