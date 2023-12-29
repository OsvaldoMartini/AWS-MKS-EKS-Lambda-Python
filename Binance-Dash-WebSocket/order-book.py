from dash import Dash, dcc, html, Input, Output, State, callback, dash_table, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from decimal import Decimal
import pandas as pd
import requests
import math
import warnings
from datetime import datetime
import config
from binance.client import Client
from binance.enums import *

warnings.simplefilter(action="ignore", category=FutureWarning)

app = Dash(external_stylesheets=[dbc.themes.CYBORG])

TRADE_SYMBOL = ""
TRADE_QUANTITY = "1"
# TYPE_ORDER  = "STOP" #"STOP" #"LIMIT" 
TYPE_ORDER  = "TAKE_PROFIT_MARKET" #"STOP" #"LIMIT" 
POSITION_SIDE = "BOTH"
PRICE ="73.350"
STOP_PRICE_PERC = 5
TIME_IN_FORCE = "GTC"
WORKING_TYPE = "MARK_PRICE"
PRICE_PROTECT = "true"
REDUCE_ONLY = "false"
# LIMIT
# MARKET
# STOP
# STOP_MARKET
# TAKE_PROFIT
# TAKE_PROFIT_MARKET
# TRAILING_STOP_MARKET


client = Client(config.API_KEY, config.API_SECRET) #, tld='us'
# client.futures_change_margin_type(symbol='ORDIUSDT', marginType='ISOLATED',leverage=5, recvWindow = 60000)
# client.futures_change_margin_type(symbol='ORDIUSDT', marginType='CROSSED', leverage=5, recvWindow = 60000)
# client.change_leverage(symbol="BTCUSDT", leverage=5, recvWindow = 60000)

# percent = lambda part, whole:float(whole) / 100 * float(part)
def percent(part, whole):
  try:
    return float(whole) * float(part) / 100
  except ZeroDivisionError:
    return 0

def truncate(f, n):
  try:
      return math.floor(f * 10 ** n) / 10 ** n
  except ZeroDivisionError:
      return 0
    
def adjust_leverage(symbol, client):
    client.futures_change_leverage(symbol=symbol, leverage=10)

def adjust_margintype(symbol, client):
    client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')

def order(symbol, side, typeOrder, positionSide, timeInForce, quantity, price, stop_price, workingType, leverage):
    print("Side {} Symbol {} Price {} Quantity {} Stop Price {} Leverage {}".format(side, symbol, price, quantity, stop_price, leverage))

    try:
        print("sending order")
        timestamp = datetime.now().timestamp()
        order = client.futures_create_order(
          symbol=symbol, 
          side=side, 
          type=typeOrder,
          positionSide=positionSide, 
          timeInForce=timeInForce, 
          quantity=quantity, 
          # price=price, 
          stopprice=stop_price,
          workingType=workingType,
          closePosition="true",
          timestamp = timestamp,
          recvWindow = 60000)

        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return e.message

    return order

def dropdown_option(title, options, default_value, _id):
  return html.Div(children=[
    html.H2(title),
    dcc.Dropdown(options = options, value = default_value, id=_id)
    ])

def create_dropdown(title, option, default_value, id_value):
  return html.Div(
    [
      # html.H4(" ".join(id_value.replace("-", " ").split(" ")[:-1]),
      #         style = {"padding":"0px 30px 0px 30px", "text-size":"15px"}),
      html.H6(title,
              style = {"padding":"0px 30px 0px 30px", "text-size":"15px"}),
      dcc.Dropdown(option, id=id_value, value=default_value),
    ], style = {"padding":"0px 30px 0px 30px"}
    )


