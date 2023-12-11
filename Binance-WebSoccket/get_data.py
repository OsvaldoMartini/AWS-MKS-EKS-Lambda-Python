import config
from binance.client import Client

client = Client.get_all_tickers()

for price in prices:
    print(price)

    # candles = client.get_klines(symbol="BNBBTC", interval=Client.KLINE_INTERVAL_30MINUTE")
