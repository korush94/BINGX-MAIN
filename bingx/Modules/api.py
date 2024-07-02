from Modules.config import METHOD, FILENAME
from bingX import BingX, ClientError
from Modules.utils import BotMsg
from Modules.order import Trade
import requests
import hashlib
import hmac
import time


class PublicApi:
    def __init__(self, api_key, api_sec):
        self.publicCli  = BingX(api_key, api_sec)
        self.getSymbols()
        self.nSymbol = len(self.symbols)
        self.nRequests = 0
        BotMsg()

    def getKline(self, symbol, ivl, tf_start, tf_end):
        self.nRequests += 1
        try:
            kline = self.publicCli.perpetual_v2.market.get_k_line_data(
                symbol=symbol, interval=ivl,
                start_time=tf_start, end_time=tf_end
            )    
        except ClientError:
            return None
        return kline

    def getSymbols(self):
        if METHOD == 'api':
            # tickers = self.cli.ticker()['data']
            # symbols = [ticker['symbol'] for ticker in tickers]
            pass
        elif METHOD == 'file':
            with open(FILENAME, "r") as sfile:
                lines = sfile.readlines()
                symbols = [line.strip() for line in lines]
        self.symbols = symbols


class PrivateApi:
    def __init__(self, api_key:str, api_secret:str):
        self.apisec = api_secret
        self.apikey = api_key
        self.base = "https://open-api.bingx.com"
        self.makeSession()

    def makeSession(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/JSON",
            "X-BX-APIKEY": self.apikey
        })

    def sign(self, params:dict):
        sortedKeys = sorted(params)
        query = "&".join([f"{key}={params[key]}" for key in sortedKeys])
        timestamp = str(int(time.time() * 1000))
        if query != "":
            query = query + "&timestamp=" + timestamp
        else:
            query = query + "timestamp=" + timestamp
        signature = hmac.new(
            self.apisec.encode("utf-8"), query.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()
        return (signature, query)

    def getUrl(self, altUrl:str, params:dict):
        signature, query = self.sign(params)
        url = self.base + altUrl + "?" + query + "&signature=" + signature
        return url

    def getBalance(self):
        altUrl = "/openApi/swap/v2/user/balance"
        url = self.getUrl(altUrl, {})
        resp = self.session.get(url)
        assets = resp.json()['data']['balance']
        bal = assets['availableMargin']
        return float(bal)

    def getLeverage(self, symbol, side):
        altUrl = "/openApi/swap/v2/trade/leverage"
        url = self.getUrl(altUrl, {"symbol":symbol})
        resp = self.session.get(url).json()['data']
        if side == "SHORT":
            lev = resp['shortLeverage']
            maxLev = resp['maxShortLeverage']
        else:
            lev = resp['longLeverage']
            maxLev = resp['maxLongLeverage']
        return lev, maxLev

    def setLeverage(self, symbol, leverage, side):
        altUrl = "/openApi/swap/v2/trade/leverage"
        url = self.getUrl(altUrl, {"symbol":symbol, "side":"BOTH", "leverage":leverage})
        resp = self.session.post(url)
        return resp.json()
        if resp.json()['code'] == 0:
            return True
        return False

    def getMargin(self, symbol):
        altUrl = "/openApi/swap/v2/trade/marginType"
        url = self.getUrl(altUrl, {"symbol":symbol})
        resp = self.session.get(url).json()
        return resp['data']['marginType']

    def setMargin(self, symbol, marginType="ISOLATED"):
        altUrl = "/openApi/swap/v2/trade/marginType"
        url = self.getUrl(altUrl, {"symbol":symbol, "marginType":marginType})
        resp = self.session.post(url)
        return resp.json()
        if resp.json()['code'] == 0:
            return True
        return False

    def sendOrder(self, symbol, positionSide, quantity, price, takeProfit, stopLoss):
        payload = {}
        altUrl = "/openApi/swap/v2/trade/order"
        params = {
            "symbol": symbol,
            "side": "BUY", # (BUY | SELL)
            "positionSide": "BOTH", # (LONG | SHORT)
            "type": "MARKET",
            "quantity": quantity,
            "takeProfit": Trade.getTakeProfit(price, takeProfit),
            "stopLoss": Trade.getStopLoss(price, stopLoss),
        }
        url = self.getUrl(altUrl, params)
        resp = self.session.post(url, data=payload)
        print(symbol, positionSide, quantity, price, takeProfit, stopLoss)
        return resp.json()