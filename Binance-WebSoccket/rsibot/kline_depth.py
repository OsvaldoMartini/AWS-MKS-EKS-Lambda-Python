from binance.client import Client
import websocket, json
import config


# Binance API credentials
client = Client(config.API_KEY, config.API_SECRET) #, tld='us'

# Symbol to monitor
symbol = 'btcusdt'

# Functi
# Function to process Kline WebSocket messages
def process_kline_message(message):
    print("Kline Data:", json.loads(message))

# Function to process Depth WebSocket messages
def process_depth_message(message):
    print("Depth Data:", json.loads(message))

# Start WebSocket for Kline data
kline_ws_url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_1m"
kline_ws = websocket.WebSocketApp(kline_ws_url, on_message=process_kline_message)
kline_ws.run_forever()

# Start WebSocket for Depth data
depth_ws_url = f"wss://stream.binance.com:9443/ws/{symbol}@depth"
depth_ws = websocket.WebSocketApp(depth_ws_url, on_message=process_depth_message)
depth_ws.run_forever()