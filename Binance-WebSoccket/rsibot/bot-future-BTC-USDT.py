import os
import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np
import math
import logging
import sys
from datetime import datetime, timezone, timedelta
import time
import threading
import signal
# import ccxt

# ANSI escape codes for moving cursor
move_up = '\x1b[1A'  # Move cursor up one line
move_down = '\x1b[1B'  # Move cursor down one line
clear_line = '\x1b[2K'  # Clear the entire line

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
#   stdout_handler = logging.StreamHandler(sys.stdout)
#   stdout_handler.setLevel(logging.DEBUG)
#   stdout_handler.setFormatter(formatter)

#   logging.getLogger().addHandler(stdout_handler)

  logging.info('Initialization Logging')
  # logger.error('This is an error message.')

# Flag to indicate if threads should stop
should_stop = False
PROFIT_SELL = 1.0006
LOSS_SELL = 0.9995
RSI_PERIOD = 14
RSI_OVERBOUGHT = 80
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'

DECIMAL_CALC = 2
# QTY_BUY = 10 # USDT
QTY_BUY = 0.05 # USDT 0.005
QTY_SELL = 1000 # It Forces to Sell 100%
ONLY_BY_WHEN = 41180
ByPass = True
BlockOrder = True

ACTION_BUY = True

SYMBOL_LEVERAGE = 75

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

pnlProfitBuy = 0
roiProfitBuy = 0
pnlLossBuy = 0
roiLossBuy = 0

curr_roiProfitBuy = 0
curr_roiProfitSell = 0
        
pnlProfitSell = 0
roiProfitSell = 0
pnlLossSell = 0
roiLossSell = 0


logger = logging.getLogger()
loggin_setup("./logs/bot_FUTURE_{}_mcda_rsi".format(TRADE_SYMBOL))

closes = []
in_position = False
# futures_entry_price = 39570.01 
futures_entry_price = 0
# forceSell = 39800.94000000

SINAIS = {}
SINAIS["BUY_HIST"] = 0 
SINAIS["SELL_HIST"] = 0 
SINAIS["BUY_VOL_INC"] = 0 
SINAIS["SELL_VOL_DEC"] = 0 
SINAIS["BUY_VOL_IMB"] = 0 
SINAIS["SELL_VOL_IMB"] = 0 
SINAIS["MSG_1"] = "" 
SINAIS["MSG_2"] = "" 
SINAIS["MSG_3"] = "" 

TOTALS = {}
TOTALS['TOTAL_PROFITS_BUY'] = 0 
TOTALS['TOTAL_LOSSES_BUY']= 0
TOTALS['TOTAL_PROFITS_SELL'] = 0
TOTALS['TOTAL_LOSSES_SELL'] = 0


# Initialize DataFrame for keeping track of historical data
historical_data = []
timeframe = '1m'  # adjust timeframe as needed

# Parameters for moving averages
short_window = 20
long_window = 50

# Initialize variables
previous_volume = None

# Parameters to Calculate Buy using Volume
volume_threshold_buy = 1.5  # Threshold for volume increase, e.g., volume doubled

# Parameters to Calculate Sell using Volume
volume_threshold_sell = 0.5  # Threshold for volume decrease, e.g., volume halved


# Calculate Signal Base on Depth
# Parameters
imbalance_threshold = 0.8  # Threshold for order book imbalance, e.g., 80% buy orders
volume_threshold_depth = 100  # Minimum volume for a significant buy order


client = Client(config.API_KEY, config.API_SECRET) #, tld='us'
# exchange = ccxt.binance({'apiKey': config.API_KEY, 'secret': config.API_SECRET})

# params = {'fromAsset': 'BTCUSDT', 'toAsset': 'USDT', 'fromAmount': 10000, 'recvWindow': 60000}
# response = exchange.sapi_post_convert_getquote(params)
# print("Direct Trade {}".format(response.status))


