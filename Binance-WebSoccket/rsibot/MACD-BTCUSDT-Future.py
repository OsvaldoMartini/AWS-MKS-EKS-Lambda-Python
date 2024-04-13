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
RSI_PERIOD = 14
SIGNAL = 25
# RSI_OVERBOUGHT = 80
# RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
DECIMAL_CALC = 2
QTY_BUY = 0.05 # USDT 0.005
BLOCK_ORDER = True
ACTION_BUY = True
ONLY_RSI = True

COMMISSION = 0.12

ALLOCATION = 0.001
SYMBOL_LEVERAGE = 75
TICKER = 0


# PRECISION_PROFIT_LOSS = 7 # CFXUSDT
PRECISION_PROFIT_LOSS = 1 # BTCUSDT

BUY_PROFIT_CALC = 1.005   # BTCUSDT
BUY_LOSS_CALC = 0.99913     # BTCUSDT

SELL_PROFIT_CALC = 1.005   # BTCUSDT
SELL_LOSS_CALC = 0.99913     # BTCUSDT

PROFIT_WHEN_BUY = 0
LOSSES_WHEN_BUY = 0
PROFIT_WHEN_SELL = 0
LOSSES_WHEN_SELL = 0

TOTALS = {}
TOTALS['TOTAL_PROFITS_BUY'] = 0 
TOTALS['TOTAL_LOSSES_BUY']= 0
TOTALS['TOTAL_PROFITS_SELL'] = 0
TOTALS['TOTAL_LOSSES_SELL'] = 0

def acumlate_values(initial, new):
  initial = float(initial) + new
  return  initial

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
loggin_setup("./logs/{}_FUTURE_mcda_rsi".format(TRADE_SYMBOL))

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
# logger.info(df)


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
    
    logger.info("FUTURES PNL {} TOTAL ENTRY {} TOTAL EXIT {} ".format( round(pnl, 2), round(total_entry_value, 1), round(total_exit_value, 1)))

    # Calculate the ROI considering IMR
    roi = (pnl / (total_entry_value / imr)) * 100
    return roi
    
def calculate_pnl_futures(entry_price, exit_price, quantity, action_buy):
  if action_buy:
      pnl = (exit_price - entry_price) * quantity
  elif not action_buy:
      pnl = (entry_price - exit_price) * quantity
  else:
      raise ValueError("Invalid side provided")
  return pnl   

