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
QTY_BUY = 10 # USDT
QTY_SELL = 1000 # It Forces to Sell 100%
ONLY_BY_WHEN = 41180
ByPass = True
BlockOrder = True

logger = logging.getLogger()
loggin_setup("./logs/bot_FUTURE_{}_mcda_rsi".format(TRADE_SYMBOL))

closes = []
in_position = False
# buyprice = 39570.01 
buyprice = 0
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
        logger.info("Current Volume: {} / Previous Volume {}".format(current_volume, previous_volume))
        if previous_volume > 0 and current_volume > 0: 
            volume_increase = current_volume / previous_volume

            logger.info("Previous Volume: {} / Current Volume: {}".format(previous_volume, current_volume))
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

    
def on_open(kline_ws):
    logger.info('opened connection')

def on_close(kline_ws):
    logger.info('closed connection')

def process_kline_message(kline_ws, message):
    global closes, in_position, buyprice, amountQty, volume, historical_data, previous_volume 
    
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
            print("SIGNAL     BUY: {}     SELL: {}  SIGNAL: {}".format(SINAIS["BUY_HIST"], SINAIS["SELL_HIST"], SINAIS["MSG_1"]), end="\r");
            print(move_down + clear_line, end="")
            print("SIGNAL VOL BUY: {} VOL SELL: {}".format(SINAIS["BUY_VOL_INC"], SINAIS["SELL_VOL_DEC"] ), end="\r")
            print(move_down + clear_line, end="")
            print("SIGNAL IMB BUY: {} IMB SELL: {}  ACTION: {}  {}".format(SINAIS["BUY_VOL_IMB"], SINAIS["SELL_VOL_IMB"], SINAIS["MSG_2"], SINAIS["MSG_3"]), end="\r")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
                    
            
            
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
            if not in_position:
                # print("RSI: {}  current Close is {}  SMA: {}".format (round(last_rsi, 2),  close, last_sma))
                buyPassWhen = "By Pass Active" if ByPass else "BUY WHEN {}".format(ONLY_BY_WHEN)  
                logger.info("current Close is {} BY PASS WHEN {}    RSI: {}".format (close, buyPassWhen, round(last_rsi, 2)))
            if in_position:
                # Stop Loss: 0.998 To near, We Don't get the Chance to have Profits
                logger.info("SPOT: {} Buy Price {} Volume {} Qty {} Target Profit {}  Stop Loss {} Current Price {}  RSI: {}".format (TRADE_SYMBOL, str(buyprice), volume, amountQty, str(buyprice * PROFIT_SELL), str(buyprice * 0.995), close, round(last_rsi, 2)))
                if float(close) <= buyprice * LOSS_SELL or float(close) >= PROFIT_SELL * buyprice:
                    soldDesc = "Stop Lossed" if float(close) <= buyprice else "PROFIT PROFIT PROFIT PROFIT PROFIT PROFIT"  
                    if not BlockOrder:
                        order_succeeded = orderSell(SIDE_SELL, TRADE_SYMBOL.upper(), int(math.trunc(amountQty)), ORDER_TYPE_MARKET, soldDesc)
                        in_position = False        
                        logger.info(order_succeeded)
                    else:
                        logger.info("SIMULATED" + soldDesc)
                        in_position = False                             

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                     logger.info("Overbought! Witing Profit Target {}  to  Sell! Sell! Sell!".format(PROFIT_SELL * buyprice))
                     if float(close) <= buyprice * 0.995 or float(close) >= PROFIT_SELL * buyprice:
                        soldDesc = "Stop Lossed" if float(close) <= buyprice else "PROFIT PROFIT PROFIT PROFIT PROFIT PROFIT"
                        in_position = False
                        if not BlockOrder:  
                            logger.info("Overbought! Sell! Sell! Sell!")
                            order_succeeded = orderSell(SIDE_SELL, TRADE_SYMBOL.upper(), int(math.trunc(amountQty)), ORDER_TYPE_MARKET, soldDesc)
                            logger.info(order_succeeded)
                        else:
                            logger.info("SIMULATED Overbought! Sell! Sell! Sell!")
                            logger.info("SIMULATED {}".format(soldDesc))
                            
                              
                else:
                    logger.info("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    logger.info("It is oversold, but you already own it, nothing to do.")
                else:
                    logger.info("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    if float(close) <= float(ONLY_BY_WHEN) or ByPass:
                        if not BlockOrder:
                            order_succeeded = order(SIDE_BUY, TRADE_SYMBOL.upper(), QTY_BUY, ORDER_TYPE_MARKET)
                            if order_succeeded:
                                logger.info(order)
                                buyprice = float(order_succeeded['fills'][0]['price'])
                                amountQty = float(order_succeeded['fills'][0]['qty'])
                                in_position = True
                                logger.info("BOUGHT PRICE:" + str(buyprice))
                        else:
                           logger.info("SIMULATED BOUGHT PRICE:" + str(close))
                           amountQty = QTY_BUY
                           buyprice = float(close)
                           volume = round(float(close) * float(QTY_BUY), 2)
                           in_position = True
                                
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
        logger.info("Sell signal detected! Order book imbalance SELL: {} Total buy volume: {}".format(imbalance_sell, total_buy_volume))
        SINAIS["SELL_VOL_IMB"] = SINAIS["SELL_VOL_IMB"] + 1
        SINAIS["MSG_3"] = "SELL IMBALANCE"  
         

    # Calculate Signal order book imbalance to buy
    imbalance_buy = total_sell_volume / total_volume if total_volume > 0 else 0

    # Check for buy signal based on order book imbalance and significant buy volume
    if imbalance_buy >= imbalance_threshold and total_sell_volume  >= volume_threshold_depth:
        # print("Buy signal detected! Order book imbalance:", imbalance_buy, "Total buy volume:", total_buy_volume)
        logger.info("Buy signal detected! Order book imbalance BUY: {} Total buy volume: {}".format(imbalance_buy, total_sell_volume))
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