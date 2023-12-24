from flask import Flask, render_template, request, flash, redirect, jsonify
import config, csv, datetime
from binance.client import Client
from binance.enums import *
from pprint import pprint
import json
from collections import defaultdict

app = Flask(__name__)
app.secret_key = b'NzU4udKNZ1bl3VM5VpYlEG2S9FstbmeYwv5ZTnWOcZxfS4cQf4dQmhSJRpRwihar'

client = Client(config.API_KEY, config.API_SECRET)


@app.route('/')
def index():
    title = 'CoinView'

    account = client.get_account()

    balances = account['balances']

    pprint(balances)

    balances = [each for each in balances if float(each.get('free')) > 0]

    # filter(lambda c: c[1] > 300000000, balances)
    #balances = filter(lambda x: x.get('asset', {}).get('free') > 0, balances)
    # [{'infos': {'foo': 'bar', 'spam': 'eggs'}, 'name': 'Bob'}]
    
    pprint(balances)
        
    positions = client.futures_account()['positions']
    
    pprint(positions)

    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances=balances, symbols=symbols, balances=balances)


@app.route('/buy', methods=['POST'])
def buy():
    print(request.form)
    try:
        order = client.create_order(symbol=request.form['symbol'], 
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=request.form['quantity'])
    except Exception as e:
        flash(e.message, "error")

    return redirect('/')


@app.route('/sell')
def sell():
    return 'sell'


@app.route('/settings')
def settings():
    return 'settings'

@app.route('/history')
def history():
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Jul, 2020", "12 Jul, 2020")

    processed_candlesticks = []

    for data in candlesticks:
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)