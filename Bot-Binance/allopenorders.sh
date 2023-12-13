#!/bin/bash
APIKEY="fpqeCxqgGWHjRxK4qmunjAFOEzB7CsQabuwUhhnkshgNEPi5kW5zsMH2TuO2CEmp"
APISECRET="NzU4udKNZ1bl3VM5VpYlEG2S9FstbmeYwv5ZTnWOcZxfS4cQf4dQmhSJRpRwihar"
#sURLPART2="symbol=BNBUSDT&side=BUY&type=LIMIT&quoteOrderQty=10&price=270.3&newOrderRespType=FULL"
URLPART2="symbol=BNBUSDT"

RECVWINDOW=5000
RECVWINDOW="recvWindow=$RECVWINDOW"
TIMESTAMP="timestamp=$(( $(date +%s) * 1000))"
#TIMESTAMP="$(( $(date +%s) *1000))"
QUERYSTRING="$URLPART2&$RECVWINDOW&$TIMESTAMP"

SIGNATURE=$(echo -n "$QUERYSTRING" | openssl dgst -sha256 -hmac $APISECRET | cut -c 10-)
#SIGNATURE=openssl dgst -sha256 -hmac $APISECRET
SIGNATURE="signature=$SIGNATURE"

#echo -n $QUERYSTRING |openssl dgst -sha256 -hmac $APISECRET

#SIGNATURE=echo openssl dgst -sha256 -hmac $APISECRET

echo "$URLPART2" 

curl  -H "X-MBX-APIKEY: $APIKEY" -X POST "https://fapi.binance.com/fapi/v1/openOrders?$URLPART2&$RECVWINDOW&$TIMESTAMP&$SIGNATURE" 'accept: application/json'

echo "TimeStamp: $TIMESTAMP"

#echo "$SIGNATURE"

# openssl dgst -sha256 -hmac $APISECRET

#curl -H "X-MBX-APIKEY:$APIKEY" -X 'GET' "https://fapi.binance.com/fapi/v1/openOrders?symbol=BNBUSDT&recvWindow=5000&$TIMESTAMP&signature=SIGNATURE"  -H 'accept: application/json'

#curl -H "X-MBX-APIKEY:$APIKEY" -X 'GET' "https://fapi.binance.com/fapi/v1/openOrders?symbol=BNBUSDT&recvWindow=5000&$TIMESTAMP&signature=$SIGNATURE"
echo