def calculate_by_volume(current_volume, previous_volume):
    if previous_volume is not None:
        # Check for buy signal based on volume increase
        # logger.info("Current Volume: {} / Previous Volume {}".format(current_volume, previous_volume))
        if previous_volume > 0 and current_volume > 0: 
            volume_increase = current_volume / previous_volume

            # logger.info("Previous Volume: {} / Current Volume: {}".format(previous_volume, current_volume))
            volume_decrease = previous_volume / current_volume
            if volume_increase >= volume_threshold_buy:
                SINAIS["BUY_VOL_INC"] = SINAIS["BUY_VOL_INC"]  + 1 
                SINAIS["MSG_2"] = "Volume INCREASED !  Buy signal detected!"
                # print("Volume increased significantly!  Buy signal detected! ")
                # print("Volume increased significantly!  Buy signal detected! ")
                # print("Volume increased significantly!  Buy signal detected! ")
                # print("Volume increased significantly!  Buy signal detected! ")
                
            # Check for sell signal based on volume decrease
            elif volume_decrease >= volume_threshold_sell:
                SINAIS["SELL_VOL_DEC"] = SINAIS["SELL_VOL_DEC"] = 1  
                SINAIS["MSG_2"] = "Volume DECREASED !  Sell signal detected"
                # print("Volume decreased significantly!  Sell signal detected!")
                # print("Volume decreased significantly!  Sell signal detected!")
                # print("Volume decreased significantly!  Sell signal detected!")
                # print("Volume decreased significantly!  Sell signal detected!")
         
    # Update previous volume
    return current_volume

def calculate_signal_by_historical(close):
    historical_data.append(close) # -> current_close
    if len(historical_data) > long_window:
        # Calculate moving averages
        short_ma = pd.Series(historical_data).rolling(window=short_window, min_periods=1).mean().iloc[-1]
        long_ma = pd.Series(historical_data).rolling(window=long_window, min_periods=1).mean().iloc[-1]
        # Check for sell signal
        if short_ma < long_ma:
            SINAIS["SELL_HIST"] = 1 
            SINAIS["BUY_HIST"] = 0
            SINAIS["MSG_1"] = "SELL SIGNAL"  
            # print("Sell signal detected! Sell signal detected!")
        if short_ma > long_ma:
            SINAIS["BUY_HIST"] = 1 
            SINAIS["SELL_HIST"] = 0 
            SINAIS["MSG_1"] = "BUY  SIGNAL"  
            # print("Buy signal detected! Buy signal detected!")
          

def order(side, symbol, quoteOrderQty, order_type):
    try:
        logger.info("sending order  SIDE {} QTY {} ".format( side, quoteOrderQty ))
        order = client.create_order(symbol=symbol, side=side, type=order_type, quoteOrderQty=quoteOrderQty, recvWindow = 60000)
        logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order

def orderSell(side, symbol, quantity, order_type, soldDesc):
    try:
        logger.info("sending order  SIDE {} QTY {} SOLD MOTIVE: {}".format(side, quantity , soldDesc))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
        logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
        order = False
        while str(e).find("Account has insufficient balance for requested") >= 0 and not order:
            quantity = math.trunc(quantity - 1) 
            logger.info("Attempt to SELL {}".format(str(quantity)))
            order = orderSell(side, symbol, math.trunc(quantity) , order_type, soldDesc)    
    return order

def get_current_price_futures(symbol):
    ticker = client.futures_symbol_ticker(symbol=symbol)
    # date = datetime(ticker['time'])
    # ticker['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ticker['time']))
    # logger.info("TICKER {}".format(ticker))
    return ticker


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

