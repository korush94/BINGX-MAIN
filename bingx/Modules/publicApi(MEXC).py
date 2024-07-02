from config import NC, METHOD, FILENAME
from datetime import timedelta
from utils import BotMsg
import time


class PublicApi:
    def __init__(self, http, private=False):
        self.ftCli = http
        self.getSymbols()
        self.nSymbol = len(self.symbols)
        BotMsg()

    def getParams(self, scale):
        n = scale[:-1]
        if 'm' in scale:
            interval = "Min" + n
            delta = timedelta(minutes=NC*int(n))
            crange = timedelta(minutes=int(n))
        elif 'h' in scale:
            interval = "Hour" + n
            delta = timedelta(hours=NC*int(n))
            crange = timedelta(hours=int(n))
        elif 'd' in scale:
            interval = "Day" + n
            delta = timedelta(days=NC)
            crange = timedelta(days=1)
        elif 'w' in scale:
            interval = "Week" + n
            delta = timedelta(weeks= int(NC*0.4))
            crange = timedelta(weeks=1)
        return interval, delta, crange

    def getKline(self, symbol, ivl, crange, tf_start, tf_end):
        kline = self.ftCli.kline(
            symbol,
            interval=ivl,
            start=tf_start,
            end=tf_end
        )
        if 'data' not in kline.keys():
            time.sleep(1)
            self.getKline(symbol, ivl, crange, tf_start, tf_end)
            return
        return kline

    def getSymbols(self):
        if METHOD == 'api':
            tickers = self.ftCli.ticker()['data']
            symbols = [ticker['symbol'] for ticker in tickers]
        elif METHOD == 'file':
            with open(FILENAME, "r") as sfile:
                lines = sfile.readlines()
                symbols = [line.strip() for line in lines]
        self.symbols = symbols
