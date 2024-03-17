from binance.client import Client
from binance.websockets import BinanceSocketManager
import pandas as pd
import talib
import numpy as np
import config

# Binance API credentials
api_key = "your_api_key"
api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET) #, tld='us'
bm = BinanceSocketManager(client)

# Symbol and timeframe
symbol = 'BTCUSDT'
timeframe = '1h'

# Fetch historical data for initial calculations
historical_data = client.get_historical_klines(symbol, timeframe, "50 hours ago UTC")
df = pd.DataFrame(historical_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
df['close'] = pd.to_numeric(df['close'])

# Calculate MACD for initial values
initial_macd, initial_signal, _ = talib.MACD(df['close'])
initial_macd = initial_macd[-1]
initial_signal = initial_signal[-1]

# Function to process WebSocket messages
def process_message(msg):
    global initial_macd, initial_signal
    candle = msg['k']
    current_close = float(candle['c'])
    # Append new close price to the dataframe
    df.loc[candle['T']] = current_close
    # Calculate MACD
    macd, signal, _ = talib.MACD(df['close'])
    # Check for signal after 50 closes
    if len(macd) > 50:
        macd = macd[-1]
        signal = signal[-1]
        # Check for MACD signal crossover
        if macd < signal and initial_macd > initial_signal:
            print("MACD sell signal detected!")
    # Update initial MACD and signal for future checks
    initial_macd = macd
    initial_signal = signal

# Start WebSocket
conn_key = bm.start_kline_socket(symbol, process_message)
bm.start()
