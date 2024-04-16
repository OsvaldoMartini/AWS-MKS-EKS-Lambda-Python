from binance.client import Client
import config
import time
# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# Function to fetch current market price
def get_current_price(symbol):
    ticker = client.get_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

# Function to calculate PNL and ROI for an open position
def calculate_open_position_pnl_roi(symbol, entry_price, quantity, current_price=False):
    Long = (current_price - entry_price) * quantity
    Short = (entry_price - current_price) * quantity

    if not current_price:
        current_price = get_current_price(symbol)

    entry_price = float(entry_price)
    quantity = float(quantity)

    # Calculate PNL
    pnl = round((current_price - entry_price) * quantity, 4)

    # Calculate ROI
    roi = round((pnl / (entry_price * quantity)) * 100, 4) 

    return pnl, roi

def get_pnl(symbol):
    # Implement your logic to calculate PNL for the given symbol
    # You may need to use historical trades or other data depending on your strategy
    # For simplicity, this example assumes a function named calculate_pnl(symbol) exists
    pnl = calculate_pnl(symbol)
    return pnl

def get_roi(entry_price, current_price):
    # Implement your logic to calculate ROI based on entry and current prices
    # For simplicity, this example assumes a linear ROI calculation
    roi = (current_price - entry_price) / entry_price * 100
    return roi

def sell_long(symbol, entry_price, pnl_threshold, roi_threshold):
    current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    pnl = get_pnl(symbol)
    roi = get_roi(entry_price, current_price)

    if pnl >= pnl_threshold or roi >= roi_threshold:
        # Place a market sell order to exit the long position
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=your_quantity_here
        )
        print(f"Sold {symbol} position. PNL: {pnl}, ROI: {roi}")
    else:
        print(f"Not selling {symbol} position. PNL: {pnl}, ROI: {roi}")

# Example usage
symbol = 'BTCUSDT'
entry_price =  45271.8
"QUARTELY 0628"

# Replace with your actual entry price
pnl_threshold = 100  # Replace with your desired PNL threshold
roi_threshold = 10    # Replace with your desired ROI threshold
# symbol = 'BTCUSDT'
# entry_price = 45271.9
# exit_price = 42725
# quantity = 1.0

sell_long(symbol, entry_price, pnl_threshold, roi_threshold)
