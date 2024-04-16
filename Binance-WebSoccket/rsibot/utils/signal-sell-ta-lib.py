import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib

# Generate example data
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='B')
prices = np.random.randn(len(dates)).cumsum() + 100
df = pd.DataFrame({'Date': dates, 'Price': prices})

# Calculate MACD using TA-Lib
df['macd'], df['signal'], _ = talib.MACD(df['Price'], fastperiod=12, slowperiod=26, signalperiod=9)

# Create a signal when MACD crosses below the Signal Line
df['Signal'] = np.where(df['macd'] < df['signal'], 1.0, 0.0)

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Price'], label='Price')
plt.plot(df['Date'], df['macd'], label='MACD')
plt.plot(df['Date'], df['signal'], label='Signal Line', linestyle='--')
plt.scatter(df['Date'][df['Signal'] == 1.0], df['Price'][df['Signal'] == 1.0], marker='v', color='red', label='Sell Signal')
plt.title('MACD Signal Down Example (Using TA-Lib)')
plt.xlabel('Date')
plt.ylabel('Price/MACD')
plt.legend()
plt.show()
