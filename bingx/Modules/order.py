from Modules.config import R2R_RATIO, LS, LOSS_LIMIT
from Modules.utils import getParams
from Modules.pair import Token
import json


class Trade:
    def __init__(self, token:Token, http):
        self.token = token
        self.api = http
        self.levs = []
        self.loadLeverages()

    def loadLeverages(self):
        with open("leverages.txt", "r") as lFile:
            lines = lFile.readlines()
        for line in lines:
            line = line.strip().split("\t")
            val = {"leverage":int(line[0]), "diff":float(line[1]), "margin":float(line[2])}
            self.levs.append(val)

    def makeOrder(self, side:str):
        ivl, _,_ = getParams(LS)
        symbol   = self.token.symbol
        price    = round(float(self.token.klast[ivl].close), 4)
        sloss    = round(float(self.token.slast[ivl]), 4)
        lev,lossLim = self.getLeverage(price, sloss)
        target   = Trade.getTarget(price, sloss, R2R_RATIO)
        vol      = Trade.getVolume(price, sloss, lev, LOSS_LIMIT)
        print(self.api.setLeverage(symbol, lev, side))
        print(self.api.setMargin(symbol, "ISOLATED"))
        return self.api.sendOrder(symbol, side, vol, price, target, sloss)
        # return self.api.sendOrder(symbol, price, vol, leverage, sloss, target, side)

    def getLeverage(self, entry, stoploss):
        dista = abs(entry - stoploss)
        pdist = (dista / entry) * 100
        for lev in self.levs:
            if lev['diff'] <= pdist:
                return (lev['leverage'], lev['margin'])
        return 10

    @staticmethod
    def getVolume(entry, stopLoss, lev, lossLimit):
        dista = entry - stopLoss
        stLvl = abs(dista / entry) * 100
        dollarVol = (lossLimit/stLvl) * lev
        volume = dollarVol / entry
        return round(volume, 2)

    @staticmethod
    def getTarget(price, stoploss, r2r):
        dist = price - stoploss
        target = price + (dist * r2r)
        return round(target, 4)

    @staticmethod
    def getTakeProfit(price, takeProfit):
        tp = {
            "type": "TAKE_PROFIT_MARKET",
            "stopPrice": takeProfit,
            "price": price,
            "workingType": "MARK_PRICE" }
        return json.dumps(tp)

    @staticmethod
    def getStopLoss(price, stopLoss):
        sl = {
            "type": "STOP_MARKET",
            "stopPrice": stopLoss,
            "price": price,
            "workingType": "MARK_PRICE" }
        return json.dumps(sl)