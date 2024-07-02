from Modules.utils import startMsg, progressBar, signalMsg
from Modules.config import METHOD, API_KEY, API_SEC, PROL
from Modules.api import PrivateApi, PublicApi
from Modules.data import DataHandler
from Modules.order import Trade
from Modules.pair import Token
# from pymexc import futures


# if __name__ == '__main__':
priv = PrivateApi(API_KEY, API_SEC)
dh = DataHandler('data')

while True:
    dh.load()
    api = PublicApi(API_KEY, API_SEC)
    startMsg(api.nSymbol, METHOD)
    c = 1
    for i, symbol in enumerate(api.symbols):
        token = Token(api, dh, symbol)
        token.load()
        step1 = token.checkScales()
        if step1:
            step2 = token.checkShort()
            if step2:
                trdr = Trade(token, priv)
                side = token.side
                ordr = trdr.makeOrder(side)
                msg = signalMsg(token)
                print(msg, "\n")
                print(ordr)

        progressBar(i+1, api.nSymbol, symbol, PROL)

    dh.save()