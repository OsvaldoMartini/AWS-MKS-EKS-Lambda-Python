import os
# from binance import Client
from binance.client import Client
from binance.enums import *
import config
import pandas as pd
import ta
import talib
import numpy as np
import math
import time
import logging
import sys
from datetime import datetime, timezone, timedelta

client = Client(config.API_KEY, config.API_SECRET)


# PROFIT = 1.007  I CLOSED MANUALLY
PROFIT = 1.0055 # LET'S SEE IF THIS GETS PROFITS
LOSSES = 0.995 # LET'S SEE IF DON'T GET TOO MUCH LOSSES
RSI_PERIOD = 14
SIGNAL = 25
# RSI_OVERBOUGHT = 80
# RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
DECIMAL_CALC = 2
QTY_BUY = 20 # USDT
BLOCK_ORDER = False
ACTION_BUY = True
ONLY_RSI = True

COMMISSION = 0.12

ALLOCATION = 0.001
SYMBOL_LEVERAGE = 30
TICKER = 0


# PRECISION_PROFIT_LOSS = 7 # CFXUSDT
PRECISION_PROFIT_LOSS = 1 # BTCUSDT

PROFIT_CALC = 1.005   # BTCUSDT
LOSS_CALC = 0.99813     # BTCUSDT


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
    self.df['Sell'] = np.where((self.df.trigger) &
                     (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80))
                     & (self.df.rsi > 50) & (self.df.macd < 0), 1, 0)  
    
    
    # Calculate MACD using TA-Lib
    self.df['macd_talib'], self.df['signal_talib'], _ = talib.MACD(self.df.Close, fastperiod=12, slowperiod=26, signalperiod=9)
    # Create a signal when MACD crosses above the Signal Line
    self.df['BuyTaLib'] = np.where(self.df['macd_talib'] > self.df['signal_talib'], 1, 0)  
    # Create a signal when MACD crosses below the Signal Line
    self.df['SellTaLib'] = np.where(self.df['macd_talib'] < self.df['signal_talib'], 1, 0)  
    
    # Calculate MACD histogram using ta
    self.df['macd_diff'] = ta.trend.macd_diff(self.df.Close, window_fast=12, window_slow=26, window_sign=9)
    # Define MACD histogram threshold for buy signal
    macd_diff_buy_threshold = 0
    # Create a buy signal when MACD histogram crosses above the threshold
    self.df['BuyTa'] = np.where(self.df['macd_diff'] > macd_diff_buy_threshold, 1, 0)  
    macd_diff_sell_threshold = 0
    # Create a sell signal when MACD histogram crosses below the threshold
    self.df['SellTa'] = np.where(self.df['macd_diff'] < macd_diff_sell_threshold, 1, 0)  


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
  
# Function to calculate PNL and ROI for an open position - SPOT
def calculate_open_position_pnl_roi_spot(current_price, entry_price, quantity):

    entry_price = float(entry_price)
    quantity = float(quantity)

    # Calculate PNL
    pnl = round((current_price - entry_price) * quantity, 4)

    # Calculate ROI
    roi = round((pnl / (entry_price * quantity)) * 100, 4) 

    return pnl, roi  

# Function to calculate PNL and ROI for an open position - SPOT
def calculate_open_position_pnl_roi_future(selling_price_per_unit, purchase_price_per_unit, quantity_bought_sold, action_buy, fees=0):
    # Calculate total cost of purchase
    if not action_buy:
      total_cost = quantity_bought_sold * purchase_price_per_unit
      
      # Calculate total revenue from sale
      total_revenue = quantity_bought_sold * selling_price_per_unit
      
      # Calculate profit or loss
      pnl = total_revenue - total_cost - fees
      
      # Calculate return on investment (ROI)
      roi = (pnl / total_cost) * 100
      
      return pnl, roi    
    if action_buy:
      # Calculate total cost of purchase
      total_cost = quantity_bought_sold * purchase_price_per_unit
      
      # If selling price is provided, calculate PNL
      if selling_price_per_unit is not None:
          total_revenue = quantity_bought_sold * selling_price_per_unit
          pnl = total_revenue - total_cost - fees
      else:
          pnl = None
      
      # Calculate return on investment (ROI)
      if pnl is not None:
          roi = (pnl / total_cost) * 100
      else:
          roi = None
      
      return pnl, roi
    
    