def mine_calculate_roi_with_imr(entry_price, exit_price, quantity, imr=1):
    # Calculate the total value at entry and exit
    # total_entry_value = entry_price * quantity
    # total_exit_value = exit_price * quantity
    
    # logger.info("entry_price {}".format(entry_price)) 
    # logger.info("exit_price {}".format(exit_price)) 
    # logger.info("quantity {}".format(quantity)) 
    # logger.info("imr {}".format(imr)) 
    
    roi = (((exit_price - entry_price) * imr ) / entry_price)

    # logger.info("FUTURES ROI {} TOTAL ENTRY {} TOTAL EXIT {} ".format( round(roi, 2), round(total_entry_value, 1), round(total_exit_value, 1)))

    # Calculate the profit or loss
    # pnl = total_exit_value - total_entry_value

    return roi * 100

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
        logger.info("FUTURES sending order  SIDE {} QTD {} ".format( side, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide,  
                                            type=order_type, 
                                            quantity=quantity, 
                                            recvWindow = 60000)
        logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order
  
def order_future_cancel_all_open_order(symbol):
    try:
        # logger.info("Cancel All open Orders / Closing All  {} ".format( symbol))
        # cleardualSidePosition='false', 
        order = client.futures_cancel_all_open_orders(symbol=symbol, 
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            recvWindow = 60000)
        # logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order

def order_future_cancel_REDUCE_only(side, symbol, quantity, positionSide, order_type):
    try:
        logger.info("reduce 100% Cancel Order / Closing Order  {} QTY {} ".format(symbol, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(side='BUY', 
                                            symbol=symbol,
                                            quantity=quantity,
                                            positionSide='BOTH',  
                                            type='MARKET', 
                                            reduceOnly=True, 
                                            recvWindow = 60000)        
        logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order

def get_entry_price(symbol):
    trades = client.futures_account_trades(symbol=symbol,
                                           recvWindow = 60000)        
    # logger.info("My Trades: {} ".format(trades))
    
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
    logger.info("TICKER {}".format(ticker))
    return float(ticker['price'])  

def strategy(pair, qty, signal, TOTALS, ACTION_BUY, open_position=False, ):
  df = getminutedata(pair, Client.KLINE_INTERVAL_1MINUTE,'100')
  logger.info("DATA FRAME {}".format(df))
  applytechnicals(df)
  inst = Signals(df, signal)  # Be Aware the Legs Quantity  like 25  THIS PROVE TRADES IT SHOUL TAKE MUCH LESS THAN 25
  inst.decide()
  # logger.info(f'current Close is '+str(current_price) + ' RSI: ' + str(round(df.rsi.iloc[-1], 2)) + ' Buy MACD: ' + str(df.Buy.iloc[-1]))
  # logger.info("current Close is {}  RSI: {}  By MACD: {} ".format(str(current_price), str(round(df.rsi.iloc[-1], 2)), str(df.Buy.iloc[-1])))
  logger.info("1st SIGNALS MACD SPOT/FUTURE: {} RSI: {} Close {}   Buy MACD {} Sell MACD {}".format (pair, str(round(df.rsi.iloc[-1], 2)), str(df.Close.iloc[-1]), str(df.Buy.iloc[-1]), str(df.Sell.iloc[-1])))
  logger.info("2st SIGNALS MACD SPOT/FUTURE: {} RSI: {} Close {}   Buy TaLib {} Sell TaLib {}".format (pair, str(round(df.rsi.iloc[-1], 2)), str(df.Close.iloc[-1]), str(df.BuyTaLib.iloc[-1]), str(df.SellTaLib.iloc[-1])))
  logger.info("3st SIGNALS MACD SPOT/FUTURE: {} RSI: {} Close {}   Buy TA {} Sell TA {}".format (pair, str(round(df.rsi.iloc[-1], 2)), str(df.Close.iloc[-1]), str(df.BuyTa.iloc[-1]), str(df.SellTa.iloc[-1])))
  
   # FUTURES CALULATE VOLUME ORDER
  # Params
  # buyVolume = round((QTY_BUY * ALLOCATION) / float(df.Close.iloc[-1]), 1)
  volume = qty #round((QTY_BUY * SYMBOL_LEVERAGE) / float(close), 1)  BTC-USDT "quantity":0.003   
  # volume = round((QTY_BUY * SYMBOL_LEVERAGE) / float(df.Close.iloc[-1]), 3) #  BTC-USDT "quantity":0.003   
  # volume = round((QTY_BUY * SYMBOL_LEVERAGE) / float(close), 1)  # CFX-USDT "quantity":410   
  logger.info("Volume Actual: {}".format(volume))
  # logger.info("BuyVolumelume: {}".format(buyVolume))
    
  # df.Sell.iloc[-1] = 1  
  # df.Buy.iloc[-1] = 1  
  if df.Buy.iloc[-1] or df.Sell.iloc[-1]:
    # Estimative
    if df.Buy.iloc[-1]:
      ACTION_BUY = True
      logger.info("Buy !!! Buy !!! Buy !!!") 
      logger.info("Buy !!! Buy !!! Buy !!!") 
      logger.info("Buy !!! Buy !!! Buy !!!") 
      
    if df.Sell.iloc[-1]:
      ACTION_BUY = False
      logger.info("Sell !!! Sell !!! Sell !!!")
      logger.info("Sell !!! Sell !!! Sell !!!")
      logger.info("Sell !!! Sell !!! Sell !!!")
      
    if not BLOCK_ORDER:
      
      open_position = True
      
      # FUTURES CREATE ORDER
      orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
      future_current_price = get_current_price_futures(TRADE_SYMBOL)

      # Spot
      # close = df.Close.iloc[-1]
      
      #Futures Prices Profit & Loss When Buy
      PROFIT_WHEN_BUY = round(float(future_current_price) * BUY_PROFIT_CALC, PRECISION_PROFIT_LOSS)  
      LOSSES_WHEN_BUY = round(float(future_current_price) * BUY_LOSS_CALC, PRECISION_PROFIT_LOSS)  
      # Futures Prices Profit & Loss When SELl
      PROFIT_WHEN_SELL = round(float(future_current_price) / SELL_PROFIT_CALC, PRECISION_PROFIT_LOSS)  
      LOSSES_WHEN_SELL = round(float(future_current_price) / SELL_LOSS_CALC, PRECISION_PROFIT_LOSS)  

      if ACTION_BUY:
        orderFuture = order_future_create_order(SIDE_BUY, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
      else:
        orderFuture = order_future_create_order(SIDE_SELL, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
        
      logger.info("Order FUTURE  {}".format(orderFuture))    
      orderId = orderFuture['orderId']
      clientOrderId = orderFuture['clientOrderId']
      orderStatus = orderFuture['status']
      origQty = orderFuture['origQty']
      logger.info("OrderId  {}  clientOrderId {} status {} origQty {}".format(orderId, clientOrderId, orderStatus, origQty))  
      
      entry_price = get_entry_price(TRADE_SYMBOL)
      if entry_price:
          logger.info("Entry Price:", entry_price)
      else:
          logger.info("No entry price found.")
    
      if ACTION_BUY:
        logger.info("BOUGHT ENTRY PRICE:" + str(entry_price))
        
      if not ACTION_BUY:
        logger.info("SELL ENTRY PRICE:" + str(entry_price))
      
    else:
      entry_price = float(df.Close.iloc[-1])
      logger.info("SPOT Entry Price {}".format(str(entry_price)))
    
      open_position = True
      
      futures_entry_price = get_current_price_futures(TRADE_SYMBOL)
      logger.info("FUTURE Entry Price {}".format(str(futures_entry_price)))
    
      # entry_price = get_entry_price(TRADE_SYMBOL)
      # if entry_price:
      #     logger.info("Entry Price:", entry_price)
      # else:
      #     logger.info("No entry price found.")
    
      # Spot
      # close = df.Close.iloc[-1]
      
      if ACTION_BUY:
        logger.info("SIMULATED BOUGHT PRICE:" + str(futures_entry_price))
        
      if not ACTION_BUY:
        logger.info("SIMULATED SELL PRICE:" + str(futures_entry_price))
        
      #Futures Prices Profit & Loss When Buy
      PROFIT_WHEN_BUY = round(float(futures_entry_price) * BUY_PROFIT_CALC, PRECISION_PROFIT_LOSS)  
      LOSSES_WHEN_BUY = round(float(futures_entry_price) * BUY_LOSS_CALC, PRECISION_PROFIT_LOSS)  


      # Futures Prices Profit & Loss When SELl
      PROFIT_WHEN_SELL = round(float(futures_entry_price) / SELL_PROFIT_CALC, PRECISION_PROFIT_LOSS)  
      LOSSES_WHEN_SELL = round(float(futures_entry_price) / SELL_LOSS_CALC, PRECISION_PROFIT_LOSS)  


      pnlProfitBuy = calculate_pnl_futures(futures_entry_price, PROFIT_WHEN_BUY, volume, True)
      roiProfitBuy = mine_calculate_roi_with_imr(futures_entry_price, PROFIT_WHEN_BUY, volume, SYMBOL_LEVERAGE)
      pnlLossBuy = calculate_pnl_futures(futures_entry_price, LOSSES_WHEN_BUY, volume, True)
      roiLossBuy = mine_calculate_roi_with_imr(futures_entry_price, LOSSES_WHEN_BUY, volume, SYMBOL_LEVERAGE)
              
      pnlProfitSell = calculate_pnl_futures(futures_entry_price, PROFIT_WHEN_SELL,  volume, False)
      roiProfitSell = mine_calculate_roi_with_imr(PROFIT_WHEN_SELL, futures_entry_price, volume, SYMBOL_LEVERAGE)
      pnlLossSell = calculate_pnl_futures(futures_entry_price, LOSSES_WHEN_SELL, volume, False)
      roiLossSell = mine_calculate_roi_with_imr(LOSSES_WHEN_SELL, futures_entry_price, volume, SYMBOL_LEVERAGE)
      
      logger.info("----------------------------------            CALCULUS  ENTRY PRICE                       ----------------------------------|")
      logger.info("                                                                                                                            |")
      logger.info("FUTURE Volume {} --->  Quantity USD: {}".format(volume, round(futures_entry_price * volume, 2)))
      logger.info("----------------------------------------------------------------------------------------------------------------------------|")
      logger.info("                                                                                                                            |")
      logger.info("BUY  ENTRY_PRICE {} TAKE_PROFIT_WHEN   {} ROI: {}% PNL: {}".format(str(futures_entry_price), str(PROFIT_WHEN_BUY), round(roiProfitBuy, 2), round(pnlProfitBuy, 2)))
      logger.info("BUY  ENTRY_PRICE {} REDUCE_LOSSES_WHEN {} ROI: {}% PNL: {}".format(str(futures_entry_price), str(LOSSES_WHEN_BUY), round(roiLossBuy, 2), round(pnlLossBuy, 2)))
      logger.info("                                                                                                                            |")
      logger.info("SELL ENTRY_PRICE {} TAKE_PROFIT_WHEN   {} ROI: {}% PNL: {}".format(str(futures_entry_price), str(PROFIT_WHEN_SELL), round(roiProfitSell, 2), round(pnlProfitSell, 2)))
      logger.info("SELL ENTRY_PRICE {} REDUCE_LOSSES_WHEN {} ROI: {}% PNL: {}".format(str(futures_entry_price), str(LOSSES_WHEN_SELL), round(roiLossSell, 2), round(pnlLossSell, 2)))
      logger.info("                                                                                                                            |")
      logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
     
      logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
      logger.info("----------------------------------            TOTAL  PROFIT AND LOSS                      ----------------------------------|")
      logger.info("                                                                                                                            |")
      logger.info("PROFITS BUY  {} LOSSES BUY  {}   TOTAL {}".format(round(TOTALS['TOTAL_PROFITS_BUY'], 2), round(TOTALS['TOTAL_LOSSES_BUY'], 2), round(TOTALS['TOTAL_PROFITS_BUY'] - abs(TOTALS['TOTAL_LOSSES_BUY']), 2)))
      logger.info("PROFITS SELL {} LOSSES SELL {}   TOTAL {}".format(round(TOTALS['TOTAL_PROFITS_SELL'], 2), round(TOTALS['TOTAL_LOSSES_SELL'], 2), round(TOTALS['TOTAL_PROFITS_SELL'] - abs(TOTALS['TOTAL_LOSSES_SELL']), 2)))
      logger.info("                                                                                                                            |")
      logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
     
    
  while open_position:
    time.sleep(0.5)
    df = getminutedata(pair,'1m','2')  # BE AWARE ABOUT THIS '2'  VALUE
    ##  SPOT ->>  df.Close.iloc[-1]
    futures_current_price = get_current_price_futures(TRADE_SYMBOL)
    
    if ACTION_BUY:
      pnlProfitBuy = calculate_pnl_futures(futures_current_price, futures_entry_price, volume, True)
      roiProfitBuy = mine_calculate_roi_with_imr(futures_current_price, futures_entry_price, volume, SYMBOL_LEVERAGE)
    
    if not ACTION_BUY:        
      pnlProfitSell = calculate_pnl_futures(futures_entry_price, futures_current_price, volume, False)
      roiProfitSell = mine_calculate_roi_with_imr(futures_current_price, futures_entry_price, volume, SYMBOL_LEVERAGE)
      
    # TOTALS['TOTAL_PROFITS_BUY'] += pnlProfitBuy 
    # TOTALS['TOTAL_LOSSES_BUY'] += pnlProfitBuy
    # TOTALS['TOTAL_PROFITS_SELL'] += pnlProfitSell
    # TOTALS['TOTAL_LOSSES_SELL'] += pnlProfitSell
      
    ## Only Futures 
    if ACTION_BUY:
      logger.info("MACD-BOT FUTURE: {} Buy Entry Price {} Volume {} Target Profit {}  Stop Loss {} Current Price {} PNL: {} USDT ROI: {}%".format (pair, str(futures_entry_price), str(round(volume * futures_entry_price, 2)), str(round(PROFIT_WHEN_BUY, DECIMAL_CALC)), str(round(LOSSES_WHEN_BUY, DECIMAL_CALC)), str(futures_current_price), round(pnlProfitBuy, 2), round(roiProfitBuy, 2)  ))
    
    if not ACTION_BUY:
      logger.info("MACD-BOT FUTURE: {} Sell Entry Price {} Volume {} Target Profit {}  Stop Loss {} Current Price {} PNL: {} USDT ROI: {}%".format (pair, str(futures_entry_price), str(round(volume * futures_entry_price, 2)), str(round(PROFIT_WHEN_SELL, DECIMAL_CALC)), str(round(LOSSES_WHEN_SELL, DECIMAL_CALC)), str(futures_current_price), round(pnlProfitSell, 2), round(roiProfitSell, 2)  ))
    
    # logger.info(f'PNL: {pnl} USDT')
    # logger.info(f'ROI: {roi}%')
    
    if ACTION_BUY and roiProfitBuy is not None:
      logger.info("Return on Investment (ROI): {:.2f}%".format(roiProfitBuy))
    if ACTION_BUY and pnlProfitBuy is not None:
      logger.info("Profit/Loss: ${:.2f} USDT".format(pnlProfitBuy))
    
    if not ACTION_BUY and roiProfitSell is not None:
      logger.info("Return on Investment (ROI): {:.2f}%".format(roiProfitSell))
    if not ACTION_BUY and pnlProfitSell is not None:
      logger.info("Profit/Loss: ${:.2f} USDT".format(pnlProfitSell))
    
    if ACTION_BUY:
      # Stop Losses or Take Profits
      if (float(roiProfitBuy) < float(-0.45)) or (float(roiProfitBuy) > float(2.0)) or float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)):
        # FUTURE
        # soldDesc = "STOP LOSSES CLOSE ORDER!!! STOP LOSSES!!!" if float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)) else "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Current price: {}  Profits At: {} ROI: {}% PNL: {}".format(float(futures_current_price), float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)), round(roiProfitBuy, 2), round(pnlProfitBuy, 2))  
        if (float(roiProfitBuy) < float(-0.45)) or float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)): 
          soldDesc1 = "STOP LOSSES CLOSE ORDER!!! Current price: {}".format(float(futures_current_price))
          soldDesc2 = "STOP LOSSES CLOSE ORDER!!! Losses At: {} ROI: {}% PNL: {}".format(float(futures_current_price), float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)), round(roiProfitBuy, 2), round(pnlProfitBuy, 2)) 
        else:
          soldDesc1 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Current price: {}".format(float(futures_current_price))
          soldDesc2 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Profits At: {} ROI: {}% PNL: {}".format(float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)), round(roiProfitBuy, 2), round(pnlProfitBuy, 2))  
        
        if not BLOCK_ORDER:
          # FUTURES CLOSE BY REDUCING 100% THE ORDER
          orderFuture = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
          orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
          open_position = False
          
          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
          logger.info("                                     TOTAL  PROFIT AND LOSS                                ----------------------------------|")
          logger.info(soldDesc1)
          logger.info(soldDesc2)
          logger.info("                                                                                           ----------------------------------|")
          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
          
          if float(pnlProfitBuy) >= 0:
            TOTALS['TOTAL_PROFITS_BUY'] += pnlProfitBuy
          else:
            TOTALS['TOTAL_LOSSES_BUY'] -= abs(pnlProfitBuy)
        
        else:
          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
          logger.info("SIMULATED                             TOTAL  PROFIT AND LOSS                              ----------------------------------|")
          logger.info(soldDesc1)
          logger.info(soldDesc2)
          logger.info("SIMULATED                                                                                 ----------------------------------|")
          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
          
          if float(pnlProfitBuy) >= 0:
            TOTALS['TOTAL_PROFITS_BUY'] += pnlProfitBuy
          else:
            TOTALS['TOTAL_LOSSES_BUY'] -= abs(pnlProfitBuy)
      
        break
    if not ACTION_BUY:
      # Stop Losses or Take Profits
      if (float(roiProfitSell) < float(-0.45)) or (float(roiProfitSell) > 2.0) or float(futures_current_price) >= float(round(LOSSES_WHEN_SELL, DECIMAL_CALC)) or float(futures_current_price) <= float(round(PROFIT_WHEN_SELL, DECIMAL_CALC)):
        # FUTURE
        if (float(roiProfitSell) < float(-0.45)) or float(futures_current_price) >= float(round(LOSSES_WHEN_SELL, DECIMAL_CALC)):
          soldDesc1 = "STOP LOSSES CLOSE ORDER!!! Current price: {}".format(float(futures_current_price))
          soldDesc2 = "STOP LOSSES CLOSE ORDER!!! Losses At: {} ROI: {}% PNL: {}".format(float(round(PROFIT_WHEN_SELL, DECIMAL_CALC)), round(roiProfitSell, 2), round(pnlProfitSell, 2)) 
        else:
          soldDesc1 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Current price: {}".format(float(futures_current_price))
          soldDesc2 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Profits At: {} ROI: {}% PNL: {}".format(float(round(PROFIT_WHEN_SELL, DECIMAL_CALC)), round(roiProfitSell, 2), round(pnlProfitSell, 2))  
        if not BLOCK_ORDER:
          # FUTURES CLOSE BY REDUCING 100% THE ORDER
          orderFuture = order_future_cancel_REDUCE_only('BUY', TRADE_SYMBOL, volume,  'BOTH', 'MARKET')
          orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
          open_position = False        

          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
          logger.info("                                     TOTAL  PROFIT AND LOSS                                ----------------------------------|")
          logger.info(soldDesc1)
          logger.info(soldDesc2)
          logger.info("                                                                                           ----------------------------------|")
          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    

          if float(pnlProfitSell) >= 0:
            TOTALS['TOTAL_PROFITS_SELL'] += round(pnlProfitSell, 2)
          else:
            TOTALS['TOTAL_LOSSES_SELL'] -= abs(round(pnlProfitSell, 2))

        else:
          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
          logger.info("SIMULATED                             TOTAL  PROFIT AND LOSS                              ----------------------------------|")
          logger.info(soldDesc1)
          logger.info(soldDesc2)
          logger.info("SIMULATED                                                                                 ----------------------------------|")
          logger.info("----------------------------------------------------------------------------------------------------------------------------|")    

          if float(pnlProfitSell) >= 0:
            TOTALS['TOTAL_PROFITS_SELL'] += round(pnlProfitSell, 2)
          else:
            TOTALS['TOTAL_LOSSES_SELL'] -= abs(round(pnlProfitSell, 2))
          
        break
  
# strategy('MANTAUSDT', 1.055, 50) # Runs One Time

  
while True:
  # strategy('MANTAUSDT', 1.055, 50) # Runs One Time
  # strategy('ALTUSDT', 10, 1.055) # Runs One Time
  # strategy('ALTUSDT', 10, 1.005) # Runs One Time
  # strategy('OMUSDT', 10, 1.005) # Runs One Time
  strategy(TRADE_SYMBOL, QTY_BUY, SIGNAL, TOTALS, ACTION_BUY) # Runs One Time
  time.sleep(0.5) 
  
  