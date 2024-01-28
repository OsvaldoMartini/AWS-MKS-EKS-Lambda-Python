import os
# from binance import Client
from binance.client import Client
from binance.enums import *
import config
import pandas as pd
import ta
import numpy as np
import math
import time
import logging
import sys
from datetime import datetime, timezone, timedelta

client = Client(config.API_KEY, config.API_SECRET)


# PROFIT = 1.007  I CLOSED MANUALLY
PROFIT = 1.0055 # LET'S SEE IF THIS GETS PROFITS
RSI_PERIOD = 14
# RSI_OVERBOUGHT = 80
# RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ALTUSDT'
QTY_BUY = 10 # USDT

def aware_utcnow():
    return datetime.now(timezone.utc)
    # return datetime.now(tz=timezone(timedelta(hours=1)))
    
def loggin_setup(filename):
  log_filename = filename.lower() + "_" + str(aware_utcnow().strftime('%d_%m_%Y_%I_%M_%S')) + '.log'
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
loggin_setup("./logs/{}_SPOT_mcda_rsi".format(TRADE_SYMBOL))

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
  df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=RSI_PERIOD, smooth_window=3)
  df['%D'] = df['%K'].rolling(3).mean()
  df['rsi'] = ta.momentum.rsi(df.Close, window=RSI_PERIOD)
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


def orderBuy(side, symbol, quoteOrderQty, order_type):
    try:
        logger.info("sending order  SIDE {} QTY {} ".format( side, quoteOrderQty ))
        order = client.create_order(symbol=symbol, side=side, type=order_type, quoteOrderQty=quoteOrderQty, recvWindow = 60000)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order

def orderSell(side, symbol, quantity, order_type, soldDesc):
    try:
        logger.info("sending order  SIDE {} QTY {} SOLD MOTIVE: {}".format(side, quantity , soldDesc))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
        order = False
        while str(e).find("Account has insufficient balance for requested") >= 0 and not order:
            quantity = math.trunc(quantity - 1) 
            logger.info("Attempt to SELL {}".format(str(quantity)))
            order = orderSell(side, symbol, math.trunc(quantity) , order_type, soldDesc)    
    return order


https://stackoverflow.com/questions/76817422/binance-api-create-futures-order-with-take-profit-limit-and-stop-loss-market

Here's how you can modify your code to achieve the desired functionality:

# Initial BUY MARKET order
buy_limit = client.futures_create_order(
    symbol=coin,
    side='BUY',
    positionSide='LONG',
    type='MARKET',
    quantity=0.001
)

tp = round(45000, 2)  # TakeProfit = 45000
sl = round(50000, 2)  # StopLoss = 50000

# TAKE_PROFIT_LIMIT order (modify this)
take_profit_limit = client.futures_create_order(
    symbol=coin,
    side='SELL',
    positionSide='LONG',
    type='TAKE_PROFIT_LIMIT',
    timeInForce='GTC',  # GTC (Good 'Til Canceled)
    quantity=0.001,
    price=tp,           # Specify the take profit price
    stopPrice=tp,       # Specify the trigger price
    closePosition=True  # or reduceOnly = True
)

# STOP_MARKET order
stop_market = client.futures_create_order(
    symbol=coin,
    side='SELL',
    positionSide='LONG',
    type='STOP_MARKET',
    quantity=0.001,
    stopPrice=sl,       # Specify the trigger price
    closePosition=True
)



def strategy(pair, qty, profit_perc, open_position=False, ):
  df = getminutedata(pair, Client.KLINE_INTERVAL_1MINUTE,'100')
  applytechnicals(df)
  inst = Signals(df, 25)  # Be Aware the Legs Quantity  like 25  THIS PROVE TRADES IT SHOUL TAKE MUCH LESS THAN 25
  inst.decide()
  # print(f'current Close is '+str(df.Close.iloc[-1]) + ' RSI: ' + str(round(df.rsi.iloc[-1], 2)) + ' Buy MACD: ' + str(df.Buy.iloc[-1]))
  # logger.info("current Close is {}  RSI: {}  By MACD: {} ".format(str(df.Close.iloc[-1]), str(round(df.rsi.iloc[-1], 2)), str(df.Buy.iloc[-1])))
  logger.info("MACD-BOT SPOT: {}   RSI: {}   current Close is {}   Buy MACD {} ".format (pair, str(round(df.rsi.iloc[-1], 2)), str(df.Close.iloc[-1]), str(df.Buy.iloc[-1]) ))
  if df.Buy.iloc[-1]:
    order = orderBuy(SIDE_BUY,
                     pair,
                     qty,
                     ORDER_TYPE_MARKET)
    logger.info(order)
    buyprice = float(order['fills'][0]['price'])
    amountQty = float(order['fills'][0]['qty'])
    open_position = True
    logger.info("BOUGHT PRICE:" + str(buyprice)) 
    
  while open_position:
    time.sleep(0.5)
    df = getminutedata(pair,'1m','2')  # BE AWARE ABOUT THIS '2'  VALUE
    logger.info("MACD-BOT SPOT: {} Buy Price {} Qty {} Target Profit {}  Stop Loss {} Current Price {}  ".format (pair, str(buyprice), amountQty, str(buyprice * profit_perc), str(buyprice * 0.995), str(df.Close.iloc[-1]) ))
    # Stop Loss
    if df.Close.iloc[-1] <= buyprice * 0.995 or df.Close.iloc[-1] >= profit_perc * buyprice:
      soldDesc = "Stop Lossed" if float(df.Close.iloc[-1]) <= buyprice else "PROFIT PROFIT PROFIT PROFIT PROFIT PROFIT"  
      orderSell(SIDE_SELL,
                      pair,
                      int(math.trunc(amountQty)),
                      ORDER_TYPE_MARKET,soldDesc)
      logger.info(order)
      break

  
# strategy('MANTAUSDT', 1.055, 50) # Runs One Time

  
while True:
  # strategy('MANTAUSDT', 1.055, 50) # Runs One Time
  # strategy('ALTUSDT', 10, 1.055) # Runs One Time
  # strategy('ALTUSDT', 10, 1.005) # Runs One Time
  # strategy('OMUSDT', 10, 1.005) # Runs One Time
  strategy(TRADE_SYMBOL, QTY_BUY, PROFIT) # Runs One Time
  time.sleep(0.5) 
  
  