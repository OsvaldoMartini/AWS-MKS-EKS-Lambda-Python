import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import numpy as np
import math


RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'btcusdt'
TRADE_QUANTITY = 50
SOCKET_SPOT = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL)


closes = []
in_position = False


client = Client(config.API_KEY, config.API_SECRET) #, tld='us'

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order  SIDE {} QRT {} ".format( side, quantity ))
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity, recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return True

    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    
    
    # info = client.get_symbol_info('BONKUSDT')
    # print(info)
    # print(info['filters'][2]['minQty'])

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
            print("SMA: {}".format(last_sma))

            # print("all rsis calculated so far")
            # np_rsi = numpy.array(rsi)
            # print("Numpy RSIs {}".format(rsi))
        
            last_rsi = rsi[-1]
            print("RSI: {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    # order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL.upper())
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    # order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL.upper())
                    if order_succeeded:
                        in_position = True
                    
                
ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()