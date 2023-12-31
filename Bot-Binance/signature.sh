#!/usr/bin/env bash

SECRET="NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"


#QUERY_STRING="timestamp=1578963600000"
QUERY_STRING="timestamp=$(( $(date +%s) * 1000))"

TIMESTAMP="timestamp=$(( $(date +%s) * 1000))"
echo  "TIMESTAMP"
printf "\n"

echo "hashing string"
echo $QUERY_STRING
echo "and return"
echo -n $QUERY_STRING | \
openssl dgst -sha256 -hmac $SECRET

printf "\n"


QUERY_STRING="symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&$TIMESTAMP"

echo "hashing string"
echo $QUERY_STRING
echo "and return"
echo -n $QUERY_STRING | \
openssl dgst -sha256 -hmac $SECRET