app.layout = html.Div(children=[
  
 html.Div([
    create_dropdown("Pair", ["AGLDUSDT", "ORDIUSDT", "UNIUSDT", "AXSUSDT", "ETHUSDT", "BTCUSDT", "BAKEUSDT", "BONKUSDT", "TIAUSDT"], "UNIUSDT", "pair-select"),
    create_dropdown("Quantity Precision", ["0.0001","0.001", "0.01", "0.1", "1", "10", "100", "1000"], "0.001", "quantity-precision"),
    create_dropdown("Price Precision", ["0.0001","0.001", "0.01", "0.1", "1", "10", "100"], "0.001", "price-precision"),
  ], style = {"display":"flex", "margin":"auto", "width":"800px", "justify-content":"space-around"}),
    
  html.Div([
    dcc.Slider(min=0, max=125, step=5, value = 20, id ="leverage-slider"),
  ], id = "leverage-slider-container",
           style={"width":"800px", "margin":"auto", "padding-top":"30px"}),  
    
  html.Div(
    [
      # html.H4(" ".join(id_value.replace("-", " ").split(" ")[:-1]),
      #         style = {"padding":"0px 30px 0px 30px", "text-size":"15px"}),
      html.H4("Balance",
              style = {"padding":"0px 30px 0px 30px", "text-size":"15px"}),
      dcc.Input(id="balance-input", type='text', value="2.22"),
      dcc.Store(id="store"),
    ], style = {"padding":"0px 30px 0px 30px"}
  ), 
    
 html.P(id="output"),
 dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0),
    html.H1(id='timer_display', children='', style = {"positon":"relative","top":"0px"}),
    html.Div(children=[
      # html.H4(id='symbol-bet', children=''),
      html.Div(dcc.Input(id='symbol-bet', type='text'), style={'width':'0.05%','padding':5, 'verticalAlign':'middle', 'justifyContent':'center'}
            ),
      html.Div(dcc.Input(id='input-on-submit', type='text', value='0.0'), style={'width':'0.05%', 'display':'table-cell','padding':5, 'verticalAlign':'middle','justifyContent':'center'}
            ),
    ]),
    html.Button('BUY', id='submit-buy', n_clicks=0, style={
      "background-color": "#04AA6D", 
      "border": "none",
      "color": "white",
      "width":"100px"
    }),
    html.Button('SELL', id='submit-sell', n_clicks=0, style={
      "background-color": "#f44336", 
      "border": "none",
      "color": "white",
      "width":"100px"
      }),
    
    html.Div(children=[
      # html.H4(id='symbol-bet', children=''),
      # html.Div(dcc.Textarea(id='message-area', value='Enter a value and press submit'), 
      #          style={'width':'0.15%','padding':5, 'verticalAlign':'middle', 'justifyContent':'center', 'height': 300}
      #       ),
      html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'}),
      
    ]),
    
    # dcc.Textarea(
    #     id='textarea-example',
    #     value='Textarea content initialized\nwith multiple lines of text',
    #     style={'width': '100%', 'height': 300},
    # ),
   

 
 html.Div(children=[
  html.Div(children=[
    dash_table.DataTable(
      id= "ask_table",
      style_header={"display":"none"},
      style_cell={"minWidth":"140px", "maxWidth":"140px","width":"140px", "text-align":"center"}),
    html.H2(id="mid-price", style = {"padding-top":"30px","text-align":"center"}),
    dash_table.DataTable(
      id= "bid_table",
      style_header={"display":"none"},
      style_cell={"minWidth":"140px", "maxWidth":"140px","width":"140px", "text-align":"center"}),

  ], style = {"width": "300px"}),
  
  html.Div(children=[
    dropdown_option("Aggregate Level", options = ["0.0001","0.001", "0.01", "0.1", "1", "10", "100"],
                    default_value = "0.1", _id = "aggregation-level"),
  ], style = {"padding-left":"100px"}),
  ], style = {"display": "flex",
              "justify-content": "center",
              "align-items": "center",
              "height":"100vh",}), 

 dcc.Interval(id="timer", interval=2000),
])

# @callback(
#     Output('textarea-example-output', 'children'),
#     Input('textarea-example', 'value')
# )
# def update_output(value):
#     return 'You have entered: \n{}'.format(value)

# callback #
@app.callback(
  Output("symbol-bet", "value"),
  Output("quantity-precision", "value"),
  Output("price-precision", "value"),
  Input("pair-select", "value")
)

def update_control(value):
  TRADE_SYMBOL = value.upper()
  
  url_exchangeInfo =   "https://fapi.binance.com/fapi/v1/exchangeInfo?symbol={}".format(TRADE_SYMBOL)
  data = requests.get(url_exchangeInfo).json()
  
  TICK_SIZE = 0.0
  found = False
  info = data['symbols']
  for s in range(len(info)):
      if info[s]['symbol'] == TRADE_SYMBOL:
          filters = info[s]['filters']
          for f in range(len(filters)):
              if filters[f]['filterType'] == 'PRICE_FILTER':
                  TICK_SIZE = float(filters[f]['tickSize'])
                  found = True
                  break
          break
  if found:
      print("TICK SIZE found", TICK_SIZE)        
  else:
      print(f"tick_size not found for {TRADE_SYMBOL}")
  
  return value, TICK_SIZE, TICK_SIZE


# callback #1
@app.callback(
  Output("store", "data"),
  Input("balance-input", "value")
)
def update_store(value):
    if not value:
        raise PreventUpdate
    return {
        "value": value,
        "style": {
            "color": "red" if len(value) % 2 == 0 else "blue"
        }
    }

