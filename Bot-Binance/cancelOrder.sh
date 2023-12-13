#!/bin/bash
APIKEY="Y6v5L7mVVFhMp1unIrRdPywT4C92BFyMyRifkl2rKFqbrkMb3ZwWKplcpnkElC7G"
APISECRET="w6vDRejpQZMOd4VaQmPB86G6Ks8SFXdLm5Ld4ZWmaGsePF2ksQOZX1zshgNLg2SA"
#sURLPART2="symbol=BNBUSDT&side=BUY&type=LIMIT&quoteOrderQty=10&price=270.3&newOrderRespType=FULL"
URLPART2="symbol=BNBUSDT&orderId=12314"
RECVWINDOW=50000
RECVWINDOW="recvWindow=$RECVWINDOW"
TIMESTAMP="timestamp=$(( $(date +%s) *1000))"
QUERYSTRING="$URLPART2&$RECVWINDOW&$TIMESTAMP"

SIGNATURE=$(echo -n "$QUERYSTRING" | openssl dgst -sha256 -hmac $APISECRET | cut -c 10-)
SIGNATURE="signature=$SIGNATURE"

curl  -H "X-MBX-APIKEY: $APIKEY" -X POST "https://api.binance.com/api/v3/order?$URLPART2&$RECVWINDOW&$TIMESTAMP&$SIGNATURE"
echo
