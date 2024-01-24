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
TRADE_BUY = 5 # USDT
TRADE_SELL = 1000 # It Forces to Sell 100%

SOCKET_SPOT = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL)

# balance = 17.25099083
# balance = 17.25452794
# balance = 17.557742498

closes = []
in_position = False
# buyprice = 39570.01 
buyprice = 0

client = Client(config.API_KEY, config.API_SECRET) #, tld='us'


def order(side, quoteOrderQty, symbol, order_type):
    try:
        print("sending order  SIDE {} QRT {} ".format( side, quoteOrderQty ))
        order = client.create_order(symbol=symbol, side=side, type=order_type, quoteOrderQty=quoteOrderQty, recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order

    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position, buyprice
    
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
            # print("all rsis calculated so far")
            # np_rsi = numpy.array(rsi)
            # print("Numpy RSIs {}".format(rsi))
        
            last_rsi = rsi[-1]
            # print("RSI: {}                SMA: {}".format(round(last_rsi, 2), last_sma))
            if not in_position:
                # print("RSI: {}  current Close is {}  SMA: {}".format (round(last_rsi, 2),  close, last_sma))
                print("RSI: {}  current Close is {}".format (round(last_rsi, 2),  close))
            if in_position:
                # Stop Loss: 0.998 To near, We Don't get the Chance to have Profits
                print("RSI: {}  current Close is {}  Target Profit {}   Stop Loss {}".format (round(last_rsi, 2),  close, str(buyprice * 1.005), str(buyprice * 0.995)))
                if float(close) <= buyprice * 0.995 or float(close) >= 1.005 * buyprice:
                    order_succeeded = order(SIDE_SELL, TRADE_SELL, TRADE_SYMBOL.upper(), ORDER_TYPE_MARKET)
                    if order_succeeded:
                        print(order_succeeded)
                        in_position = False

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                if float(close) <= buyprice * 0.995 or float(close) >= 1.005 * buyprice:
                        order_succeeded = order(SIDE_SELL, TRADE_SELL, TRADE_SYMBOL.upper(), ORDER_TYPE_MARKET)
                        if order_succeeded:
                            print(order_succeeded)
                            in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_BUY, TRADE_SYMBOL.upper(), ORDER_TYPE_MARKET)
                    if order_succeeded:
                        print(order)
                        buyprice = float(order_succeeded['fills'][0]['price'])
                        in_position = True
                        print("BOUGHT PRICE:" + str(buyprice)) 
                        # while open_position:
                        #     print(f'current Close '+ str(close))
                        #     print(f'current Target '+ str(buyprice * 1.005))
                        #     print(f'current Stop is '+ str(buyprice * 0.995)) # 0.998 To near, We Don't get the Chance to have Profits
                        #     # Stop Loss
                        #     if close <= buyprice * 0.995 or close >= 1.005 * buyprice:
                        #          order_succeeded = order(SIDE_SELL, TRADE_BUY, TRADE_SYMBOL.upper(), ORDER_TYPE_MARKET)
                        #          if order_succeeded:
                        #             print(order_succeeded)
                        #             in_position = False
                        #             break
                
ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()