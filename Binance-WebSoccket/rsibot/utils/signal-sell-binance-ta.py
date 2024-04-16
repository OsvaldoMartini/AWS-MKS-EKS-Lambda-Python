import os
from binance.client import Client
import pandas as pd
import ta
import matplotlib.pyplot as plt
import config

# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# Symbol and timeframe
symbol = "BTCUSDT"
timeframe = "1h"
limit = 100  # Number of candles to fetch

# Fetch historical klines (candlestick data)
klines = client.get_klines(symbol=symbol, interval=timeframe, limit=limit)

# Extract relevant data from klines
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
df['close'] = pd.to_numeric(df['close'])

# Calculate MACD histogram using ta
df['macd_diff'] = ta.trend.macd_diff(df['close'], window_fast=12, window_slow=26, window_sign=9)

# Define MACD histogram threshold for sell signal
macd_diff_sell_threshold = 0

# Create a sell signal when MACD histogram crosses below the threshold
df['sell_signal'] = df['macd_diff'] < macd_diff_sell_threshold

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['macd_diff'], label='MACD Histogram')
plt.axhline(y=macd_diff_sell_threshold, color='r', linestyle='--', label='Sell Threshold')
plt.scatter(df.index[df['sell_signal']], df['close'][df['sell_signal']], marker='v', color='red', label='Sell Signal')
plt.title('MACD Histogram Sell Signal Example for {}'.format(symbol))
plt.xlabel('Date')
plt.ylabel('Price/MACD Histogram')
plt.legend()
plt.show()
