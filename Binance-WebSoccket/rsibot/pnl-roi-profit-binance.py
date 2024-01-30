from binance.client import Client
import os
import pandas as pd
import matplotlib.pyplot as plt

# Binance API credentials
api_key = "your_api_key"
api_secret = "your_api_secret"

client = Client(api_key, api_secret)

# Function to fetch historical klines (candlestick data)
def fetch_historical_data(symbol, interval, start_date, end_date):
    klines = client.get_historical_klines(symbol, interval, start_str=start_date, end_str=end_date)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = pd.to_numeric(df['close'])
    return df

# Function to calculate PNL and ROI
def calculate_pnl_roi(symbol, entry_date, entry_price, exit_date, exit_price, quantity):
    historical_data = fetch_historical_data(symbol, '1d', entry_date, exit_date)

    entry_price = float(entry_price)
    exit_price = float(exit_price)
    quantity = float(quantity)

    # Calculate PNL
    pnl = (exit_price - entry_price) * quantity

    # Calculate ROI
    roi = (pnl / (entry_price * quantity)) * 100

    return pnl, roi

# Example trade details
symbol = 'BTCUSDT'
entry_date = '2022-01-01'
entry_price = '30000.0'
exit_date = '2022-02-01'
exit_price = '40000.0'
quantity = '0.01'

# Calculate PNL and ROI
pnl, roi = calculate_pnl_roi(symbol, entry_date, entry_price, exit_date, exit_price, quantity)

print(f'PNL: {pnl} USDT')
print(f'ROI: {roi}%')

# Plotting historical data (optional)
historical_data = fetch_historical_data(symbol, '1d', entry_date, exit_date)
plt.figure(figsize=(12, 6))
plt.plot(historical_data.index, historical_data['close'], label='Close Price')
plt.scatter(pd.to_datetime([entry_date, exit_date]), [entry_price, exit_price], marker='o', color='red', label='Entry/Exit')
plt.title('Historical Data with Entry/Exit Points')
plt.xlabel('Date')
plt.ylabel('Close Price (USDT)')
plt.legend()
plt.show()
