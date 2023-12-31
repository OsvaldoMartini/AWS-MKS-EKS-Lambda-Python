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
import numpy as np

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
# 1- LIMIT,
# 2- MARKET,
# 3- STOP_LOSS,
# 4- STOP_LOSS_LIMIT,
# 5- TAKE_PROFIT,
# 6- TAKE_PROFIT_LIMIT,
# 7- LIMIT_MAKER


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

def tick_size(price, minPrice, tickSize):
  return round((price - minPrice) / tickSize) * tickSize + minPrice;

def order(symbol, side, typeOrder, positionSide, timeInForce, quantity, price, stop_price, workingType, leverage):
    print("Side {} Symbol {} Price {} Quantity {} Stop Price {} Leverage {}".format(side, symbol, price, quantity, stop_price, leverage))

    price = round(tick_size(float(price), 0.0000010, 0.0000010), 7)
    stop_price = round(tick_size(float(stop_price), 0.0000010, 0.0000010),7)
    print("Min Price {}".format(price))
    quantity = round(quantity,0)
    
    try:
        print("sending order")
        timestamp = datetime.now().timestamp()
        order = client.futures_create_order(
          symbol=symbol, 
          callbackRate=1,
          side=side, 
          type=typeOrder,
          positionSide=positionSide, 
          timeInForce=timeInForce, 
          quantity=quantity, 
          price=price, 
          stopprice=stop_price,
          workingType=workingType,
          # closePosition="true",
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
    create_dropdown("Pair", ["AGLDUSDT", "ORDIUSDT", "UNIUSDT", "AXSUSDT", "ETHUSDT", "BTCUSDT", "BAKEUSDT", "1000BONKUSDT", "TIAUSDT"], "1000BONKUSDT", "pair-select"),
    create_dropdown("Quantity Precision", ["0.00000001", "0.0000001", "0.000001", "0.00001", "0.0001", "0.001", "0.01", "0.1", "1", "10", "100", "1000", "10000"], "0.001", "quantity-precision"),
    create_dropdown("Price Precision", ["0.00000001", "0.0000001", "0.000001", "0.00001", "0.0001", "0.001", "0.01", "0.1", "1", "10", "100", "1000", "10000"], "0.001", "price-precision"),
  ], style = {"display":"flex", "margin":"auto", "width":"800px", "justify-content":"space-around"}),
    
  html.Div([
    dcc.Slider(min=0, max=125, step=5, value = 20, id ="leverage-slider"),
  ], id = "leverage-slider-container",
           style={"width":"800px", "margin":"auto", "padding-top":"30px"}),  
  
 html.Div(children=[
    html.Div(children=[
      html.Div(
      [
        # html.H4(" ".join(id_value.replace("-", " ").split(" ")[:-1]),
        #         style = {"padding":"0px 30px 0px 30px", "text-size":"15px"}),
        html.Div(children=[
          create_dropdown("Type Order", [
                "LIMIT",
                "MARKET",
                "STOP",
                "STOP_MARKET",
                "TAKE_PROFIT",
                "TAKE_PROFIT_MARKET",
                "TRAILING_STOP_MARKET"],
                          "MARKET", "type-order"),
        ], ),
        
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
      html.Div(dcc.Input(id='price-to-submit', type='text'), style={'width':'0.05%', 'display':'table-cell','padding':5, 'verticalAlign':'middle','justifyContent':'center'}
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
 
  ]),
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
    create_dropdown("Aggregate Level", ["0.00000001", "0.0000001", "0.000001", "0.00001", "0.0001", "0.001", "0.01", "0.1", "1", "10", "100"],
                    "0.001", "aggregation-level"),
  ], style = {"padding-left":"100px"}),
  ], style = {"display": "flex",
              "justify-content": "center",
              "align-items": "center",
              # "height":"100vh",
              }), 

 dcc.Interval(id="timer-update-order-book", interval=2000),
])

# @callback(
#     Output('textarea-example-output', 'children'),
#     Input('textarea-example', 'value')
# )
# def update_output(value):
#     return 'You have entered: \n{}'.format(value)

# def __init__(self, name, age):
#     # self.name = name
#     # self.age = age
#     update_control("1000BONKUSDT")

# callback #
@app.callback(
  Output("symbol-bet", "value", "allow_duplicate=True"),
  Output("price-to-submit", "value", "allow_duplicate=True"),
  Output("quantity-precision", "value"),
  Output("price-precision", "value"),
  Output("aggregation-level", "value", "allow_duplicate=True"),
  Input("pair-select", "value"),
  prevent_initial_call=True
)

