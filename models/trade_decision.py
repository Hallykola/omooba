class TradeDecision:

    def __init__(self, row,index=0):
        self.gain = row.GAIN
        self.loss = row.LOSS
        self.signal = row.SIGNAL
        self.sl = row.SL
        self.tp = row.TP
        self.pair = row.PAIR
        self.id = index

    def __repr__(self):
        return f"TradeDecision():{self.id} {self.pair} dir:{self.signal} gain:{self.gain:.4f} loss:{self.loss:.4f} sl:{self.sl:.4f}  tp:{self.tp:.4f}"