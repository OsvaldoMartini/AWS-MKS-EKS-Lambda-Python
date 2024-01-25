import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import numpy as np
import math
import ccxt


RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ALTUSDT'
QTY_BUY = 10 # USDT
QTY_SELL = 1000 # It Forces to Sell 100%

SOCKET_SPOT = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL.lower())

# balance = 17.25099083
# balance = 17.25452794
# balance = 17.557742498


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
        print("sending order  SIDE {} QRT {} ".format( side, quoteOrderQty ))
        order = client.create_order(symbol=symbol, side=side, type=order_type, quoteOrderQty=quoteOrderQty, recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order

def orderSell(side, symbol, quantity, order_type, attept, factor):
    try:
        print("sending order  SIDE {} QRT {} --- Attempt {}".format(side, quantity, attept ))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        while str(e).find("Account has insufficient balance for requested") >= 0:
            attept = attept + 1
            if attept >= 9:
                factor = factor * 10
                attept = 0
                 
            quantity = round(quantity - factor, 5) 
            print("Attempt to SELL {}".format(attept, str(quantity)))
            order = orderSell(side, symbol, round(quantity, 5) , order_type, attept, factor)    
    return order

def orderSellQty(side, symbol, quantity, order_type):
    try:
        print("sending order  SIDE {} QRT {} ".format( side, quantity ))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order

amountQty = 18
# order = order(SIDE_BUY, TRADE_SYMBOL, QTY_BUY, ORDER_TYPE_MARKET)
orderSell(SIDE_SELL, TRADE_SYMBOL, int(round(amountQty, 0)), ORDER_TYPE_MARKET, 0, 0.001)
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position, buyprice, amountQty
    
    # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    print(close)        

    # stopPrice = close * 0.995
    # price = close * 1.004
    # amountQty = 0.00023
    # order = order(SIDE_BUY, TRADE_SYMBOL, amountQty, ORDER_TYPE_MARKET)
    # order = orderSell(SIDE_SELL, TRADE_SYMBOL, amountQty, ORDER_TYPE_MARKET)
    # order = orderSellQty(SIDE_SELL, TRADE_SYMBOL, amountQty, ORDER_TYPE_MARKET)
    
    print(order)
    # {side: "BUY", symbol: "ALTUSDT", quantity: "16", type: "MARKET"}  // As Amout 
    # {side: "BUY", symbol: "ALTUSDT", quoteOrderQty: "10", type: "MARKET"} // As Total USDT
    # {side: "BUY", symbol: "ALTUSDT", quoteOrderQty: "5", type: "MARKET"} // As Total USDT
    # {"side":"BUY","symbol":"BTCUSDT","quantity":"0.00020","type":"TAKE_PROFIT_LIMIT","stopPrice":"40000","price":"40150","timeInForce":"GTC"}
    # {"side":"BUY","symbol":"BTCUSDT","quantity":"0.00337","type":"TAKE_PROFIT_LIMIT","stopPrice":"","trailingDelta":"200","price":"4050"}
    # print("RSI: {}  Buy Price {} Qty {} Target Profit {}  Stop Loss {} Current Price {}  ".format (round(last_rsi, 2), str(buyprice), amountQty, str(buyprice * 1.005), str(buyprice * 0.995), close ))
    # if float(close) <= buyprice * 0.995 or float(close) >= 1.005 * buyprice:
                

                
ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()