def calculate_roi_with_imr(entry_price, exit_price, quantity, action_buy, imr=1):
    # Calculate the total value at entry and exit
    total_entry_value = entry_price * quantity
    total_exit_value = exit_price * quantity

    # Calculate the profit or loss
    pnl = total_exit_value - total_entry_value

    # Calculate the ROI considering IMR
    roi = (pnl / (total_entry_value / imr)) * 100
    if ACTION_BUY:
      return roi
    if not ACTION_BUY:
      return abs(roi)    
    
def calculate_pnl_futures(entry_price, exit_price, quantity, action_buy):
  if action_buy:
      pnl = (exit_price - entry_price) * quantity
  elif not action_buy:
      pnl = (entry_price - exit_price) * quantity
  else:
      raise ValueError("Invalid side provided")
  return pnl   


# USDT-Margined Contracts
# Initial Margin = Quantity * Entry Price * IMR
# IMR = 1 / leverage
# PnL:
# Long = (Exit Price - Entry Price) * Quantity
# Short = (Entry Price - Exit Price) * Quantity
# ROE% = PnL / Initial Margin = side * (1 - entry price / exit price) / IMR
# Target price:
# Long target price = entry price * ( ROE% / leverage + 1 )
# Short target price = entry price * ( 1 - ROE% / leverage )

def calculate_roi_futures(entry_price, exit_price, quantity, action_buy):
  if action_buy:
    return ((exit_price - entry_price) / entry_price) * 100
  elif not action_buy:
    total_entry_value = entry_price * quantity
    total_exit_value = exit_price * quantity
     # Calculate the fees
    fees = total_exit_value * COMMISSION

    # Calculate the net exit value after fees
    net_exit_value = total_exit_value - fees

    # Calculate ROI
    roi = ((net_exit_value - total_entry_value) / total_entry_value) * 100
    return roi
    # return ((exit_price - entry_price) / entry_price) * 100

