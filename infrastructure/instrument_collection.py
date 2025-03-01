import json
from models import instrument
class InstrumentCollection:
    FILENAME = "instruments.json"
    API_KEYS = ['name', 'type', 'displayName', 'pipLocation',
         'displayPrecision', 'tradeUnitsPrecision', 'marginRate']
    
    def __init__(self) -> None:
        self.instruments_dict = {}
    def LoadInstruments(self,path):
        fullPath =  f"{path}/{self.FILENAME}"
        with open(fullPath,'r') as f:
            data = json.loads(f.read())
            for k,v in data.items():
                self.instruments_dict[k] = instrument.Instrument.fromApiObject(v)

    def CreateFile(self,path,data):
        if data is None:
            print("Instrument file creation failed")
            return
        
        instruments_dict = {}
        for i in data:
            key = i['name']
            instruments_dict[key] = { k: i[k] for k in self.API_KEYS }

        fileName = f"{path}/{self.FILENAME}"
        with open(fileName, "w") as f:
            f.write(json.dumps(instruments_dict, indent=2))


    def PrintInstruments(self):
        [print(k,v) for k,v in self.instruments_dict.items()]
        print(len(self.instruments_dict.keys()), "instruments")

instrumentCollection = InstrumentCollection()



