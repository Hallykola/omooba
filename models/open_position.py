from dateutil import parser

class OpenPosition:

    def __init__(self, api_ob):
        self.id = api_ob['ticket']
        self.time = api_ob['time']
        self.time_msc = api_ob['time_msc']
        self.volume = float(api_ob['volume'])
        self.price_open = float(api_ob['price_open'])
        self.price_current = float(api_ob['price_current'])
        self.profit = float(api_ob['profit'])
        self.symbol = api_ob['symbol']
        self.sl = float(api_ob['sl'])
        self.tp = float(api_ob['tp'])
        

    def __repr__(self):
        return str(vars(self))
    