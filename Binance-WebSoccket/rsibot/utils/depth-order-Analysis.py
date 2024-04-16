import talib
from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
import config

# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# Specify the symbol and timeframe
symbol = 'BTCUSDT'
timeframe = '1h'  # You can change this to other timeframes like '5m', '15m', '1d', etc.

# Fetch historical klines data from Binance
klines = client.get_klines(symbol=symbol, interval=timeframe)

# Extract relevant data and create a DataFrame
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Calculate the order depth using TA-Lib
df['obv'] = talib.OBV(df['close'], df['volume'])

# Plot the Order Book Volume (OBV)
plt.figure(figsize=(10, 6))
df['obv'].plot(label='OBV', color='blue')
plt.title('Order Book Volume (OBV) Analysis')
plt.xlabel('Timestamp')
plt.ylabel('OBV')
plt.legend()
plt.show()
