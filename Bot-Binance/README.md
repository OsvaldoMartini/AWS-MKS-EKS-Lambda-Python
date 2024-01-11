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



# TROUBLESHOOTING TULIND
## I USED THE vs_buildtools__7abaf36a580b419687a8e33f893cda3f
```bash
vs_buildtools__XXX  Installlation and lots of Youtubes to understand
```

# NPM INstal inside of the Compiler

**********************************************************************
** Visual Studio 2022 Developer Command Prompt v17.8.4
** Copyright (c) 2022 Microsoft Corporation
**********************************************************************
[vcvarsall.bat] Environment initialized for: 'x64_x86'

```bash
C:\Program Files\Microsoft Visual Studio\2022\Community>cd 1800
The system cannot find the path specified.

CD  <YOUR TULIND PROJECT>
npm istall tulind   WILL WORK !!!

```
