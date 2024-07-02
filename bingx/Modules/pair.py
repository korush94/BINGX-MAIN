 
from Modules.config import STP, NF, STP, STF, LS, SCALES
from stock_indicators import indicators, Quote
from datetime import datetime, timezone
from Modules.utils import getParams
import pandas as pd
import numpy as np


class Token:
    def __init__(self, api, datahandler, symbol):
        self.symbol = symbol
        self.dh = datahandler
        self.scales = {}
        for sc in SCALES:
            if sc[1]:
                self.scales[sc[0]] = sc
        self.api = api
        self.klast, self.slast = {}, {}
        self.setNow()

    def setNow(self):
        self.now = pd.Timestamp(
            int(datetime.now(tz=timezone.utc).timestamp()), unit="s")
        self.tf_end = int(self.now.timestamp() * 1000)

    def kData(self, ivl, crange):
        kline = self.api.getKline(self.symbol, ivl,
                              self.tf_start, self.tf_end)
        if kline is None:
            return None
        kdata = pd.DataFrame(kline)
        for col in ['open', 'high', 'low', 'close']:
            kdata[col] = kdata[col].astype(np.float64)
        kdata.time = pd.to_datetime(kdata.time, unit='ms')
        if kdata.shape[0] < STP:
            return None
        row = kdata.iloc[-1].copy()
        row['endt'] = row.time + crange
        self.klast[ivl] = row
        return kdata

    def getQuotes(self, kdata):
        try:
            quotes = [
                Quote(d,o,h,l,c,v)
                for d,o,h,l,c,v
                in zip(kdata.time, kdata.open, kdata.high, kdata.low, kdata.close, kdata.volume)
            ]
        except :
            quotes = [
                Quote(
                    d, format(float(o),f'.{NF}f'), format(float(h),f'.{NF}f'),
                    format(float(l),f'.{NF}f'), format(float(c),f'.{NF}f'), v
                )
                for d,o,h,l,c,v
                in zip(kdata.time, kdata.open, kdata.high, kdata.low, kdata.close, kdata.volume)
            ]
        return quotes

    def superTrend(self, quotes, ivl, second=False):
        sdata = indicators.get_super_trend(quotes, lookback_periods=STP, multiplier=STF)
        supertrend = sdata[-1]
        if second:
            self.st2 = sdata[-2]
        self.slast[ivl] = np.float64(supertrend.super_trend)
        if supertrend.lower_band is None:
            return -1 # SELL
        elif supertrend.upper_band is None:
            return  1 # BUY

    def getData(self, scale):
        ivl, delta, crange = getParams(scale)
        self.tf_start = int((self.now - delta).timestamp() * 1000)
        kdata = self.kData(ivl, crange)
        if kdata is None:
            return None
        quotes = self.getQuotes(kdata)
        state = self.superTrend(quotes, ivl)
        self.dh.data[scale][self.symbol] = [
            self.klast[ivl].close, self.slast[ivl],
            state, self.klast[ivl].time
        ]
        return state

    def checkScales(self):
        check = []
        for scale in self.scales:
            if (len(check) != sum(check)) and (-len(check) != sum(check)):
                return False
            if self.scales[scale]:
                state = self.getData(scale)
                if state is None: continue
            else:
                state = self.dh.data[scale][self.symbol][2]
            check.append(state)
        if (sum(check) == len(self.scales)) or (sum(check) == -len(self.scales)):
            self.check = check
            return True
        else:
            return False

    def checkShort(self):
        # print("!!", self.symbol, "- HighChance !!")
        ivl, delta, crange = getParams(LS)
        self.setNow()
        self.tf_start = int((self.now - delta).timestamp())
        kdata = self.kData(ivl, crange)
        quotes = self.getQuotes(kdata)
        st_signal = self.superTrend(quotes, ivl, True)
        self.check.append(st_signal)
        if sum(self.check) == len(self.scales)+1 or sum(self.check) == -(len(self.scales))-1:
            print(f"!! {self.symbol} !!")
            if (self.st2.lower_band is None) and (sum(self.check) == len(self.scales)+1):
                self.sig = "BUY"
                self.side = "LONG"
                return self.dh.newSignal(self, ivl)
            elif (self.st2.upper_band is None) and (sum(self.check) == (-len(self.scales))-1):
                self.sig = "SELL"
                self.side = "SHORT"
                return self.dh.newSignal(self, ivl)
        return False

    def load(self):
        for scale in self.scales:
            scale_data = self.dh.data[scale]
            if self.symbol in scale_data.keys():
                ivl, _, crange = getParams(scale)
                limit = self.now - (crange * 2)
                last = scale_data[self.symbol][3]
                if limit < last:
                    self.klast[ivl] = pd.DataFrame.from_dict({
                        'time' : [last,],
                        'endt' : [last+crange,],
                        'close' : [scale_data[self.symbol][0],]
                    }).iloc[0]
                    self.slast[ivl] = scale_data[self.symbol][1]
                    self.scales[scale] = False