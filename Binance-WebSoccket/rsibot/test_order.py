import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import numpy as np
import math
import ccxt

# ENUMS
#  https://github.com/sammchardy/python-binance/blob/master/binance/enums.py

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'CFXUSDT'
QTY_BUY = 10 # USDT
QTY_SELL = 1000 # It Forces to Sell 100%
in_position = False

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

def orderSell_Other(side, symbol, quantity, order_type, attept, factor):
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

def orderSell(side, symbol, quantity, order_type, soldDesc):
    try:
        print("sending order  SIDE {} QTY {} SOLD MOTIVE: {}".format(side, quantity , soldDesc))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
    except Exception as e:
        print("an exception occured - {}".format(e))
        order = False
        while str(e).find("Account has insufficient balance for requested") >= 0 and not order:
            quantity = math.trunc(quantity - 1) 
            print("Attempt to SELL {}".format(str(quantity)))
            order = orderSell(side, symbol, math.trunc(quantity) , order_type, soldDesc)    
    return order


def orderSellQty(side, symbol, quantity, order_type):
    try:
        print("sending order  SIDE {} QRT {} ".format( side, quantity ))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order

def order_future_create_order(side, symbol, quantity, positionSide, order_type):
    try:
        print("FUTURES sending order  SIDE {} QRT {} ".format( side, quantity))
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

