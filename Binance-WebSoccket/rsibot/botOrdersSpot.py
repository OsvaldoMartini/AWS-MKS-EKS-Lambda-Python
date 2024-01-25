import os
# from binance import Client
from binance.client import Client
import config
import pandas as pd
import ta
import numpy as np
import time
import logging
import sys
from datetime import datetime, timezone, timedelta

client = Client(config.API_KEY, config.API_SECRET)

def aware_utcnow():
    return datetime.now(timezone.utc)
    # return datetime.now(tz=timezone(timedelta(hours=1)))
    
def loggin_setup(filename):
  log_filename = filename.lower() + "_" + str(aware_utcnow().strftime('%m_%d_%Y_%I_%M_%S')) + '.log'
  os.makedirs(os.path.dirname(log_filename), exist_ok=True)
  logging.basicConfig(filename=log_filename, format='%(levelname)s | %(asctime)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

  formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

  logging.getLogger().setLevel(logging.INFO)

  # Console Logging
  stdout_handler = logging.StreamHandler(sys.stdout)
  stdout_handler.setLevel(logging.DEBUG)
  stdout_handler.setFormatter(formatter)

  logging.getLogger().addHandler(stdout_handler)

  logging.info('Initialization Logging')
  # logger.error('This is an error message.')

logger = logging.getLogger()
loggin_setup('./logs/ALTUSDT_mcda_rsi')

def getminutedata(symbol, interval, lookback):
  frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + ' min ago UTC'))
  
  frame = frame.iloc[:,:6]
  frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
  frame = frame.set_index('Time')
  frame.index = pd.to_datetime(frame.index, unit='ms')  # Index as Milliseconds
  frame = frame.astype(float)
  return frame

# df = getminutedata('MANTAUSDT', Client.KLINE_INTERVAL_1MINUTE,'100')

def applytechnicals(df):
  df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
  df['%D'] = df['%K'].rolling(3).mean()
  df['rsi'] = ta.momentum.rsi(df.Close, window=14)
  df['macd'] = ta.trend.macd_diff(df.Close)
  df.dropna(inplace=True)
 
# applytechnicals(df) 


class Signals:
  
  def __init__(self, df, lags):
    self.df = df
    self.lags = lags
    
  def gettrigger(self):
    dfx = pd.DataFrame()
    for i in range(self.lags + 1):
      mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
      dfx = dfx._append(mask, ignore_index=True)
    return dfx.sum(axis=0)
  
  def decide(self):
    self.df['trigger'] = np.where(self.gettrigger(), 1, 0)
    self.df['Buy'] = np.where((self.df.trigger) &
                     (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80))
                     & (self.df.rsi > 50) & (self.df.macd > 0), 1, 0)  

# inst = Signals(df, 25)  # Be Aware the Legs Quantity  like 25  THIS PROVE TRADES IT SHOUL TAKE MUCH LESS THAN 25
# inst.decide()

# df[df.Buy == 1]
# print(df)

def strategy(pair, qty, open_position=False):
  df = getminutedata(pair, Client.KLINE_INTERVAL_1MINUTE,'100')
  applytechnicals(df)
  inst = Signals(df, 25)  # Be Aware the Legs Quantity  like 25  THIS PROVE TRADES IT SHOUL TAKE MUCH LESS THAN 25
  inst.decide()
  # print(f'current Close is '+str(df.Close.iloc[-1]) + ' RSI: ' + str(round(df.rsi.iloc[-1], 2)) + ' Buy MACD: ' + str(df.Buy.iloc[-1]))
  logger.info("current Close is {}  RSI: {}    Buy MACD: {} ".format(str(df.Close.iloc[-1]), str(round(df.rsi.iloc[-1], 2)), str(df.Buy.iloc[-1])))
  if df.Buy.iloc[-1]:
    order = client.create_order(symbol=pair,
                                side='BUY',
                                type='MARKET',
                                quantity=qty)
    logger.info(order)
    buyprice = float(order['fills'][0]['price'])
    open_position = True
    
  while open_position:
    time.sleep(0.5)
    df = getminutedata(pair,'1m','2')  # BE AWARE ABOUT THIS '2'  VALUE
    logger.info("current Close {}".format(str(df.Close.iloc[-1])))
    logger.info("current Target {}".format(str(buyprice * 1.005)))
    logger.info("current Stop is {}".format(tr(buyprice * 0.995))) # 0.998 To near, We Don't get the Chance to have Profits
    # Stop Loss
    if df.Close[-1] <= buyprice * 0.995 or df.Close[-1] >= 1.005 * buyprice:
      order = client.create_order(symbol=pair,
                                  side='SELL',
                                  type='MARKET',
                                  quantity=qty,
                                  recvWindow = 60000)
      logger.info(order)
      break

  
# strategy('MANTAUSDT', 50) # Runs One Time

  
while True:
  # strategy('MANTAUSDT', 50) # Runs One Time
  strategy('ALTUSDT', 50) # Runs One Time
  time.sleep(0.5) 
  
  