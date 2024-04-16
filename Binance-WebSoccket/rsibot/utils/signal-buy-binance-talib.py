import os
from binance.client import Client
import pandas as pd
import talib
import matplotlib.pyplot as plt
import config

# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# Symbol and timeframe
symbol = "BTCUSDT"
timeframe = "1m"
limit = 100  # Number of candles to fetch

# Fetch historical klines (candlestick data)
klines = client.get_klines(symbol=symbol, interval=timeframe, limit=limit)

# Extract relevant data from klines
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
df['close'] = pd.to_numeric(df['close'])

# Calculate MACD using TA-Lib
df['macd'], df['signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

# Create a signal when MACD crosses above the Signal Line
df['buy_signal'] = df['macd'] > df['signal']

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['macd'], label='MACD')
plt.plot(df.index, df['signal'], label='Signal Line', linestyle='--')
plt.scatter(df.index[df['buy_signal']], df['close'][df['buy_signal']], marker='^', color='green', label='Buy Signal')
plt.title('MACD Buy Signal Example for {}'.format(symbol))
plt.xlabel('Date')
plt.ylabel('Price/MACD')
plt.legend()
plt.show()
