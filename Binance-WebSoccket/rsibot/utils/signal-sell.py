import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Generate example data
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='B')
prices = np.random.randn(len(dates)).cumsum() + 100
df = pd.DataFrame({'Date': dates, 'Price': prices})

# Calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    data['Short_MA'] = data['Price'].ewm(span=short_window, adjust=False).mean()
    data['Long_MA'] = data['Price'].ewm(span=long_window, adjust=False).mean()
    data['MACD'] = data['Short_MA'] - data['Long_MA']
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()

calculate_macd(df)

# Create a signal when MACD crosses below the Signal Line
df['Signal'] = np.where(df['MACD'] < df['Signal_Line'], 1.0, 0.0)

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Price'], label='Price')
plt.plot(df['Date'], df['MACD'], label='MACD')
plt.plot(df['Date'], df['Signal_Line'], label='Signal Line', linestyle='--')
plt.scatter(df['Date'][df['Signal'] == 1.0], df['Price'][df['Signal'] == 1.0], marker='v', color='red', label='Sell Signal')
plt.title('MACD Signal Down Example')
plt.xlabel('Date')
plt.ylabel('Price/MACD')
plt.legend()
plt.show()
