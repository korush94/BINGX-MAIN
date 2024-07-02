API_KEY = ""
API_SEC = ""

# Loss Limit
LOSS_LIMIT = 0.10 # Dollars

# Risk2Riward Ration
R2R_RATIO = 3

# scales to check - (True -> Enable , False -> Disable)
SCALES = [
    ['1w' , False] ,
    ['1d' , False] ,
    ['4h' , True] ,
    ['1h', True] ,
    ['15m', True] ,
]

# get symbols [options: api(get from MexcApi) , file(get from file)
METHOD = "file"
FILENAME = "pair.txt"

# count of candles for check
NC = 250

# count of float numbers after dot (3.1234 --(NF=2)-> 3.12)
NF = 8

# SuperTrend Parameters (STP -> period) (STF -> Factor)
STP = 10
STF = 2.5

# last Scale (options-> 1m, 5m)
LS = '1m'

# progressbar length
PROL = 20