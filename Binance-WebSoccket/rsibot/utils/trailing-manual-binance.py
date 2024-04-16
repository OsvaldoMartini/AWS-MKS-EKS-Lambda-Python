from binance.client import Client
import time

# Replace YOUR_API_KEY and YOUR_SECRET_KEY with your Binance API key and secret key
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_SECRET_KEY'

# Initialize the Binance client
client = Client(api_key, api_secret)

def place_trailing_stop_limit_order(symbol, quantity, stop_price, limit_price, callback_rate):
    # Set up the trailing stop-limit order parameters
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TRADING_STOP_LIMIT,
        timeInForce=Client.TIME_IN_FORCE_GTC,
        quantity=quantity,
        stopPrice=stop_price,
        price=limit_price,
        callbackRate=callback_rate,
        newOrderRespType=Client.ORDER_RESP_TYPE_FULL
    )

    return order

if __name__ == "__main__":
    # Replace these values with your own
    symbol = 'BTCUSDT'
    quantity = 1.0  # The quantity of the asset you want to sell
    stop_price = 40000  # The trigger price for the stop-limit order
    limit_price = 39500  # The limit price for the stop-limit order
    callback_rate = 1.0  # The trailing stop callback rate

    try:
        order = place_trailing_stop_limit_order(symbol, quantity, stop_price, limit_price, callback_rate)
        print(f"Trailing stop-limit order placed successfully: {order}")
    except Exception as e:
        print(f"Error placing order: {e}")
