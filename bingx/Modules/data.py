from Modules.config import SCALES
import pandas as pd
import os.path


class DataHandler:
    def __init__(self, folder):
        self.dir = folder
        self.data = {}
        self.signals = {}
        self.ps = "\\"
        for scale in SCALES:
            self.data[scale[0]] = {}

    def newSignal(self, token, ivl):
        if token.symbol in self.signals.keys():
            if token.klast[ivl].time == self.signals[token.symbol]:
                return False
        self.signals[token.symbol] = token.klast[ivl].time
        return True

    def setValues(self, scale, symbol):
        li = self.data[scale][symbol]
        cp = li[0]      # ClosePrice
        sp = li[1]      # SuperTrend
        si = li[2]      # ScaleSignal
        ts = int(li[3].timestamp()) # TimeStamp
        return (cp, sp, si, ts)

    def getValues(self, line):
        sm = line[0]
        cp = float(line[1])
        sp = float(line[2])
        si = int(line[3])
        ts = pd.Timestamp(int(line[4]), unit="s")
        return [sm, cp, sp, si, ts]

    def load(self):
        for scale in SCALES:
            if os.path.isfile(f"data{self.ps}{scale[0]}"):
                with open(f'data{self.ps}{scale[0]}', 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line = [o.strip() for o in line.split(",")]
                    values = self.getValues(line)
                    self.data[scale[0]][values[0]] = values[1:]

    def save(self):
        for scale in SCALES:
            with open(f"data{self.ps}{scale[0]}", "w") as fdata:
                for symbol in self.data[scale[0]].keys():
                    v1, v2, v3, v4 = self.setValues(scale[0], symbol)
                    if None in [v1, v2, v3]:
                        continue
                    fdata.write(f"{symbol} , {v1} , {v2} , {v3} , {v4} \n")