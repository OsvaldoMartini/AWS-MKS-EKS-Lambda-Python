from dash import html, dcc, Output, Input, Dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import pandas_ta as ta
import requests
import config
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

app = Dash(external_stylesheets = [dbc.themes.CYBORG])

def create_dropdown(option, id_value):
  return html.Div(
    [
      html.H4(" ".join(id_value.replace("-", " ").split(" ")[:-1]),
              style = {"padding":"0px 30px 0px 30px", "text-size":"15px"}),
      dcc.Dropdown(option, id=id_value, value=option[0]),
    ], style = {"padding":"0px 30px 0px 30px"}
    )

app.layout = html.Div([
  # dcc.Dropdown(["btcusd", "ethusd", "xrpusd"], id="coin-select", value="btcusd"),
  # dcc.Dropdown(["60", "3600", "86400"], id="timeframe-select", value="60"),
  # dcc.Dropdown(["20", "50", "100"], id="num-bars-select", value="20"),
  html.Div([
    create_dropdown(["AGLDUSDT", "ORDIUSDT", "AXSUSDT", "ETHUSDT", "BTCUSDT", "BAKEUSDT", "BONKUSDT", "TIAUSDT"], "coin-select"),
    create_dropdown(["60", "3600", "86400"], "timeframe-select"),
    create_dropdown(["20", "50", "100"], "num-bars-select"),
  ], style = {"display":"flex", "margin":"auto", "width":"800px", "justify-content":"space-around"}),
    
  html.Div([
    dcc.RangeSlider(0,20,1, value = [0,20], id ="range-slider"),
  ], id = "range-slider-container",
           style={"width":"800px", "margin":"auto", "padding-top":"30px"}),
  
  dcc.Graph(id="candles"),
  dcc.Graph(id="indicator"),
  dcc.Interval(id="interval", interval = 1000)
])

# Change the Value of Range Slider
@app.callback(
  Output("range-slider-container","children"),
  Input("num-bars-select","value")
)

def update_rangeslider(num_bars):
  # To NOT be Crowded of BARS I divide per 20
  return dcc.RangeSlider(min=0, max=int(num_bars), step=int(int(num_bars)/20), 
    value= [0, int(num_bars)], id="range-slider")


@app.callback(
  Output("candles","figure"),
  Output("indicator","figure"),
  Input("interval", "n_intervals"),
  Input("coin-select","value"),
  Input("timeframe-select","value"),
  Input("num-bars-select","value"),
  Input("range-slider","value")
)

def update_figure(n_intervals,symbol, timeframe, num_bars, range_values):
  # url = f"http://www.bitstamp.net/api/v2/ohlc/{symbol}/"
  # url = f"https://fapi.binance.com/fapi/v1/klines/{symbol}/"
  # start_str=str((pd.to_datetime('today')-pd.Timedelta(str(14)+' days')).date())
  
  # data = client.get_historical_klines(symbol=symbol, start_str=start_str, interval="1m")
  # data = client.futures_klines(symbol=symbol.upper(), interval="1m", start_str = "14 days ago UTC")
  data = client.futures_klines(symbol=symbol.upper(), interval="1m", startTime = "10 days ago UTC", limit=100)
  
  
    # params = {
  #   "symbol":symbol,
  #   "timeInterval":15,
  #   "limit":100
  # }  
  
  # print(start_str)
  # params = {
  #   "step":timeframe,
  #   "limit":int(num_bars) + 14
  # }  
  
  # data = requests.get(url, params=params).json()["data"]["ohlc"]
  D = pd.DataFrame(data)
  
  D.columns = ['open_time', 'open','high','low','close','volume','close_time','qav','num_trades',
                  'taker_base_vol','taker_quote_vol','is_best_mathc']
  # print(D)
  usecols=['close', 'high', 'low', 'open', 'open_time', 'volume']

  data = D[usecols]
  data["timestamp"]  = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in data.open_time]
  # data.timestamp = pd.to_datetime(data.open_time, unit = "s")
    
  # Calculating the RSI
  # 14 Days windows to be calculated 
  data["rsi"] = ta.rsi(data.close.astype(float))
  # 14 Days windows to be calculated for Warmer base
  # It DEPENDS WHERE COME FROM DE DATA 
  data = data.iloc[5:]
  data = data.iloc[range_values[0]:range_values[1]]
  
  print(data)
  
  candles = go.Figure(
    data = [
      go.Candlestick(
        x = data.timestamp,
        open = data.open,
        high = data.high,
        low = data.low,
        close = data.close
      )
    ]
  )
  
  # Candle Stick Graphics
  candles.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_dark")
  # candles.update_layout(transition_duration=500)
  
  # RSI Graphics
  indicator = px.line(x=data.timestamp, y=data.rsi, height=300, template="plotly_dark")
  # indicator.update_layout(transition_duration=500)
  
  # print(data)
  
  return candles, indicator
 
if __name__ == "__main__":
  app.run_server(debug=True, port=8060)
  