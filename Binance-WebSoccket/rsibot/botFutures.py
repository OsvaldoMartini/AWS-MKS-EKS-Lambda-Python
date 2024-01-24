import pandas as pd
import time
import requests
from datetime import datetime, timezone
import calendar


# Note that if you are using Python 3.11 or newer, you can replace datetime.timezone.utc with a shorter datetime.UTC.
def aware_utcnow():
    return datetime.now(timezone.utc)
  
def aware_utcfromtimestamp(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc)
  
def naive_utcnow():
    return aware_utcnow().replace(tzinfo=None)

def naive_utcfromtimestamp(timestamp):
    return aware_utcfromtimestamp(timestamp).replace(tzinfo=None)    

print("aware_utcnow:           " + str(aware_utcnow()))
print("aware_utcfromtimestamp: " + str(aware_utcfromtimestamp(0)))
print("naive_utcnow:           " + str(naive_utcnow()))
print("naive_utcfromtimestamp: " + str(naive_utcfromtimestamp(0)))

while True:
  
  symbol='MANTAUSDT'
  timeInterval = 1
  limit = 100
  
  now = aware_utcnow() # datetime.utcnow()
  unixtime = calendar.timegm(now.utctimetuple())
  since = unixtime
  start = str(since-60*60*10)
  
  
  url = 'https://fapi.binance.com/fapi/v1/klines?symbol='+symbol+'&interval='+str(timeInterval)+'m'+'&limit='+str(limit)
  
  data = requests.get(url).json()
  
  D = pd.DataFrame(data)
  D.columns = ['open_time', 'open','high','low','close','volume','close_time','qav','num_trades',
                  'taker_base_vol','taker_quote_vol','is_best_mathc']
  
  period = 14
  df = D
  df['close'] = df['close'].astype(float)
  df2 = df['close'].to_numpy()
  
  df2 = pd.DataFrame(df2, columns = ['close'])
  delta = df2.diff()
  
  up, down = delta.copy() , delta.copy()
  up[up < 0] = 0
  down[down > 0] = 0
  
  _gain = up.ewm(com=(period - 1), min_periods=period).mean()
  _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
  
  RS = _gain / _loss
  
  rsi = 100 - (100 / (1+ RS))
  rsi = rsi['close'].iloc[-1]
  rsi=round(rsi,1)
  
  text='Binance Futures ' + symbol + ' RSI: ' +str(rsi)
  
  print(text)
  
  time.sleep(0.5)
  
  