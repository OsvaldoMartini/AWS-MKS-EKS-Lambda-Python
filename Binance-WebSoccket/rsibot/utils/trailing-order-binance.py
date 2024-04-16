from binance.client import Client
import os
import config

# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# Symbol for the trading pair
symbol = 'BTCUSDT'

QTY_BUY = 5
ALLOCATION = 0.001
SYMBOL_LEVERAGE = 50
TICKER = 0
# Quantity and stop price for the initial limit order
quantity = 0.00012

limit_price = 43120
# order_create
# {"side":"BUY","symbol":"BTCUSDT","quantity":"0.00012","price":"43179.19","type":"LIMIT","timeInForce":"GTC"}
# trailing stop
# {"side":"BUY","symbol":"BTCUSDT","quantity":"0.00065","type":"TAKE_PROFIT_LIMIT","stopPrice":"","trailingDelta":"100","price":"43179.19"}
# {"side":"SELL","symbol":"BTCUSDT","quantity":"0.00034","type":"TAKE_PROFIT_LIMIT","stopPrice":"","trailingDelta":"200","price":"43179.19"}
# Trailing stop parameters
trail_percent = 1.0  # trailing stop percentage
activation_price = 43154  # initial activation price

# Place an initial limit order
order = client.create_order(
    symbol=symbol,
    side='BUY',
    type='LIMIT',
    timeInForce='GTC',
    quantity=quantity,
    price=limit_price
)

# Get the order ID and update the activation price
order_id = order['orderId']
activation_price = float(order['price'])

print(f"Initial limit order placed. Order ID: {order_id}")

# Function to update the trailing stop order
def update_trailing_stop(order_id, activation_price, trail_percent):
    order_info = client.get_order(symbol=symbol, orderId=order_id)
    current_price = float(order_info['price'])
    
    print(order_info)

    # Calculate the new stop price
    new_stop_price = round(current_price - (current_price * trail_percent / 100), 2)
    print('new_stop_price ' + str(new_stop_price))
    
    print('trail_percent ' + str(trail_percent))

    # Update the trailing stop order
    client.create_order(
        symbol=symbol,
        side='SELL',
        type='TRAILING_STOP_MARKET',
        quantity=quantity,
        activationPrice=activation_price,
        stopPrice=new_stop_price,
        callbackRate=trail_percent
    )

    print(f"Trailing stop order updated. New Stop Price: {new_stop_price}")

# Update the trailing stop order periodically (you can use a loop or schedule it as needed)
update_trailing_stop(order_id, activation_price, trail_percent)
