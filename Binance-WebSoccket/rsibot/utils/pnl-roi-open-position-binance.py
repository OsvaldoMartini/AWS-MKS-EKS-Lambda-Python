from binance.client import Client
import os
import pandas as pd
import config
import time
# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# SPOT Function to fetch current market price
def get_current_price(symbol):
    ticker = client.get_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

# FUTURES Function to fetch current market price
def get_current_price_futures(symbol):
    print(client.futures_symbol_ticker(symbol=symbol)) 
    return float(client.futures_symbol_ticker(symbol=symbol)['price'])

# Function to calculate PNL and ROI for an open position
def calculate_open_position_pnl_roi(symbol, entry_price, quantity, current_price=False):
    if not current_price:
        current_price = get_current_price(symbol)

    entry_price = float(entry_price)
    quantity = float(quantity)

    # Calculate PNL
    pnlLong = round((current_price - entry_price) * quantity, 4)
    pnlShort = round((entry_price - current_price) * quantity, 4)
    
    # Calculate ROI
    roiLong = round((pnlLong / (entry_price * quantity)) * 100, 4) 

    return pnlLong, roiLong, pnlShort

# Example open position details
symbol = 'BTCUSDT'

entry_price = 42841.95
quantity = 0.00128
# Fee = 0.00000128

# quantity = quantity - Fee
# Calculate PNL and ROI for the open position
targetPrice = 43600
while True:
    pnlLong, roiLong, pnlShort = calculate_open_position_pnl_roi(symbol, entry_price, quantity, targetPrice)


    print(f'Current Market Price Futures: {get_current_price_futures(symbol)} USDT')
    print(f'Current Market Price: {get_current_price(symbol)} USDT')
    print(f'PNL Long: {pnlLong} USDT')
    print(f'ROI Long: {roiLong}%')
    print(f'PNL Short: {pnlShort}%')
    time.sleep(0.5) 