def get_decimal_tick(value):
  print("1 CALLBACK EVENT:", ctx.triggered_id)
  print("GET DECIMAL TICK SIZE")
  TRADE_SYMBOL = value.upper()
    
  levels_to_show = 10
    
  # url_exchangeInfo =   "https://fapi.binance.com/fapi/v1/exchangeInfo?symbol={}".format(TRADE_SYMBOL)
  params = {
    "symbol":TRADE_SYMBOL,
    "limit":"5",
  }
  
  url = "https://fapi.binance.com/fapi/v1/depth"
  data = requests.get(url, params=params).json()
  pre_data = pd.DataFrame(data["bids"], columns=["price","quantity"])
  price = pre_data.price.iloc[0]
  print("DECIMAL TICK SIZE", price)
  decPos = str(pre_data.price.iloc[0])[::-1].find('.')
  factor = 10 ** decPos
  TICK_SIZE = np.format_float_positional(math.floor(1 ) / factor, trim='-') 
  found = True
  # info = data['symbols']
  # for s in range(len(info)):
  #     if info[s]['symbol'] == TRADE_SYMBOL:
  #         filters = info[s]['filters']
  #         for f in range(len(filters)):
  #             if filters[f]['filterType'] == 'PRICE_FILTER':
  #                 TICK_SIZE = float(filters[f]['tickSize'])
  #                 found = True
  #                 break
  #         break
  if found:
      print("TICK SIZE found {}  SYMBOL {}".format(TICK_SIZE, value))        
  else:
      print(f"tick_size not found for {TRADE_SYMBOL}")
  
  return value, price, TICK_SIZE, TICK_SIZE, TICK_SIZE
  pass


# callback #1
@app.callback(
  Output("store", "data"),
  Output("aggregation-level", "value", "allow_duplicate=True"),
  Input("balance-input", "value"),
  Input("price-to-submit", "value"),
  State("interval-component", "n_intervals"),
  prevent_initial_call=True
)

def update_store(value, price, n_intervals):
    print("2 CALLBACK EVENT:", ctx.triggered_id)
    if n_intervals > 1 and ctx.triggered_id == "price-to-submit":
      raise PreventUpdate
    
    print("UPDATE STORE BALANCE {} PRICE {}".format(value, price))
    if not value:
        raise PreventUpdate
    decPos = price[::-1].find('.')
    factor = 10 ** decPos
    TICK_SIZE = np.format_float_positional(math.floor(1 ) / factor, trim='-') 
    # print("UPDATE STORE TICK_SIZE {} ".format(TICK_SIZE))
    return ({
        "value": value,
        "style": {
            "color": "red" if len(value) % 2 == 0 else "blue"
        }
    }, TICK_SIZE)
  

# callback #2
@app.callback(
  Output("output", "children"),
  Output("output", "style"),
  Input("store", "data")
)

def update_style(data):
  if ctx.triggered_id is None:
      raise PreventUpdate
  print("3 CALLBACK EVENT:", ctx.triggered_id)
  if not data:
    raise PreventUpdate
  return data["value"], data["style"]


@callback(
  Output("textarea-example-output", "children"),
  Input('submit-buy', 'n_clicks'),
  Input('submit-sell', 'n_clicks'),
  State("balance-input","value"),
  State("leverage-slider","value"),
  State("quantity-precision","value"),
  State("type-order","value"),
  State('price-to-submit', 'value'),
  State('symbol-bet', 'value'),
  prevent_initial_call=True
)