def profit_calculus(action_buy, entry_price, volume):
    if action_buy:
        logger.info("SIMULATED BOUGHT PRICE: {:.2f}".format(entry_price))

    if not action_buy:
        logger.info("SIMULATED SELL   PRICE: {:.2f}".format(entry_price))

    #Futures Prices Profit & Loss When Buy
    PROFIT_WHEN_BUY = round(float(entry_price) * float(BUY_PROFIT_CALC), PRECISION_PROFIT_LOSS)  
    LOSSES_WHEN_BUY = round(float(entry_price) * float(BUY_LOSS_CALC), PRECISION_PROFIT_LOSS)  


    # Futures Prices Profit & Loss When SELl
    PROFIT_WHEN_SELL = round(float(entry_price) / float(SELL_PROFIT_CALC), PRECISION_PROFIT_LOSS)  
    LOSSES_WHEN_SELL = round(float(entry_price) / float(SELL_LOSS_CALC), PRECISION_PROFIT_LOSS)  


    pnlProfitBuy = calculate_pnl_futures(entry_price, PROFIT_WHEN_BUY, volume, True)
    roiProfitBuy = mine_calculate_roi_with_imr(entry_price, PROFIT_WHEN_BUY, volume, SYMBOL_LEVERAGE)
    pnlLossBuy = calculate_pnl_futures(entry_price, LOSSES_WHEN_BUY, volume, True)
    roiLossBuy = mine_calculate_roi_with_imr(entry_price, LOSSES_WHEN_BUY, volume, SYMBOL_LEVERAGE)
            
    pnlProfitSell = calculate_pnl_futures(entry_price, PROFIT_WHEN_SELL,  volume, False)
    roiProfitSell = mine_calculate_roi_with_imr(PROFIT_WHEN_SELL, entry_price, volume, SYMBOL_LEVERAGE)
    pnlLossSell = calculate_pnl_futures(entry_price, LOSSES_WHEN_SELL, volume, False)
    roiLossSell = mine_calculate_roi_with_imr(LOSSES_WHEN_SELL, entry_price, volume, SYMBOL_LEVERAGE)

    logger.info("----------------------------------            CALCULUS  ENTRY PRICE                       ----------------------------------|")
    logger.info("                                                                                                                            |")
    logger.info("FUTURE Volume {} --->  Quantity USD: {}".format(volume, round(entry_price * volume, 2)))
    logger.info("----------------------------------------------------------------------------------------------------------------------------|")
    logger.info("                                                                                                                            |")
    logger.info("BUY  ENTRY_PRICE {:.2f} TAKE_PROFIT_WHEN   {:.2f} ROI: {}% PNL: {}".format(entry_price, PROFIT_WHEN_BUY, round(roiProfitBuy, 2), round(pnlProfitBuy, 2)))
    logger.info("BUY  ENTRY_PRICE {:.2f} REDUCE_LOSSES_WHEN {:.2f} ROI: {}% PNL: {}".format(entry_price, LOSSES_WHEN_BUY, round(roiLossBuy, 2), round(pnlLossBuy, 2)))
    logger.info("                                                                                                                            |")
    logger.info("SELL ENTRY_PRICE {:.2f} TAKE_PROFIT_WHEN   {:.2f} ROI: {}% PNL: {}".format(entry_price, PROFIT_WHEN_SELL, round(roiProfitSell, 2), round(pnlProfitSell, 2)))
    logger.info("SELL ENTRY_PRICE {:.2f} REDUCE_LOSSES_WHEN {:.2f} ROI: {}% PNL: {}".format(entry_price, LOSSES_WHEN_SELL, round(roiLossSell, 2), round(pnlLossSell, 2)))
    logger.info("                                                                                                                            |")
    logger.info("----------------------------------------------------------------------------------------------------------------------------|")    

    logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
    logger.info("----------------------------------            TOTAL  PROFIT AND LOSS                      ----------------------------------|")
    logger.info("                                                                                                                            |")
    logger.info("PROFITS BUY  {:.2f} LOSSES BUY  {:.2f}   TOTAL {:.2f}".format(round(TOTALS['TOTAL_PROFITS_BUY'], 2), TOTALS['TOTAL_LOSSES_BUY'], TOTALS['TOTAL_PROFITS_BUY'] - abs(TOTALS['TOTAL_LOSSES_BUY'])))
    logger.info("PROFITS SELL {:.2f} LOSSES SELL {:.2f}   TOTAL {:.2f}".format(round(TOTALS['TOTAL_PROFITS_SELL'], 2),TOTALS['TOTAL_LOSSES_SELL'], TOTALS['TOTAL_PROFITS_SELL'] - abs(TOTALS['TOTAL_LOSSES_SELL'])))
    logger.info("                                                                                                                            |")
    logger.info("----------------------------------------------------------------------------------------------------------------------------|")   
         

