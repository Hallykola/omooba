# from dateutil import parser
import datetime
class Mt5LiveApiPrice:
    def __init__(self,instrument,api_ob) :
        self.instrument = instrument
        self.ask = float(api_ob['ask'])
        self.bid = float(api_ob['bid'])
        self.time = datetime.datetime.fromtimestamp(float(api_ob['time_msc'])/1000) - datetime.timedelta(hours=1)
        # print("troublemaker",self.time)


    def __repr__(self) -> str:
        return str(vars(self))

    def get_dict(self):
        return dict(
            instrument=self.instrument,
            time = self.time,
            ask=self.ask,
            bid=self.bid
        )