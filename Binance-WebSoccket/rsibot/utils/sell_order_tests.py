from binance.client import Client
from binance.enums import *
import time
import config
import json

# Function to search for a word in the JSON data
def search_word_in_json(data, word):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                search_word_in_json(value, word)
            elif isinstance(value, str) and word in value:
                print(f"Found '{word}' in the JSON response.")
    elif isinstance(data, list):
        for item in data:
            search_word_in_json(item, word)


def order_sell(side, symbol, quantity, order_type, soldDesc, attemptRatio):
    try:
        print("sending order  SIDE {} QTY {} SOLD MOTIVE: {}".format(side, quantity , soldDesc))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type="MARKET", recvWindow = 60000)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        order = False
        while str(e).find("Account has insufficient balance for requested") >= 0 and not order:
            quantity -= attemptRatio
            # quantity = math.trunc(quantity) 
            print("Attempt to SELL {}".format(str(quantity)))
            order = order_sell(side, symbol, float(quantity) , order_type, soldDesc, attemptRatio)    
    return order

# FUTURES
def order_future_cancel_all_open_order(symbol):
    try:
        # logger.info("Cancel All open Orders / Closing All  {} ".format( symbol))
        # cleardualSidePosition='false', 
        order = client.futures_cancel_all_open_orders(symbol=symbol, 
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            recvWindow = 60000)
        # logger.info(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
    return order  

def order_future_cancel_REDUCE_only(side, symbol, quantity, positionSide, order_type):
    try:
        print("reduce 100% Cancel Order / Closing Order  {} QTY {} ".format(symbol, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(side='SELL', 
                                            symbol=symbol,
                                            quantity=quantity,
                                            positionSide='BOTH',  
                                            type='MARKET', 
                                            reduceOnly=True, 
                                            recvWindow = 60000)        
        print(order)
        return order
    except Exception as e:
        print("an exception occured - {}".format(e))
    return False


TRADE_SYMBOL = 'BTCUSDT'
SPOT_DEC = 5

# Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your actual API key and secret

# Initialize the Binance client
client = Client(config.API_KEY, config.API_SECRET) #, tld='us'

server_time = int(time.time() * 1000)  # Convert to milliseconds

# Specify recvWindow (in milliseconds)
recv_window = 5000  # Adjust this value as per exchange requirements

# Ensure that our timestamp falls within the recvWindow
timestamp = max(server_time, server_time - recv_window)

print("Time:{}".format(timestamp)) 

# Get account information
# account_info = client.get_account(recvWindow = timestamp)

# usdtBalance = client.get_asset_balance(asset='USDT').get('free')
# btcBalance = client.get_asset_balance(asset='BTC').get('free')

positions = client.futures_position_information(symbol=TRADE_SYMBOL, timestamp = int(time.time() * 1000), recvWindow = 60000)

# Print positions
for position in positions:
    print("Positons: {}".format(position))
    futures_entry_price = position['entryPrice'] 
    unRealizedProfit = position['unRealizedProfit']
    positionAmt = position['positionAmt']
    notional = position['notional']

print(futures_entry_price)
                                    

# Amount QTY
print("QT: {:.5f}".format(10/65284.45))


volume = 0.000143568
volume = 0.002
soldDesc = "Empty"

# order_future = order_future_cancel_all_open_order(TRADE_SYMBOL)
# order_future = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, round(volume, 3), 'BOTH', 'MARKET')


# order_succeeded = order_sell(SIDE_SELL, TRADE_SYMBOL.upper(), round(volume, SPOT_DEC), ORDER_TYPE_MARKET, soldDesc, 0.00005)

print ("response")
# print (order_succeeded)
# search_word_in_json(order_succeeded, "APIError")

# order_sell = Client.order_market_sell(symbol='BTCUSDT', quantity=0.0006, recvWindow = 300)


# # Loop through each balance to sell all available assets
# for balance in account_info['balances']:
#     asset = balance['asset']
#     free = float(balance['free'])
#     print("Asset {}".format(asset)) 
#     print("Free {}".format(free)) 
#     if free > 0:
#         # Place a market sell order for the current asset
#         symbol = asset + 'USDT'  # Assuming you want to sell against USDT
#         # order = client.order_market_sell(symbol=symbol, quantity=free)
#         # order = client.order_market_sell(symbol=symbol, quantity=free, recvWindow = 60000)
        
#         print(f"Sold {free} {asset} at market price.")