# TAKE_PROFIT_LIMIT order (modify this)
def order_future_profit_limit(side, symbol, quantity, takeProfit, positionSide, order_type):
    try:
        print("TAKE PROFIT FUTURES order  SIDE {} QRT {} ".format( side, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide,  
                                            type=order_type, 
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            quantity=quantity,
                                            # price=takeProfit,         # Specify the take profit price
                                            stopPrice=takeProfit,   # Specify the trigger price
                                            # closePosition=True,
                                            reduceOnly=True, 
                                            recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order


def order_future_stop_loss(side, symbol, quantity, stopLoss, positionSide, order_type):
    try:
        print("TAKE PROFIT FUTURES order  SIDE {} QRT {} ".format( side, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide,  
                                            type=order_type, 
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            quantity=quantity,
                                            price=stopLoss,         # Specify the take profit price
                                            stopPrice=stopLoss,   # Specify the trigger price
                                            # closePosition=True,
                                            reduceOnly=True, 
                                            recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order

def order_future_cancel_order(symbol, side, orderId, origClientOrderId):
    try:
        print("Cancel / Closing  {} orderID {} ".format( symbol, orderId))
        # dualSidePosition='false', 
        order = client.futures_cancel_order(symbol=symbol, 
                                            side=side, 
                                            orderId=orderId, 
                                            origClientOrderId=origClientOrderId,
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order


def order_future_cancel_all_open_order(symbol):
    try:
        print("Cancel All open Orders / Closing All  {} ".format( symbol))
        # dualSidePosition='false', 
        order = client.futures_cancel_all_open_orders(symbol=symbol, 
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order





def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')
    
    
ACTION_BUY = False    

def on_message(ws, message):
    global closes, in_position, buyprice, amountQty
    
    # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    print(close)        

    amountQty = 42453.08000
    # order = order(SIDE_BUY, TRADE_SYMBOL, QTY_BUY, ORDER_TYPE_MARKET)
    # TRADE_SYMBOL = '1000SATSUSDT'
  

    QTY_BUY = 5
    ALLOCATION = 100
    SYMBOL_LEVERAGE = 20
    TICKER = 0
    buyVolume = round((QTY_BUY * ALLOCATION) / float(close), TICKER)
    volume = round((QTY_BUY * SYMBOL_LEVERAGE) / float(close), TICKER)
    print("Volume: {}".format(volume))
    print("BuyVolumelume: {}".format(buyVolume))

    TRADE_SYMBOL = 'CFXUSDT'
    QTY_BUY = 5
    
    if not in_position:
        order = order_future_cancel_order(TRADE_SYMBOL, 'BOTH', 1706420720587, 'YU9jTugelnL8uBdasAZNmr')
        # order = order_future_cancel_order(TRADE_SYMBOL, 'BOTH', 7107214241, '7psQJgCAulNsQ6dDnD1A9y')
        # order = order_future_cancel_order(TRADE_SYMBOL, 'BOTH', 7107214275, 'KR6VqRg4Os6D5uXSuvvFus')
        # order = order_future_cancel_order(TRADE_SYMBOL, 'BOTH', 7107214189, 'TZrMNRYPNzko7I9w4nLKOQ')
        # # {'orderId': 7107189247, 'symbol': 'CFXUSDT', 'status': 'NEW', 'clientOrderId': 'r1TYhjT4NyLJJ6FSVcTYrc', 
        order = order_future_cancel_all_open_order(TRADE_SYMBOL)
        
    # if not in_position:
    #     if ACTION_BUY:
    #         order = order_future_create_order(SIDE_BUY, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
    #     else:
    #         order = order_future_create_order(SIDE_SELL, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
        
    #     print(order)
        
    #     takeProfit_WHEN_BUY = round(float(close) * 1.0055, 4)  # TakeProfit = 45000
    #     takeProfit_WHEN_SELL = round(float(close) * 0.995, 4)  # TakeProfit = 45000
    #     print("Take Profit When Selling : {}".format(takeProfit_WHEN_SELL))
    #     print("Take Profit When Buying : {}".format(takeProfit_WHEN_BUY))
    #     # order = order_future_profit_limit(SIDE_BUY, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, TAKE_PROFIT_LIMIT)
    #     # {"symbol":"CFXUSDT","type":"LIMIT","side":"SELL","quantity":452,"price":"0.2240","positionSide":"BOTH","leverage":20,"isolated":true,"timeInForce":"GTC","reduceOnly":true,"placeType":"position"}
    #     try:
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'SHORT', ORDER_TYPE_TAKE_PROFIT_MARKET)
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'LONG', ORDER_TYPE_TAKE_PROFIT_MARKET)
    #         if ACTION_BUY:
    #             order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_BUY, 'BOTH', FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET)
    #             order = order_future_stop_loss(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'BOTH', FUTURE_ORDER_TYPE_STOP)
    #         else:
    #             order = order_future_profit_limit(SIDE_BUY, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'BOTH', FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET)
    #             order = order_future_stop_loss(SIDE_BUY, TRADE_SYMBOL, volume, takeProfit_WHEN_BUY, 'BOTH', FUTURE_ORDER_TYPE_STOP)
                    
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'SHORT', ORDER_TYPE_TAKE_PROFIT_LIMIT)
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'LONG', ORDER_TYPE_TAKE_PROFIT_LIMIT)
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'BOTH', ORDER_TYPE_TAKE_PROFIT_LIMIT)
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'SHORT', ORDER_TYPE_TAKE_PROFIT)
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'LONG', ORDER_TYPE_TAKE_PROFIT)
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'BOTH', ORDER_TYPE_TAKE_PROFIT)
    #         # order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, takeProfit_WHEN_SELL, 'BOTH', ORDER_TYPE_LIMIT)
    #         print(order)
    #     except Exception as e:
    #         print("an exception occured - {}".format(e))
            
    in_position = True
    
    # orderSell(SIDE_SELL, TRADE_SYMBOL, int(math.trunc(amountQty)), ORDER_TYPE_MARKET, "TEST")

    
    # stopPrice = close * 0.995
    # price = close * 1.004
    # amountQty = 0.00023
    # order = order(SIDE_BUY, TRADE_SYMBOL, amountQty, ORDER_TYPE_MARKET)
    # order = orderSell(SIDE_SELL, TRADE_SYMBOL, amountQty, ORDER_TYPE_MARKET)
    # order = orderSellQty(SIDE_SELL, TRADE_SYMBOL, amountQty, ORDER_TYPE_MARKET)
    
    
    # {side: "BUY", symbol: "ALTUSDT", quantity: "16", type: "MARKET"}  // As Amout 
    # {side: "BUY", symbol: "ALTUSDT", quoteOrderQty: "10", type: "MARKET"} // As Total USDT
    # {side: "BUY", symbol: "ALTUSDT", quoteOrderQty: "5", type: "MARKET"} // As Total USDT
    # {"side":"BUY","symbol":"BTCUSDT","quantity":"0.00020","type":"TAKE_PROFIT_LIMIT","stopPrice":"40000","price":"40150","timeInForce":"GTC"}
    # {"side":"BUY","symbol":"BTCUSDT","quantity":"0.00337","type":"TAKE_PROFIT_LIMIT","stopPrice":"","trailingDelta":"200","price":"4050"}
    # print("RSI: {}  Buy Price {} Qty {} Target Profit {}  Stop Loss {} Current Price {}  ".format (round(last_rsi, 2), str(buyprice), amountQty, str(buyprice * 1.005), str(buyprice * 0.995), close ))
    # if float(close) <= buyprice * 0.995 or float(close) >= 1.005 * buyprice:


                

                
ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()