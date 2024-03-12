import os
import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import numpy as np
import math
import logging
import sys
from datetime import datetime, timezone, timedelta
# import ccxt

# balance = 17.25099083
# balance = 17.25452794
# balance = 17.557742498
# balance = 34.11620543
# balance = 34.07442870
# balance = 33.94533986
# balance = 33.916637855
# balance = 33.87617461
# balance = 33.80694975
# balance = 33.79699856
# balance = 33.52835663
# balance = 33.45275975
# balance = 33.49762823
# balance = 33.65854172
# balance = 33.54358782
# balance = 33.350
# balance = 33.30836479
# balance = 33.26055656
# balance = 33.19435273
# balance = 32.89885495
# balance = 32.77350370
# balance = 32.55632435
# balance = 32.26410725
# balance = 32.48765925
# balance = 35.33248501
# balance = 33.85719541
# balance = 33.504457359
# balance = 33.35608892
# balance = 33.30454215
# balance = 28.28391263
# balance = 27.97146840
# balance = 28.09037416
# balance = 76.58375102
# balance = 78.62466593
# balance = 78.55509714
# balance = 78.55920142
# balance = 78.44214068
# balance = 78.51556829
# balance = 78.10052908
# balance = 60.30221175
# balance = 60.26690514
# balance = 60.15021606
# balance = 60.08925408
# balance = 62.11620258
# balance = 62.11620258
# balance = 61.63380193
# balance = 56.40977667
# balance = 56.90652933
# balance = 56.41419003
# balance = 56.18852165




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

PROFIT_SELL = 1.0006
LOSS_SELL = 0.9995
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 40
TRADE_SYMBOL = 'ALTUSDT'
QTY_BUY = 20 # USDT
QTY_SELL = 1000 # It Forces to Sell 100%
ONLY_BY_WHEN = 0.33455
ByPass = True
BlockOrder = True

logger = logging.getLogger()
loggin_setup("./logs/" + TRADE_SYMBOL)

SOCKET_SPOT = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL.lower())

closes = []
in_position = False
# buyprice = 39570.01 
buyprice = 0
# forceSell = 39800.94000000




client = Client(config.API_KEY, config.API_SECRET) #, tld='us'
# exchange = ccxt.binance({'apiKey': config.API_KEY, 'secret': config.API_SECRET})

# params = {'fromAsset': 'BTCUSDT', 'toAsset': 'USDT', 'fromAmount': 10000, 'recvWindow': 60000}
# response = exchange.sapi_post_convert_getquote(params)
# print("Direct Trade {}".format(response.status))

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

    
def on_open(ws):
    logger.info('opened connection')

def on_close(ws):
    logger.info('closed connection')

def on_message(ws, message):
    global closes, in_position, buyprice, amountQty, volume
    
    # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        # print("candle closed at {}".format(close))
        closes.append(float(close))
        
        if len(closes) > RSI_PERIOD:
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
                                
                                     
                
ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()