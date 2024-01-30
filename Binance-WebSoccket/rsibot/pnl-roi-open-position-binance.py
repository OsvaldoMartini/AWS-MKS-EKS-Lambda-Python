from binance.client import Client
import os
import pandas as pd
import config

# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# Function to fetch current market price
def get_current_price(symbol):
    ticker = client.get_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

# Function to calculate PNL and ROI for an open position
def calculate_open_position_pnl_roi(symbol, entry_price, quantity):
    current_price = get_current_price(symbol)

    entry_price = float(entry_price)
    quantity = float(quantity)

    # Calculate PNL
    pnl = round((current_price - entry_price) * quantity, 4)

    # Calculate ROI
    roi = round((pnl / (entry_price * quantity)) * 100, 4) 

    return pnl, roi

# Example open position details
symbol = 'BTCUSDT'

entry_price = '43250.26'
quantity = '0.01'

# Calculate PNL and ROI for the open position
pnl, roi = calculate_open_position_pnl_roi(symbol, entry_price, quantity)

print(f'Current Market Price: {get_current_price(symbol)} USDT')
print(f'PNL: {pnl} USDT')
print(f'ROI: {roi}%')
