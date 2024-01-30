from binance.client import Client
from datetime import datetime
import config

# Binance API credentials
# api_key = "your_api_key"
# api_secret = "your_api_secret"

client = Client(config.API_KEY, config.API_SECRET)

# Function to calculate PNL and ROI
def calculate_pnl_roi(symbol, entry_price, exit_price, quantity):
    # Get historical klines data
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY)

    # Extract closing prices and timestamps
    closes = [float(kline[4]) for kline in klines]
    timestamps = [int(kline[0]) for kline in klines]

    # Find index of entry and exit timestamps
    # entry_timestamp = int(datetime.timestamp(datetime.strptime(entry_price, "%Y-%m-%d %H:%M:%S")))
    # exit_timestamp = int(datetime.timestamp(datetime.strptime(exit_price, "%Y-%m-%d %H:%M:%S")))
    # entry_index = timestamps.index(entry_timestamp)
    # exit_index = timestamps.index(exit_timestamp)

    # Calculate PNL
    pnl = (exit_price - entry_price) * quantity

    # Calculate ROI
    roi = (pnl / (entry_price * quantity)) * 100

    return pnl, roi

# Example usage
symbol = 'BTCUSDT'
entry_price = 43250.0
exit_price = 43280.0
quantity = 1.0

pnl, roi = calculate_pnl_roi(symbol, entry_price, exit_price, quantity)

print(f"PNL: {pnl} USDT")
print(f"ROI: {roi}%")
