## WebSocket test Net Binance
WebSocket
[place Ordes MISC](https://binance-docs.github.io/apidocs/websocket_api/en/#place-new-order-trade)

```bash
wss://testnet.binance.vision/ws
```

## Create Signature SHA256
```bash
echo -n “symbol=BNBUSDT&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&timestamp=1636982705000” | openssl dgst -sha256 -hmac “MYSECRET KEY HERE”

echo -n “symbol=BNBUSDT&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&timestamp=1636982705000” | openssl dgst -sha256 -hmac "ULWLGBK3SsM2zVsOiK9mqwSjayLfzEEhoL8PcuZSoybAak7qZoMscIn9zyBoXtb0"
```


## CoinGecko API
[API](https://www.coingecko.com/api/documentation)

fetch Request:
 binance GET https://api.binance.com/api/v3/exchangeInfo 
RequestHeaders:
 {} 
RequestBody:
 undefined 

Exchange.js:660
fetch Request:
 binance GET https://fapi.binance.com/fapi/v1/exchangeInfo 
RequestHeaders:
 {} 
RequestBody:
 undefined 

Exchange.js:660
fetch Request:
 binance GET https://dapi.binance.com/dapi/v1/exchangeInfo 