def on_open(kline_ws):
    logger.info('opened connection')

def on_close(kline_ws):
    logger.info('closed connection')

def process_kline_message(kline_ws, message):
    global closes, in_position, curr_roiProfitBuy, futures_entry_price, amountQty, volume, historical_data, previous_volume 
    
    # df = pd.DataFrame(message, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # df.set_index('timestamp', inplace=True)
    # df['close'] = pd.to_numeric(df['close'])
    # print(df)
    
    # print(message)
    
    # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
        
    current_volume = float(candle['v'])
    
    if is_candle_closed:
  
  
        # Initialize MACD
        # if init_MACD: 
        #   macd = MACD(close=binance.fetch_ohlcv(symbol, timeframe)[-100:], window_fast=12, window_slow=26, window_sign=9)
        #   init_MACD = False

  
  
        # print("candle closed at {}".format(close))
        closes.append(float(close))
        
        if len(closes) > RSI_PERIOD:
            # Calculates Buy or Sell Based on Volume
            previous_volume = calculate_by_volume(current_volume, previous_volume)

            # Calculate Signal Base on Historical close
            calculate_signal_by_historical(close)
    
            np_closes = numpy.array(closes)
            np.set_printoptions(suppress = True)
            # print("Numpy tt: {} Closes {}".format(len(np_closes), np_closes))
        
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            sma = talib.SMA(np_closes, RSI_PERIOD)
            last_sma = sma[-1]
            # print("all rsis calculated so far")
            # np_rsi = numpy.array(rsi)
            # print("Numpy RSIs {}".format(rsi))
        
            last_rsi = rsi[-1]
            # print("RSI: {}                SMA: {}".format(round(last_rsi, 2), last_sma))
            
            # SPOT Entry Price
            spot_current_price = float(close)
            # logger.info("SPOT   Entry Price {:.2f}".format(float(spot_current_price)))

            # FUTURE Entry
            ticker_future = get_current_price_futures(TRADE_SYMBOL)
            # logger.info("TICKER {}".format(ticker_future))
            futures_current_price = float(ticker_future['price'])
            # logger.info("FUTURE Entry Price {:.2f}".format(float(futures_current_price)))

            line1  = "SIGNAL     BUY: {}     SELL: {}  SIGNAL: {}".format(SINAIS["BUY_HIST"], SINAIS["SELL_HIST"], SINAIS["MSG_1"])
            line2  = "SIGNAL VOL BUY: {} VOL SELL: {}".format(SINAIS["BUY_VOL_INC"], SINAIS["SELL_VOL_DEC"] )
            line3  = "SIGNAL IMB BUY: {} IMB SELL: {}  ACTION: {}  {}".format(SINAIS["BUY_VOL_IMB"], SINAIS["SELL_VOL_IMB"], SINAIS["MSG_2"], SINAIS["MSG_3"])
            line4  = "SMA : {:.2f}     RSI: {:.2f}".format(float(last_sma), float(last_rsi))
            line5  = "SPOT   Current Price {:.2f}".format(float(spot_current_price))
            line6  = "FUTURE Current Price {:.2f}".format(float(futures_current_price))
            line7  = "Return on Investment (ROI): {:.2f}%".format(float(curr_roiProfitBuy))
            lines = line1 +"\n" + line2 +"\n" + line3 +"\n" + line4 +"\n" + line5 +"\n" + line6 +"\n" + line7
            print(lines)
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            


            if not in_position:
                # print("RSI: {}  current Close is {}  SMA: {}".format (round(last_rsi, 2),  close, last_sma))
                buyPassWhen = "By Pass Active" if ByPass else "BUY WHEN {}".format(ONLY_BY_WHEN)  
                logger.info("SPOT   Current Close is {:.2f}  {}  RSI: {:.2f}".format (float(spot_current_price), buyPassWhen, float(last_rsi)))
                logger.info("FUTURE Current Close is {:.2f}  {}  RSI: {:.2f}".format (float(futures_current_price), buyPassWhen, float(last_rsi)))
            if in_position:
                # Stop Loss: 0.998 To near, We Don't get the Chance to have Profits
                # logger.info("SPOT:   {} Buy Price {:.2f} Volume {} Qty {} Target Profit {:.2f}  Stop Loss {:.2f} Current Price {:.2f}  RSI: {:.2f}".format (TRADE_SYMBOL, float(futures_entry_price), volume, amountQty, float(futures_entry_price * PROFIT_SELL), float(spot_entry_price * 0.995), float(spot_current_price), float(last_rsi)))
                if ACTION_BUY:
                    curr_pnlProfitBuy = calculate_pnl_futures(futures_current_price, futures_entry_price, volume, True)
                    curr_roiProfitBuy = mine_calculate_roi_with_imr(futures_current_price, futures_entry_price, volume, SYMBOL_LEVERAGE)
                    
                if not ACTION_BUY:        
                    curr_pnlProfitSell = calculate_pnl_futures(futures_entry_price, futures_current_price, volume, False)
                    curr_roiProfitSell = mine_calculate_roi_with_imr(futures_current_price, futures_entry_price, volume, SYMBOL_LEVERAGE)
                    
                # if ACTION_BUY and curr_roiProfitBuy is not None and curr_roiProfitBuy > 0:
                #     print(move_down + clear_line, end="")
                #     print("Return on Investment (ROI): {:.2f}%".format(curr_roiProfitBuy), end="\r")
                # if ACTION_BUY and curr_pnlProfitBuy is not None:
                #     print(move_down + clear_line, end="")
                #     print("Profit/Loss: ${:.2f} USDT".format(curr_pnlProfitBuy), end="\r")
                
                # if not ACTION_BUY and curr_roiProfitSell is not None and curr_roiProfitSell > 0:
                #     print(move_down + clear_line, end="")
                #     print("Return on Investment (ROI): {:.2f}%".format(curr_roiProfitSell), end="\r")
                # if not ACTION_BUY and curr_pnlProfitSell is not None:
                #     print(move_down + clear_line, end="")
                #     print("Profit/Loss: ${:.2f} USDT".format(curr_pnlProfitSell), end="\r")
                    
                
                
                ## Only Futures 
                # if ACTION_BUY:
                #     logger.info("MACD-BOT FUTURE: {:.2f} Buy Entry Price {:.2f} Volume {:.2f} Target Profit {:.2f}  Stop Loss {:.2f} Current Price {:.2f} PNL: {:.2f} USDT ROI: {:.2f}%".format (TRADE_SYMBOL, futures_entry_price, volume * futures_entry_price, round(PROFIT_WHEN_BUY, DECIMAL_CALC), round(LOSSES_WHEN_BUY, DECIMAL_CALC), futures_current_price, pnlProfitBuy, roiProfitBuy))
                # if not ACTION_BUY:
                #     logger.info("MACD-BOT FUTURE: {:.2f} Sell Entry Price {:.2f} Volume {:.2f} Target Profit {:.2f}  Stop Loss {:.2f} Current Price {:.2f} PNL: {:.2f} USDT ROI: {:.2f}%".format (TRADE_SYMBOL, futures_entry_price, volume * futures_entry_price, round(PROFIT_WHEN_SELL, DECIMAL_CALC), round(LOSSES_WHEN_SELL, DECIMAL_CALC), futures_current_price, pnlProfitSell, roiProfitSell ))
                    
                # logger.info(f'PNL: {pnl} USDT')
                # logger.info(f'ROI: {roi}%')
                
                # if ACTION_BUY and roiProfitBuy is not None:
                #     logger.info("Return on Investment (ROI): {:.2f}%".format(float(roiProfitBuy)))
                # if ACTION_BUY and pnlProfitBuy is not None:
                #     logger.info("Profit/Loss: ${:.2f} USDT".format(float(pnlProfitBuy)))
                
                # if not ACTION_BUY and roiProfitSell is not None:
                #     logger.info("Return on Investment (ROI): {:.2f}%".format(float(roiProfitSell)))
                # if not ACTION_BUY and pnlProfitSell is not None:
                #     logger.info("Profit/Loss: ${:.2f} USDT".format(float(pnlProfitSell)))                
                
                if ACTION_BUY:
                   # Stop Losses or Take Profits
                    if (float(curr_roiProfitBuy) < float(-0.45)) or (float(curr_roiProfitBuy) > float(2.0)) or float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)):
                        if (float(curr_roiProfitBuy) < float(-0.45)) or float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)):
                          soldDesc = "FUTURE Stop Losses"
                        #   soldDesc1 = "STOP LOSSES CLOSE ORDER!!! Current price: {:.2f}".format(futures_current_price)
                        #   soldDesc2 = "STOP LOSSES CLOSE ORDER!!! Losses At: {:.2f} ROI: {:.2f}% PNL: {:.2f}".format(round(PROFIT_WHEN_BUY, DECIMAL_CALC), roiProfitBuy, pnlProfitBuy) 
                        if (float(curr_roiProfitBuy) > float(2.0)) or float(futures_current_price) >= float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)):
                            soldDesc = "FUTURE PROFIT PROFIT PROFIT PROFIT PROFIT PROFIT"  
                            # soldDesc1 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Current price: {:.2f}".format(futures_current_price)
                            # soldDesc2 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Profits At: {:.2f} ROI: {:.2f}% PNL: {:.2f}".format(round(PROFIT_WHEN_BUY, DECIMAL_CALC), roiProfitBuy, pnlProfitBuy)  
                    
                        # FUTURE
                        # soldDesc = "STOP LOSSES CLOSE ORDER!!! STOP LOSSES!!!" if float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)) else "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Current price: {}  Profits At: {} ROI: {}% PNL: {}".format(float(futures_current_price), float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)), round(roiProfitBuy, 2), round(pnlProfitBuy, 2))  
                        # if (float(roiProfitBuy) < float(-0.45)) or float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)): 
                        #     soldDesc1 = "STOP LOSSES CLOSE ORDER!!! Current price: {:.2f}".format(futures_current_price)
                        #     soldDesc2 = "STOP LOSSES CLOSE ORDER!!! Losses At: {:.2f} ROI: {:.2f}% PNL: {:.2f}".format(round(PROFIT_WHEN_BUY, DECIMAL_CALC), roiProfitBuy, pnlProfitBuy) 
                        # else:
                        #     soldDesc1 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Current price: {:.2f}".format(futures_current_price)
                        #     soldDesc2 = "PROFITS!!! PROFITS!!! CLOSE ORDER!!! Profits At: {:.2f} ROI: {:.2f}% PNL: {:.2f}".format(round(PROFIT_WHEN_BUY, DECIMAL_CALC), roiProfitBuy, pnlProfitBuy)  
                    
                   
                        # logger.info("FUTURE: {} Buy Price {:.2f} Volume {} Qty {} Target Profit {:.2f}  Stop Loss {:.2f} Current Price {:.2f}  RSI: {:.2f}".format (TRADE_SYMBOL, float(futures_entry_price), volume, amountQty, float(futures_entry_price * PROFIT_SELL), float(futures_entry_price * 0.995), float(futures_current_price), float(last_rsi)))
                        # if float(futures_current_price) <= futures_entry_price * LOSS_SELL or float(futures_current_price) >= PROFIT_SELL * futures_entry_price:
                            #if (float(roiProfitBuy) < float(-0.45)) or (float(roiProfitBuy) > float(2.0)) or float(futures_current_price) <= float(round(LOSSES_WHEN_BUY, DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFIT_WHEN_BUY, DECIMAL_CALC)):
                        # soldDesc = "FUTURE Stop Losses" if float(futures_current_price) < futures_entry_price else "SPOT PROFIT PROFIT PROFIT PROFIT PROFIT PROFIT"  
                        if not BlockOrder:
                            order_succeeded = orderSell(SIDE_SELL, TRADE_SYMBOL.upper(), int(math.trunc(amountQty)), ORDER_TYPE_MARKET, soldDesc)
                            in_position = False        
                            logger.info(order_succeeded)
                        else:
                            logger.info("SIMULATED {}".format(soldDesc))
                            logger.info("SPOT   Current Price {:.2f}".format(float(spot_current_price)))
                            logger.info("FUTURE Current Price {:.2f}".format(float(futures_current_price)))
                            in_position = False           
                            
                            logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
                            logger.info("SIMULATED                             TOTAL  PROFIT AND LOSS                              ----------------------------------|")
                            # logger.info(soldDesc1)
                            # logger.info(soldDesc2)
                            logger.info("SIMULATED                                                                                 ----------------------------------|")
                            logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
                            
                            if float(curr_pnlProfitBuy) >= 0:
                                TOTALS['TOTAL_PROFITS_BUY'] += curr_pnlProfitBuy
                            else:
                                TOTALS['TOTAL_LOSSES_BUY'] -= abs(curr_pnlProfitBuy)                  

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                     logger.info("Overbought! Waiting Profit Target {}  to  Sell! Sell! Sell!".format(PROFIT_SELL * futures_entry_price))
                    
                    
                     if float(futures_current_price) <= futures_entry_price * 0.995 or float(futures_current_price) >= PROFIT_SELL * futures_entry_price:
                        soldDesc = "SPOT Stop Losses" if float(futures_current_price) <= futures_entry_price else "SPOT PROFIT PROFIT PROFIT PROFIT PROFIT PROFIT"
                        in_position = False
                        if not BlockOrder:  
                            logger.info("Overbought! Sell! Sell! Sell!")
                            order_succeeded = orderSell(SIDE_SELL, TRADE_SYMBOL.upper(), int(math.trunc(amountQty)), ORDER_TYPE_MARKET, soldDesc)
                            logger.info(order_succeeded)
                        else:
                            logger.info("SIMULATED Overbought! Sell! Sell! Sell!")
                            logger.info("SIMULATED SELL {}".format(soldDesc))
                            
                            if float(curr_pnlProfitBuy) >= 0:
                                TOTALS['TOTAL_PROFITS_BUY'] += curr_pnlProfitBuy
                            else:
                                TOTALS['TOTAL_LOSSES_BUY'] -= abs(curr_pnlProfitBuy)
                            
                              
                else:
                    logger.info("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    logger.info("It is oversold, but you already own it, nothing to do.")
                else:
                    
                    logger.info("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    if float(futures_current_price) <= float(ONLY_BY_WHEN) or ByPass:
                        if not BlockOrder:
                            order_succeeded = order(SIDE_BUY, TRADE_SYMBOL.upper(), QTY_BUY, ORDER_TYPE_MARKET)
                            if order_succeeded:
                                logger.info(order)
                                futures_entry_price = float(order_succeeded['fills'][0]['price'])
                                amountQty = float(order_succeeded['fills'][0]['qty'])
                                in_position = True
                                logger.info("BOUGHT PRICE: {:.2f}".format(float(futures_entry_price)))
                        else:
                           logger.info("SIMULATED SPOT    BOUGHT PRICE: {:.2f}".format(float(spot_current_price)))
                           logger.info("SIMULATED FUTURES BOUGHT PRICE: {:.2f}".format(float(futures_current_price)))
                           amountQty = QTY_BUY
                           futures_entry_price = float(futures_current_price)
                           # volume = round(float(futures_current_price) * float(QTY_BUY), 2)
                           volume = amountQty
                           in_position = True
                           profit_calculus(ACTION_BUY, float(futures_entry_price), float(volume))
                                
# Function to process Depth WebSocket messages
def process_depth_message(depth_ws, message):
    
     # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    bids = json_message['b']
    asks = json_message['a']
    
    # Calculate total volume of buy and sell orders
    total_buy_volume = sum(float(bid[1]) for bid in bids)
    total_sell_volume = sum(float(ask[1]) for ask in asks)
    # logger.info(message)
    # for bid in bids:
    #     price, volume = float(bid[0]), float(bid[1])
    #     buy_volume += volume
    # for ask in asks:
    #     price, volume = float(ask[0]), float(ask[1])
    #     sell_volume += volume

    # Calculate Signal order book imbalance to sell
    total_volume = total_buy_volume + total_sell_volume
    imbalance_sell = total_buy_volume / total_volume if total_volume > 0 else 0

    # Check for sell signal based on order book imbalance and significant buy volume
    if imbalance_sell >= imbalance_threshold and total_buy_volume >= volume_threshold_depth:
        # print("Sell signal detected! Order book imbalance:", imbalance_sell, "Total buy volume:", total_buy_volume)
        logger.info("Depth Thread: Sell signal detected! Order book imbalance SELL: {:.2f} Total buy volume: {:.2f}".format(imbalance_sell, total_buy_volume))
        SINAIS["SELL_VOL_IMB"] = SINAIS["SELL_VOL_IMB"] + 1
        SINAIS["MSG_3"] = "SELL IMBALANCE"  
         

    # Calculate Signal order book imbalance to buy
    imbalance_buy = total_sell_volume / total_volume if total_volume > 0 else 0

    # Check for buy signal based on order book imbalance and significant buy volume
    if imbalance_buy >= imbalance_threshold and total_sell_volume  >= volume_threshold_depth:
        # print("Buy signal detected! Order book imbalance:", imbalance_buy, "Total buy volume:", total_buy_volume)
        logger.info("Depth Thread: Buy  signal detected! Order book imbalance BUY: {:.2f} Total buy volume: {:.2f}".format(imbalance_buy, total_sell_volume))
        SINAIS["BUY_VOL_IMB"] = SINAIS["BUY_VOL_IMB"] + 1 
        SINAIS["MSG_3"] = "BUY IMBALANCE"  
            
        

# Start WebSocket for Kline data
SOCKET_SPOT_KLINE = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL.lower())
# Start WebSocket for Depth data
SOCKET_SPOT_DEPTH = "wss://stream.binance.com:9443/ws/{}@depth".format(TRADE_SYMBOL.lower())
              
              

# Start WebSocket for Kline data
def run_kline_ws():
    global should_stop
    kline_ws = websocket.WebSocketApp(SOCKET_SPOT_KLINE, on_open=on_open, on_close=on_close, on_message=process_kline_message)
    kline_ws.run_forever()

# Start WebSocket for Depth data
def run_depth_ws():
    global should_stop
    depth_ws = websocket.WebSocketApp(SOCKET_SPOT_DEPTH, on_open=on_open, on_close=on_close, on_message=process_depth_message)
    depth_ws.run_forever()

# Create threads for each WebSocket connection
kline_thread = threading.Thread(target=run_kline_ws)
depth_thread = threading.Thread(target=run_depth_ws)

             
# Function to stop all threads
def stop_all_threads():
    global should_stop
    should_stop = True              

# Stop all threads
# Function to handle Ctrl+C
def signal_handler(signum, frame):
    print("Ctrl+C pressed, stopping threads...")
    stop_all_threads()
    sys.exit(0)
 
# Register signal handler for Ctrl+C
# Assign the new handler
signal.signal(signal.SIGINT, signal_handler)

# Start threads
kline_thread.start()
depth_thread.start()


# Wait for threads to finish
kline_thread.join()
depth_thread.join()              

              
# ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
# ws.run_forever()