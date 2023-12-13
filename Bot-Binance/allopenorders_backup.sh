#!/bin/bash
APIKEY="Y6v5L7mVVFhMp1unIrRdPywT4C92BFyMyRifkl2rKFqbrkMb3ZwWKplcpnkElC7G"
APISECRET="w6vDRejpQZMOd4VaQmPB86G6Ks8SFXdLm5Ld4ZWmaGsePF2ksQOZX1zshgNLg2SA"
#sURLPART2="symbol=BNBUSDT&side=BUY&type=LIMIT&quoteOrderQty=10&price=270.3&newOrderRespType=FULL"
URLPART2="symbol=BNBUSDT&orderId=12314"
RECVWINDOW=5000
RECVWINDOW="recvWindow=$RECVWINDOW"
TIMESTAMP="timestamp=$(( $(date +%s) * 1000+500))"
#TIMESTAMP="$(( $(date +%s) *1000))"
QUERYSTRING="$URLPART2&$RECVWINDOW&$TIMESTAMP"

SIGNATURE=$(echo -n "$QUERYSTRING" | openssl dgst -sha256 -hmac $APISECRET | cut -c 10-)
SIGNATURE="signature=$SIGNATURE"

# curl  -H "X-MBX-APIKEY: $APIKEY" -X POST "https://api.binance.com/fapi/v3/openOrders?$URLPART2&$RECVWINDOW&$TIMESTAMP&$SIGNATURE" 'accept: application/json'


echo "TimeStamp: $TIMESTAMP"

#time="12:34:56.789"
#time=$(date +%s)
time=$(( $(date +%s) * 1000))"
IFS=":." read -r h m s ms <<<"$time"
echo $h $m $s $ms

milliseconds=$(( (h*3600 + m*60 + s)*1000 + ms ))
#milliseconds=$(( (h*3600 + m*60 + s) + ms ))
echo $milliseconds


curl -H "X-MBX-APIKEY: $APIKEY" -X 'GET' "https://api.binance.com/api/v3/openOrders?symbol=BNBUSDT&recvWindow=5000&$TIMESTAMP&signature=95c0a9af68533202da19f7509a08fa8a557da078f87af9d033d0aee017aff79e" -H 'accept: application/json'
echo

