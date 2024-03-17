import json
import websocket

# socket='wss://stream.binance.com:9443/ws'
socket='wss://stream.binance.com:9443/ws/bonkusdt@depth10@100ms'

TOTALS = {}
TOTALS['BIDS'] = 0 
TOTALS['ASKS']= 0


def on_open(self):
    print("opened")
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params":
        [
         "btcusdt@depth@100ms"
         ],
        "id": 1
        }

    ws.send(json.dumps(subscribe_message))

def on_message(self, message):
    # print("received a message")

    ###### depths of bid/ask ######
    d = json.loads(message)
    for k, v in d.items():
        if k == "b":
           TOTALS['BIDS'] = TOTALS['BIDS'] + len(v) 
           print(f"bid depth : {TOTALS['BIDS']}")
        if k == "a":
           TOTALS['ASKS'] = TOTALS['ASKS'] + len(v) 
           print(f"ask depth : {TOTALS['ASKS']}")

def on_close(self):
    print("closed connection")

ws = websocket.WebSocketApp(socket,
                            on_open=on_open,
                            on_message=on_message,
                            on_close=on_close)

ws.run_forever()