def update_output(buy_click, sell_click, balance, leverage, quantity_precision, type_order, price, symbol):
  if ctx.triggered_id == "type-order" or ctx.triggered_id == "quantity-precision" or ctx.triggered_id == "leverage-slider":
    raise PreventUpdate
  print("Type Order", type_order)
    
  # print("quantity_precision", quantity_precision)
  # quantity_precision = np.format_float_positional(quantity_precision, trim='-')
  msg = "None of the buttons have been clicked yet"
  
  if (len(price) > 0):
    print("Price", price)
    # price = np.format_float_positional(price, trim='-')
    print("Symbol {} Price {} balance {} Leverage {} Qtdy Precision. {}".format(symbol, price, balance, leverage, quantity_precision))
    
  # # print("Price ", price)
  # # print("Symbol ", symbol)
    
  tick_after_decimal = str(price)[::-1].find('.') 
  # print("Tick after decimal ", tick_after_decimal)
  # # print("tick_after_decimal", tick_after_decimal)
  
  # # print("Leverage1", percent(float(leverage), float(balance)))
  if (float(price) > 0):
    TRADE_QUANTITY = truncate((float(leverage) * float(balance)) / float(price), tick_after_decimal)
    # # print("percent(float(STOP_PRICE_PERC) {}, float(price))) {}", percent(float(STOP_PRICE_PERC), float(price)))
    # # print("TRADE_QUANTITY", TRADE_QUANTITY)
    STOP_PRICE = truncate(float(price) - percent(float(STOP_PRICE_PERC), float(price)), tick_after_decimal)   
    # # print("STOP_PRICE", STOP_PRICE)
      
    if "submit-buy" == ctx.triggered_id:
    #   #  put binance buy logic here
      order_succeeded = order(
        symbol,
        "BUY",
        type_order,
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
      # # print("Buy! Buy! Buy!")
    elif "submit-sell" == ctx.triggered_id:
      #  put binance sell logic here
      order_succeeded = order(
        symbol,
        "SELL",
        type_order,
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
      # # print("Sell! Sell! Sell!")
    
  # # print("Response:", msg)
    
  return msg


@app.callback(
    Output("timer_display", "children"),
    Input("interval-component", "n_intervals"),
)

def update_interval(n_intervals):
  if not n_intervals:
      raise PreventUpdate
  
  # print("4 CALLBACK EVENT:", ctx.triggered_id)
  # current_time = timer.time()
  current_time = datetime.now().time()
 
  # # print(current_time.strftime('%H-%M-%S'))
  
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
  
  # # print(levels_df)
  return levels_df

@app.callback(
  Output("bid_table", "data"),
  Output("bid_table", "style_data_conditional"),
  Output("ask_table", "data"),
  Output("ask_table", "style_data_conditional"),
  Output("mid-price", "children"),
  Output("price-to-submit", "value"),
  Output("symbol-bet", "value"),
  Input("aggregation-level", "value"),
  State("quantity-precision", "value"),
  State("price-precision", "value"),
  State("pair-select", "value"),
  Input("timer-update-order-book", "n_intervals"),
  # State("interval-component", "n_intervals"),
)

def update_orderbook(agg_level, quantity_precision, price_precision, symbol, n_intervals):
  # if n_intervals < 1 or ctx.triggered_id != "timer-update-order-book" or ctx.triggered_id != "aggregation-level":
  #   raise PreventUpdate
  if ctx.triggered_id == "timer-update-order-book" or ctx.triggered_id != "aggregation-level":
    
    print("5 CALLBACK EVENT:", ctx.triggered_id)
    
    print("UPDATE ORDER BOOK")
    # print("update_orderbook {} {}  {} {} {}".format(agg_level, quantity_precision, price_precision, symbol, n_intervals))
    # url = "https://api.binance.com/api/v3/depth"
    url = "https://fapi.binance.com/fapi/v1/depth"
    
    levels_to_show = 10
    
    params = {
      "symbol":symbol.upper(),
      "limit":"100",
    }
    
    data = requests.get(url, params=params).json()
    
    pre_data = pd.DataFrame(data["bids"], columns=["price","quantity"])
    # print("PRE DATA price", pre_data.price)
    price_after_decimal = str(pre_data.price.iloc[0])[::-1].find('.')
    # print("price_after_decimal", price_after_decimal)
    quantity_after_decimal = price_after_decimal  #str(pre_data.quantity.iloc[0])[::-1].find('.')
    # print("quantity_after_decimal", quantity_after_decimal)
    try:
      bid_df = pd.DataFrame(data["bids"], columns=["price","quantity"], dtype =float)
      ask_df = pd.DataFrame(data["asks"], columns=["price","quantity"], dtype =float)
      
    #  Middle Price
      # price_after_decimal = str(bid_df.price.iloc[0])[::-1].find('.')
      mid_price = (bid_df.price.iloc[0] + ask_df.price.iloc[0])/2
      # # print("Largest BID: " ,bid_df.price.iloc[0])
      # print("Smallest ASK: " ,ask_df.price.iloc[0])
      mid_price_precision = int(price_after_decimal)
      mid_price = f"%.{mid_price_precision}f" % mid_price 
      
      # Bids
      bid_df = aggregate_levels(bid_df, agg_level = Decimal(agg_level), side = "bid")
      bid_df = bid_df.sort_values("price", ascending = False) 
      
      # Asks
      ask_df = aggregate_levels(ask_df, agg_level = Decimal(agg_level), side = "ask")
      ask_df = ask_df.sort_values("price", ascending = False) 
    
      bid_df = bid_df.iloc[:levels_to_show]
      ask_df = ask_df.iloc[-levels_to_show:]
      
      # quantity_precision[::-1].find('.') # np.format_float_positional(quantity_precision, trim='-')
      quantity_after_decimal = price_after_decimal 
      # quantity_after_decimal = str(quantity_precision)[::-1].find('.')
      bid_df.quantity = bid_df.quantity.apply(
        lambda x: f"%.{quantity_after_decimal}f" % x)
      
      # price_precision = np.format_float_positional(price_precision, trim='-')
      # price_after_decimal = str(price_precision)[::-1].find('.')
      bid_df.price = bid_df.price.apply(
        lambda x: f"%.{price_after_decimal}f" % x)
        
      ask_df.quantity = ask_df.quantity.apply(
        lambda x: f"%.{quantity_after_decimal}f" % x)
      
      ask_df.price = ask_df.price.apply(
        lambda x: f"%.{price_after_decimal}f" % x)
    except Exception as e:
        # print("an exception occured - {}".format(e))
        return e.message
      
    return (bid_df.to_dict("records"), table_styling(bid_df, "bid"),  
            ask_df.to_dict("records"),  table_styling(ask_df, "ask"), mid_price, mid_price, symbol)
  elif n_intervals <= 1:
     raise PreventUpdate
  pass


if __name__ == "__main__":
  app.run_server(debug=True)
