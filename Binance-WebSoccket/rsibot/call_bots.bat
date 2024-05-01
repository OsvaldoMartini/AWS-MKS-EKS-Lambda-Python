@echo off
SETLOCAL

cd D:\Projects DevOps\AWS MKS EKS Lambda Python\Binance-WebSoccket\rsibot
start "BOT FUTURE"  python bot-future-BTC-USDT.py
start "BOT SPOT v1.2" python bot-future-BTC-USDT-v1.2.py


ENDLOCAL