# callback #2
@app.callback(
  Output("output", "children"),
  Output("output", "style"),
  Input("store", "data")
)

def update_style(data):
  if not data:
    raise PreventUpdate
  return data["value"], data["style"]


@callback(
  Output("textarea-example-output", "children"),
  Input('submit-buy', 'n_clicks'),
  Input('submit-sell', 'n_clicks'),
  Input("balance-input","value"),
  Input("leverage-slider","value"),
  Input("quantity-precision","value"),
  State('input-on-submit', 'value'),
  State('symbol-bet', 'value'),
  prevent_initial_call=True
)

def update_output(buy_click, sell_click, balance, leverage, quantity_precision,  price, symbol):
  print("Symbol {} Price {} balance {} Leverage {} Qtdy Precision. {}".format(symbol, price, balance, leverage, quantity_precision))
    
  msg = "None of the buttons have been clicked yet"
  # print("Price ", price)
  # print("Symbol ", symbol)
    
  tick_after_decimal = str(quantity_precision)[::-1].find('.') 
  # print("tick_after_decimal", tick_after_decimal)
  
  # print("Leverage1", percent(float(leverage), float(balance)))
  if (float(price) > 0):
    TRADE_QUANTITY = truncate((float(leverage) * float(balance)) / float(price), tick_after_decimal)
    print("percent(float(STOP_PRICE_PERC), float(price)))", percent(float(STOP_PRICE_PERC), float(price)))
    print("TRADE_QUANTITY", TRADE_QUANTITY)
    STOP_PRICE = truncate(float(price) - percent(float(STOP_PRICE_PERC), float(price)), tick_after_decimal)   
    print("STOP_PRICE", STOP_PRICE)
      
    if "submit-buy" == ctx.triggered_id:
    #   #  put binance buy logic here
      order_succeeded = order(
        symbol,
        "BUY",
        TYPE_ORDER,
        "BOTH",
        TIME_IN_FORCE,
        TRADE_QUANTITY, 
        price,
        STOP_PRICE,
        "CONTRACT_PRICE",
        leverage
        )
      if order_succeeded:
        in_position = False
      msg = "BUY - > Price {} Quantity {}".format(price, TRADE_QUANTITY) 
      print("Buy! Buy! Buy!")
    elif "submit-sell" == ctx.triggered_id:
      #  put binance sell logic here
      order_succeeded = order(
        symbol,
        "SELL",
        TYPE_ORDER,
        "BOTH",
        TIME_IN_FORCE,
        TRADE_QUANTITY, 
        price,
        STOP_PRICE,
        "CONTRACT_PRICE",
        leverage
        )
      if order_succeeded:
        in_position = False
      msg = "SELL - > Price {} Quantity {}".format(price, TRADE_QUANTITY) 
      print("Sell! Sell! Sell!")
    
  print("Response:", msg)
    
  return msg


@app.callback(
    Output("timer_display", "children"),
    Input("interval-component", "n_intervals"),
)

def update_interval(n):
  # current_time = timer.time()
  current_time = datetime.now().time()
 
  # print(current_time.strftime('%H-%M-%S'))
  
  # time_interval_s = 120
  # time_interval_ms = time_interval_s * 1000

  # #calculate remaining time in ms
  # remaining = time_interval_ms - (n * 100)

  # minute = (remaining // 60000)
  # second = (remaining % 60000) // 1000
  # milisecond = (remaining % 1000) // 10
  # return u'{:02d}:{:02d}.{:02d}'.format(minute, second, milisecond)
  return current_time.strftime('%H-%M-%S')


def table_styling(df, side):
  
  if side == "ask":
    bar_color = "rgba(230, 31, 7, 0.2)"
    font_color = "rgb(230, 31, 7)"
  elif side == "bid":
    bar_color = "rgba(13, 230, 49, 0.2)"
    font_color = "rgb(13, 230, 49)"
    
    
  n_bins = 25 # This could Change
  bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
  
  quantity = df.quantity.astype(float)
  ranges = [ ((quantity.max() - quantity.min()) * i) + quantity.min() for i in bounds ]
    
  cell_bg_color = "#060606"
  
  styles = []
  
  for i in range(1, len(bounds)):
    min_bound = ranges[i-1]
    max_bound = ranges[i]
    max_bound_percentage = bounds[i] * 100
    styles.append({
      
      "if": {
        "filter_query": ("{{quantity}} >= {min_bound}" +
                         (" && {{quantity}} < {max_bound}" if ((i < len(bounds)) -1) else "")
                         ).format(min_bound = min_bound, max_bound=max_bound),
        "column_id": "quantity"
      },
      "background": (
        """
          linear-gradient(270deg,
          {bar_color} 0%,
          {bar_color} {max_bound_percentage}%,
          {cell_bg_color} {max_bound_percentage}%
          {cell_bg_color} 100%)
        """.format(bar_color = bar_color, cell_bg_color=cell_bg_color,
                   max_bound_percentage=max_bound_percentage),
      ),
        "paddingBottom":2,
        "paddingTop":2,
      })
  
  
  styles.append({
    "if": {"column_id": "price"},
    "color" : font_color,
    "background-color" : cell_bg_color
  })
  
  return styles

