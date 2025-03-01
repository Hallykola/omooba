from dateutil import parser
class LiveApiPrice:
    def __init__(self,api_ob) :
        self.instrument = api_ob['instrument']
        self.ask = float(api_ob['asks'][0]['price'])
        self.bid = float(api_ob['bids'][0]['price'])
        self.time = parser.parse(api_ob['time'])

    def __repr__(self) -> str:
        return str(vars(self))

    def get_dict(self):
        return dict(
            instrument=self.instrument,
            time = self.time,
            ask=self.ask,
            bid=self.bid
        )