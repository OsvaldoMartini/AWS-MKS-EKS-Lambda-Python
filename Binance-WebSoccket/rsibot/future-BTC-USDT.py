import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import numpy as np
import math
import ccxt

# balance = 19.50
# balance = 16.97
# balance = 14.30
# balance = 13.40
# balance = 13.20
# balance = 12.45
# balance = 12.54
# balance = 12.05
# balance = 11.36
# balance = 10.11
# balance = 10.11
# balance = 9.94
# balance = 9.79
# balance = 9.47
# balance = 9.53
# balance = 6.88
# balance = 6.82
# balance = 6.52
# balance = 6.33
# balance = 6.13
# balance = 6.13


ACTION_BUY = False


# ENUMS
#  https://github.com/sammchardy/python-binance/blob/master/binance/enums.py
# ORDER_TYPE_LIMIT = 'LIMIT'
# ORDER_TYPE_MARKET = 'MARKET'
# ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
# ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
# ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
# ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
# ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

# FUTURE_ORDER_TYPE_LIMIT = 'LIMIT'
# FUTURE_ORDER_TYPE_MARKET = 'MARKET'
# FUTURE_ORDER_TYPE_STOP = 'STOP'
# FUTURE_ORDER_TYPE_STOP_MARKET = 'STOP_MARKET'
# FUTURE_ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
# FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
# FUTURE_ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'
# FUTURE_ORDER_TYPE_TRAILING_STOP_MARKET = 'TRAILING_STOP_MARKET'

# TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
# TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
# TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill
# TIME_IN_FORCE_GTX = 'GTX'  # Post only order


RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
QTY_BUY = 10 # USDT
QTY_SELL = 1000 # It Forces to Sell 100%
in_position = False

SOCKET_SPOT = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL.lower())

# balance = 18.36

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
        print("TAKE PROFIT FUTURES order  SIDE {} Qtd {} Price PROFIT {}".format( side, quantity, takeProfit))
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
        print("STOP LOSS SIDE {} QRT {} Price Stop {}".format(side, quantity, stopLoss))
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