def aggregate_levels(levels_df, agg_level = Decimal('1'), side = "bid"):
  
  if side == "bid":
    right = False
    label_func = lambda x: x.left
    
  elif side == "ask":
    right = True
    label_func = lambda x: x.right
    
  
  # Round the Price down to the nearest multiple 10 cents 
  min_level = math.floor(Decimal(min(levels_df.price)) / agg_level - 1) * agg_level 
  max_level = math.ceil(Decimal(max(levels_df.price)) / agg_level + 1) * agg_level 

  level_bounds = [float(min_level + agg_level*x) for x in
                 range(int((max_level - min_level)/ agg_level)+ 1 )]
  
  levels_df["bin"] = pd.cut(levels_df.price, bins = level_bounds,
                            precision = 10, right = right)
  
  levels_df = levels_df.groupby("bin").agg(
    quantity = ("quantity", "sum")).reset_index()

  levels_df["price"] = levels_df.bin.apply(label_func)
  
  levels_df = levels_df[ levels_df.quantity > 0]
  
  levels_df = levels_df[["price", "quantity"]]
  
  # print(levels_df)
  return levels_df

@app.callback(
  Output("bid_table", "data"),
  Output("bid_table", "style_data_conditional"),
  Output("ask_table", "data"),
  Output("ask_table", "style_data_conditional"),
  Output("mid-price", "children"),
  Output("input-on-submit", "value"),
  Input("aggregation-level", "value"),
  Input("quantity-precision", "value"),
  Input("price-precision", "value"),
  Input("pair-select", "value"),
  Input("timer", "n_intervals"),
)

def update_orderbook(agg_level, quantity_precision, price_precision, symbol, n_intervals):
  
  # url = "https://api.binance.com/api/v3/depth"
  url = "https://fapi.binance.com/fapi/v1/depth"
  
  levels_to_show = 10
  
  params = {
    "symbol":symbol.upper(),
    "limit":"100",
  }
   
  data = requests.get(url, params=params).json()
  
  bid_df = pd.DataFrame(data["bids"], columns=["price","quantity"], dtype =float)
  ask_df = pd.DataFrame(data["asks"], columns=["price","quantity"], dtype =float)
  
#  Middle Price
  mid_price = (bid_df.price.iloc[0] + ask_df.price.iloc[0])/2
  # print(bid_df.price)
  # print("Largest BID: " ,bid_df.price.iloc[0])
  # print(ask_df.price) 
  # print("Smallest ASK: " ,ask_df.price.iloc[0])
  mid_price_precision = int(quantity_precision) + 2 
  mid_price = f"%.{mid_price_precision}f" % mid_price 
  

  # Bids
  bid_df = aggregate_levels(bid_df, agg_level = Decimal(agg_level), side = "bid")
  bid_df = bid_df.sort_values("price", ascending = False) 
  
  # Asks
  ask_df = aggregate_levels(ask_df, agg_level = Decimal(agg_level), side = "ask")
  ask_df = ask_df.sort_values("price", ascending = False) 
 
  # print(bid_df)
  
  bid_df = bid_df.iloc[:levels_to_show]
  ask_df = ask_df.iloc[-levels_to_show:]
  
  quantity_after_decimal = str(quantity_precision)[::-1].find('.')
  bid_df.quantity = bid_df.quantity.apply(
    lambda x: f"%.{quantity_after_decimal}f" % x)
  
  price_after_decimal = str(price_precision)[::-1].find('.')
  bid_df.price = bid_df.price.apply(
    lambda x: f"%.{price_after_decimal}f" % x)
    
  ask_df.quantity = ask_df.quantity.apply(
    lambda x: f"%.{quantity_after_decimal}f" % x)
  
  ask_df.price = ask_df.price.apply(
     lambda x: f"%.{price_after_decimal}f" % x)
    
  # print(bid_df.to_dict("records"))
   
  return (bid_df.to_dict("records"), table_styling(bid_df, "bid"),  
          ask_df.to_dict("records"),  table_styling(ask_df, "ask"), mid_price, mid_price)
  pass


if __name__ == "__main__":
  app.run_server(debug=True)
