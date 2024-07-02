from datetime import datetime
import requests
import hashlib
import json
import hmac


class PrivateApi:
    def __init__(self, apiKey:str, apiSecret:str):
        self.apikey = apiKey
        self.apisec = apiSecret
        self.base = "https://contract.mexc.com/"
        self.makeSession()

    def makeSession(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/JSON",
            "ApiKey": self.apikey
        })

    def sign(self, params:dict, method:str):
        timestamp = str(int(datetime.now().timestamp() * 1000))
        if method == "GET":
            kv = []
            for key, value in params.items():
                kv.append(f"{key}={value}")
            query = "&".join(kv)
        elif method == "POST":
            query = json.dumps(params)
        query = self.apikey + timestamp + query
        signature = hmac.new(
            self.apisec.encode("utf-8"), query.encode("utf-8"), 
            digestmod= hashlib.sha256
        ).hexdigest()
        self.session.headers.update({
            "Request-Time": timestamp,
            "Signature": signature
        })

    def getBalance(self, symbol="USDT"):
        url = "api/v1/private/account/asset/"
        url = self.base + url + symbol
        self.sign({}, "GET")
        respJson = self.session.get(url).json()
        balance = respJson['data']['equity']
        return balance

    def getAssets(self):
        url = self.base + "api/v1/private/account/assets"
        self.sign({}, "GET")
        response = self.session.get(url)
        return response

    def sendOrder(self, symbol:str, price:float, volume:float, leverage:int, stopLoss:float, target:float, side:str):
        url = self.base + "api/v1/private/order/submit"
        params = {
            "symbol": symbol,
            "price": price,
            "vol": volume, # Base Currency Quantity
            "leverage": leverage,
            "stopLossPrice": stopLoss,
            "takeProfitPrice": target,
            "side": 1 if side == "LONG" else 3,
            "type": 5,     # Market Orders
            "openType": 1, # Isolated
        }
        self.sign(params, "POST")
        response = self.session.post(url, json=params)
        return response