# FUTURES
def order_future_create_order(side, symbol, quantity, positionSide, order_type):
    try:
        print("FUTURES sending order  SIDE {} QTD {} ".format( side, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide,  
                                            type=order_type, 
                                            quantity=quantity, 
                                            recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order
  
def order_future_cancel_all_open_order(symbol):
    try:
        # print("Cancel All open Orders / Closing All  {} ".format( symbol))
        # cleardualSidePosition='false', 
        order = client.futures_cancel_all_open_orders(symbol=symbol, 
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            recvWindow = 60000)
        # print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order

def order_future_cancel_REDUCE_only(side, symbol, quantity, positionSide, order_type):
    try:
        print("reduce 100% Cancel Order / Closing Order  {} QTY {} ".format(symbol, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(side='BUY', 
                                            symbol=symbol,
                                            quantity=quantity,
                                            positionSide='BOTH',  
                                            type='MARKET', 
                                            reduceOnly=True, 
                                            recvWindow = 60000)        
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order

def get_entry_price(symbol):
    trades = client.futures_account_trades(symbol=symbol,
                                           recvWindow = 60000)        
    # print("My Trades: {} ".format(trades))
    
    # Sort trades by timestamp in descending order
    sorted_trades = sorted(trades, key=lambda x: x['time'], reverse=True)
    
    # Find the first buy trade (entry trade)
    for trade in sorted_trades:
        if trade['side'] == 'BUY':
            return float(trade['price'])

    # If no buy trade found, return None
    return None
  
def get_current_price_futures(symbol):
    ticker = client.futures_symbol_ticker(symbol=symbol)
    print("TICKER {}".format(ticker))
    return float(ticker['price'])  

def strategy(pair, qty, losses_perc, profit_perc, signal, ACTION_BUY, open_position=False, ):
  df = getminutedata(pair, Client.KLINE_INTERVAL_1MINUTE,'100')
  applytechnicals(df)
  inst = Signals(df, signal)  # Be Aware the Legs Quantity  like 25  THIS PROVE TRADES IT SHOUL TAKE MUCH LESS THAN 25
  inst.decide()
  # print(f'current Close is '+str(current_price) + ' RSI: ' + str(round(df.rsi.iloc[-1], 2)) + ' Buy MACD: ' + str(df.Buy.iloc[-1]))
  # logger.info("current Close is {}  RSI: {}  By MACD: {} ".format(str(current_price), str(round(df.rsi.iloc[-1], 2)), str(df.Buy.iloc[-1])))
  logger.info("MACD SPOT: {} RSI: {} Close {}   Buy MACD {} Sell MACD {}  Buy TaLib {} Sell TaLib {} Buy TA {} Sell TA {}".format (pair, str(round(df.rsi.iloc[-1], 2)), str(df.Close.iloc[-1]), str(df.Buy.iloc[-1]), str(df.Sell.iloc[-1]), str(df.BuyTaLib.iloc[-1]), str(df.SellTaLib.iloc[-1]), str(df.BuyTa.iloc[-1]), str(df.SellTa.iloc[-1])))
  
   # FUTURES CALULATE VOLUME ORDER
  # Params
  # buyVolume = round((QTY_BUY * ALLOCATION) / float(df.Close.iloc[-1]), 1)
  volume = 0.005 #round((QTY_BUY * SYMBOL_LEVERAGE) / float(close), 1)  BTC-USDT "quantity":0.003   
  # volume = round((QTY_BUY * SYMBOL_LEVERAGE) / float(df.Close.iloc[-1]), 3) #  BTC-USDT "quantity":0.003   
  # volume = round((QTY_BUY * SYMBOL_LEVERAGE) / float(close), 1)  # CFX-USDT "quantity":410   
  print("Volume Actual: {}".format(volume))
  # print("BuyVolumelume: {}".format(buyVolume))
    
  # df.Sell.iloc[-1] = 1  
  df.Sell.iloc[-1] = 1  
  if df.Buy.iloc[-1] or df.Sell.iloc[-1]:
    # Estimative
    if df.Buy.iloc[-1]:
      ACTION_BUY = True
      logger.info("Buy !!! Buy !!! Buy !!!") 
      
    if df.Sell.iloc[-1]:
      ACTION_BUY = False
      logger.info("Sell !!! Sell !!! Sell !!!")
    
    if not BLOCK_ORDER:
      
      # SPOT CREATE ORDER
      # order = orderBuy(SIDE_BUY,
      #                 pair,
      #                 qty,
      #                 ORDER_TYPE_MARKET)
      # logger.info(order)
      # entry_price = float(order['fills'][0]['price'])
      # amountQtySpot = float(order['fills'][0]['qty'])
      # open_position = True
      # logger.info("Buy !!! Buy !!! Buy !!!") 
      # logger.info("BOUGHT PRICE:" + str(entry_price))
      open_position = True
      
      # FUTURES CREATE ORDER
      orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
      current_price = get_current_price_futures(TRADE_SYMBOL)

      # Spot
      # close = df.Close.iloc[-1]
      
      #Futures
      close = float(current_price)
      PROFIT_WHEN_BUY = round(float(close) * PROFIT_CALC, PRECISION_PROFIT_LOSS)  
      LOSSES_WHEN_BUY = round(float(close) * LOSS_CALC, PRECISION_PROFIT_LOSS)  
      PROFIT_WHEN_SELL = round(float(close) * LOSS_CALC, PRECISION_PROFIT_LOSS)  
      LOSSES_WHEN_SELL = round(float(close) * PROFIT_CALC, PRECISION_PROFIT_LOSS)  
      print("Close {} REDUCE_PROFIT_WHEN_BUY  value {}".format(str(close), str(PROFIT_WHEN_BUY)))
      print("Close {} REDUCE_LOSSES_WHEN_BUY  value {}".format(str(close), str(LOSSES_WHEN_BUY)))
      print("Close {} REDUCE_PROFIT_WHEN_SELL  value {}".format(str(close), str(PROFIT_WHEN_SELL)))
      print("Close {} REDUCE_LOSSES_WHEN_SELL  value {}".format(str(close), str(LOSSES_WHEN_SELL)))

      if ACTION_BUY:
        orderFuture = order_future_create_order(SIDE_BUY, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
      else:
        orderFuture = order_future_create_order(SIDE_SELL, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
      print("Order FUTURE  {}".format(orderFuture))    
      orderId = orderFuture['orderId']
      clientOrderId = orderFuture['clientOrderId']
      orderStatus = orderFuture['status']
      origQty = orderFuture['origQty']
      print("OrderId  {}  clientOrderId {} status {} origQty {}".format(orderId, clientOrderId, orderStatus, origQty))  
      
      entry_price = get_entry_price(TRADE_SYMBOL)
      if entry_price:
          print("Entry Price:", entry_price)
      else:
          print("No entry price found.")
    
      if ACTION_BUY:
        logger.info("BOUGHT ENTRY PRICE:" + str(entry_price))
        
      if not ACTION_BUY:
        logger.info("SELL ENTRY PRICE:" + str(entry_price))
      
    else:
      entry_price = float(df.Close.iloc[-1])
      amountQtySpot = 5
      open_position = True
      logger.info("SIMULATED Buy !!! Buy !!! Buy !!!") 
      logger.info("SIMULATED BOUGHT PRICE:" + str(entry_price))
       
    
  while open_position:
    time.sleep(0.5)
    df = getminutedata(pair,'1m','2')  # BE AWARE ABOUT THIS '2'  VALUE
    ##  SPOT ->>  df.Close.iloc[-1]
    current_price = get_current_price_futures(TRADE_SYMBOL)
    # Calculate PNL and ROI Spot
    # pnl, roi = calculate_open_position_pnl_roi_spot(df.Close.iloc[-1], entry_price, amountQtySpot)
    
    # Calculate PNL and ROI Futures
    # pnl, roi = calculate_open_position_pnl_roi_future(df.Close.iloc[-1], entry_price, volume, ACTION_BUY)
    
    pnl = calculate_pnl_futures(entry_price, current_price, volume, ACTION_BUY)
    # roi = calculate_roi_futures(entry_price, df.Close.iloc[-1], volume, ACTION_BUY)
    roi = calculate_roi_with_imr(entry_price, current_price, volume, ACTION_BUY, SYMBOL_LEVERAGE)
    ## With SPOT
    # logger.info("MACD-BOT SPOT: {} Buy Price {} Qty {:f} Volume {} Target Profit {}  Stop Loss {} Current Price {} PNL: {} USDT ROI: {}%".format (pair, str(entry_price), amountQtySpot, str(volume), str(round(entry_price * profit_perc, DECIMAL_CALC)), str(round(entry_price * losses_perc, DECIMAL_CALC)), str(df.Close.iloc[-1]), pnl, roi ))
    
    ## Only Futures 
    logger.info("MACD-BOT SPOT: {} Buy Price {} Volume {} Target Profit {}  Stop Loss {} Current Price {} PNL: {} USDT ROI: {}%".format (pair, str(entry_price), str(volume), str(round(entry_price * profit_perc, DECIMAL_CALC)), str(round(entry_price * losses_perc, DECIMAL_CALC)), str(current_price), pnl, roi ))
    # print(f'PNL: {pnl} USDT')
    # print(f'ROI: {roi}%')
    
    if pnl is not None:
      print("Profit/Loss: ${:.2f} USDT".format(pnl))
    if roi is not None:
      print("Return on Investment (ROI): {:.2f}%".format(roi))
    
    # Stop Loss
    if (float(roi) > 0.15) or float(current_price) <= float(round(entry_price * losses_perc, DECIMAL_CALC)) or float(current_price) >= float(round(profit_perc * entry_price, DECIMAL_CALC)):
      soldDesc = "Sell !!! Sell !!! Sell !!! Stop Lossed" if float(current_price) <= entry_price else "Sell !!! Sell !!! Sell !!! PROFIT PROFIT PROFIT PROFIT PROFIT PROFIT"  
      if not BLOCK_ORDER:
        # SPOT CLOSE ORDER
        # orderSpot = orderSell(SIDE_SELL,
        #                 pair,
        #                 int(math.trunc(amountQtySpot)),
        #                 ORDER_TYPE_MARKET,soldDesc)
        # logger.info(orderSpot)
        open_position = False
        
        # FUTURES CLOSE BY REDUCING 100% THE ORDER
        # if ACTION_BUY and (PROFIT_WHEN_BUY <= float(close) or LOSSES_WHEN_BUY >= float(close)): # TakeProfit
        if ACTION_BUY: # TakeProfit
              orderFuture = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
              orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
              # ACTION_BUY = not ACTION_BUY # INVERSE OF TRADING
              in_position = False
        # elif not ACTION_BUY and (PROFIT_WHEN_SELL >= float(close) or LOSSES_WHEN_SELL <= float(close)):  # TakeProfit 
        elif not ACTION_BUY:  # TakeProfit 
            orderFuture = order_future_cancel_REDUCE_only('BUY', TRADE_SYMBOL, volume,  'BOTH', 'MARKET')
            orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
            # ACTION_BUY = not ACTION_BUY # INVERSE OF TRADING
            in_position = False
      
        
      else:
         logger.info("SIMULATED Sell !!! Sell !!! Sell !!!" + soldDesc)
      break

  
# strategy('MANTAUSDT', 1.055, 50) # Runs One Time

  
while True:
  # strategy('MANTAUSDT', 1.055, 50) # Runs One Time
  # strategy('ALTUSDT', 10, 1.055) # Runs One Time
  # strategy('ALTUSDT', 10, 1.005) # Runs One Time
  # strategy('OMUSDT', 10, 1.005) # Runs One Time
  strategy(TRADE_SYMBOL, QTY_BUY, LOSSES, PROFIT, SIGNAL, ACTION_BUY) # Runs One Time
  time.sleep(0.5) 
  
  