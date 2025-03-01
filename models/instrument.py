class Instrument:
    ['name', 'type', 'displayName', 'pipLocation',
         'displayPrecision', 'tradeUnitsPrecision', 'marginRate']
    def __init__(self,name,ins_type,displayName,pipLocation,displayPrecision,tradeUnitsPrecision,marginRate) -> None:
        self.name = name
        self.ins_type = ins_type
        self.displayName = displayName
        self.pipLocation = pipLocation
        self.displayPrecision = displayPrecision
        self.tradeUnitsPrecision = tradeUnitsPrecision
        self.marginRate = marginRate

    def __repr__(self) -> str:
        return str(vars(self))
    
    @classmethod
    def fromApiObject(cls,ob):
        return Instrument(
            ob['name'],
            ob['type'],
            ob['displayName'],
            ob['pipLocation'],
            ob['displayPrecision'],
            ob['tradeUnitsPrecision'],
            ob['marginRate'],
        )
        