def order_future_cancel_order(symbol, side, orderId, clientOrderId):
    try:
        print("Cancel / Closing  {} orderID {} ".format( symbol, orderId))
        # dualSidePosition='false', 
        order = client.futures_cancel_order(symbol=symbol, 
                                            side=side, 
                                            orderId=orderId, 
                                            clientOrderId=clientOrderId,
                                            # timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            # timestamp=True,
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

def order_future_cancel_REDUDE_only(side, symbol, quantity, positionSide, order_type):
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

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')
    
def on_message(ws, message):
    global closes, in_position, buyprice, amountQty, PROFIT_WHEN_BUY, LOSSES_WHEN_BUY, PROFIT_WHEN_SELL, LOSSES_WHEN_SELL, volume, ACTION_BUY
    
    # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    # print(close)        

    amountQty = 42453.08000
    # order = order(SIDE_BUY, TRADE_SYMBOL, QTY_BUY, ORDER_TYPE_MARKET)
    # TRADE_SYMBOL = '1000SATSUSDT'
  

    QTY_BUY = 5
    ALLOCATION = 0.001
    SYMBOL_LEVERAGE = 50
    TICKER = 0
    # buyVolume = round((QTY_BUY * ALLOCATION) / float(close), 0)
    
    TRADE_SYMBOL = 'BTCUSDT'
    # PRECISION_PROFIT_LOSS = 7 # CFXUSDT
    PRECISION_PROFIT_LOSS = 1 # BTCUSDT
    QTY_BUY = 5
    
    PROFIT_CALC = 1.005   # BTCUSDT
    LOSS_CALC = 0.99813     # BTCUSDT
    # PROFIT_CALC = 1.0002   # CFXUSDT
    # LOSS_CALC = 0.9998     # CFXUSDT
       
    
    # order = order_future_cancel_REDUDE_only(SIDE_SELL, TRADE_SYMBOL, close, 449, 'BOTH', FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET)
    # {"symbol":"CFXUSDT","type":"MARKET","side":"SELL","positionSide":"BOTH","quantity":783,"reduceOnly":true,"placeType":"order-form"}
    # order = order_future_cancel_REDUDE_only(SIDE_BUY, TRADE_SYMBOL, 450, 'BOTH', 'MARKET')  # SHOULD WORK
    
    # Watcher Dog / Cancel / Reduce Position
    if in_position:
        try:
            if ACTION_BUY and (PROFIT_WHEN_BUY <= float(close) or LOSSES_WHEN_BUY >= float(close)): # TakeProfit
                order = order_future_cancel_REDUDE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
                order = order_future_cancel_all_open_order(TRADE_SYMBOL)
                # ACTION_BUY = not ACTION_BUY # INVERSE OF TRADING
                in_position = False
            elif not ACTION_BUY and (PROFIT_WHEN_SELL >= float(close) or LOSSES_WHEN_SELL <= float(close)):  # TakeProfit 
                order = order_future_cancel_REDUDE_only('BUY', TRADE_SYMBOL, volume,  'BOTH', 'MARKET')
                order = order_future_cancel_all_open_order(TRADE_SYMBOL)
                # ACTION_BUY = not ACTION_BUY # INVERSE OF TRADING
                in_position = False
            
            # order = order_future_cancel_order(TRADE_SYMBOL, 'BOTH', 7107214241, '7psQJgCAulNsQ6dDnD1A9y')
            # order = order_future_cancel_order(TRADE_SYMBOL, 'BOTH', 7107214275, 'KR6VqRg4Os6D5uXSuvvFus')
            # order = order_future_cancel_order(TRADE_SYMBOL, 'BOTH', 7107214189, 'TZrMNRYPNzko7I9w4nLKOQ')
            # # {'orderId': 7107189247, 'symbol': 'CFXUSDT', 'status': 'NEW', 'clientOrderId': 'r1TYhjT4NyLJJ6FSVcTYrc', 
        except Exception as e:
            print("an exception occured - {}".format(e))
    
    # Define the Prices Profit and Stop Loss 
    if not in_position:
        order = order_future_cancel_all_open_order(TRADE_SYMBOL)
        
        # Params
        buyVolume = round((QTY_BUY * ALLOCATION) / float(close), 1)
        volume = 0.003 #round((QTY_BUY * SYMBOL_LEVERAGE) / float(close), 1)  BTC-USDT "quantity":0.003   
        # volume = round((QTY_BUY * SYMBOL_LEVERAGE) / float(close), 1)  # CFX-USDT "quantity":410   
        print("Volume Actual: {}".format(volume))
        print("BuyVolumelume: {}".format(buyVolume))
        
        PROFIT_WHEN_BUY = round(float(close) * PROFIT_CALC, PRECISION_PROFIT_LOSS)  
        LOSSES_WHEN_BUY = round(float(close) * LOSS_CALC, PRECISION_PROFIT_LOSS)  
        PROFIT_WHEN_SELL = round(float(close) * LOSS_CALC, PRECISION_PROFIT_LOSS)  
        LOSSES_WHEN_SELL = round(float(close) * PROFIT_CALC, PRECISION_PROFIT_LOSS)  
        print("Close {} REDUCE_PROFIT_WHEN_BUY  value {}".format(str(close), str(PROFIT_WHEN_BUY)))
        print("Close {} REDUCE_LOSSES_WHEN_BUY  value {}".format(str(close), str(LOSSES_WHEN_BUY)))
        print("Close {} REDUCE_PROFIT_WHEN_SELL  value {}".format(str(close), str(PROFIT_WHEN_SELL)))
        print("Close {} REDUCE_LOSSES_WHEN_SELL  value {}".format(str(close), str(LOSSES_WHEN_SELL)))

        if ACTION_BUY:
          order = order_future_create_order(SIDE_BUY, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
        else:
          order = order_future_create_order(SIDE_SELL, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
          
        orderId = order['orderId']
        clientOrderId = order['clientOrderId']
        orderStatus = order['status']
        print("OrderId  {}  clientOrderId {}".format(orderId, clientOrderId))  
        # order = order_future_profit_limit(SIDE_BUY, TRADE_SYMBOL, volume, profit_sell, TAKE_PROFIT_LIMIT)
        # {"symbol":"CFXUSDT","type":"LIMIT","side":"SELL","quantity":452,"price":"0.2240","positionSide":"BOTH","leverage":20,"isolated":true,"timeInForce":"GTC","reduceOnly":true,"placeType":"position"}
        # try:
            
        #     if ACTION_BUY and orderStatus =='NEW':
        #         order = order_future_profit_limit(SIDE_SELL, TRADE_SYMBOL, volume, PROFIT_WHEN_BUY, 'BOTH', FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET)
        #         order = order_future_stop_loss(SIDE_SELL, TRADE_SYMBOL, volume, LOSSES_WHEN_BUY, 'BOTH', FUTURE_ORDER_TYPE_STOP)
        #         print('Created StopLoss and TakeProfit for  BYUING')
        #         print("BUYING current Close {}   Take Profit When Buying {}    Stop Loss When Buying  {}".format(close, PROFIT_WHEN_BUY, LOSSES_WHEN_BUY))
        #     elif not ACTION_BUY and orderStatus =='NEW':
        #         order = order_future_profit_limit(SIDE_BUY, TRADE_SYMBOL, volume, PROFIT_WHEN_SELL, 'BOTH', FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET)
        #         order = order_future_stop_loss(SIDE_BUY, TRADE_SYMBOL, volume, LOSSES_WHEN_SELL, 'BOTH', FUTURE_ORDER_TYPE_STOP)
        #         print('Created StopLoss and TakeProfit for SELLING')
        #         print("SELLING current Close {}   Take Profit When Selling {}    Stop Loss When Selling  {}".format(close, PROFIT_WHEN_SELL, LOSSES_WHEN_SELL))
            
        # except Exception as e:
        #     print("an exception occured - {}".format(e))
            
    in_position = True
    
    
    if in_position:
        if ACTION_BUY:
           print("BUY PROFIT {} Stop Loss {} Close {}  ".format(PROFIT_WHEN_BUY, LOSSES_WHEN_BUY, close))
        elif not ACTION_BUY:
           print("SELL PROFIT {} Stop Loss {} Close {}  ".format(PROFIT_WHEN_SELL, LOSSES_WHEN_SELL, close))
          
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
    # print("RSI: {}  Buy Price {} Qty {} Target Profit {}  Stop Loss {} Current Price {}  ".format (round(last_rsi, 2), str(buyprice), amountQty, str(buyprice * PROFIT_CALC), str(buyprice * 0.995), close ))
    # if float(close) <= buyprice * 0.995 or float(close) >= PROFIT_CALC * buyprice:


                

                
ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()