from datetime import datetime, timezone, timedelta
from Modules.config import NC

def getParams(scale):
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
        # return interval, delta, crange
        return scale, delta, crange

def signalMsg(token):
        msg = "-"*2 + token.symbol + "-"*5 + str(token.now).split('.')[0] + "-"*35
        for key in token.klast.keys():
            c = token.klast[key].close
            t = token.klast[key].time
            e = token.klast[key].endt
            s = token.slast[key]
            msg += f"\n- {key}({t} - {e}) :    Close: {c}  -  SuperTrend: {s}"
        msg += "\n" + "!"*10 + f" [* {token.sig} *] " + "!"*10
        return msg

def progressBar(current, total, symbol, PROL):
    fraction = current / total
    arrow = int(fraction * PROL - 1) * '-' + '>'
    padding = int(PROL - len(arrow)) * ' '
    ending = '\n' if current == total else '\r'
    print(
          f' Progress: [{arrow}{padding}] {int(fraction*100)}% ({current}/{total}){" "*(18-len(symbol))}"{symbol}"',
          end=ending
    )

def BotMsg():
    now = datetime.now(tz=timezone.utc)
    now = str(now).split(".")[0]
    print("\n", "*"*10, "Bot Started", now, timezone.utc, "*"*50)

def startMsg(n, method):
    startMsg = f" - There is {n} Futures pairs recieved from {method} - "
    print(startMsg, "\n")