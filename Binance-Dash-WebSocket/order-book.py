from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from decimal import Decimal
import pandas as pd
import requests
import math
import warnings
from datetime import datetime

warnings.simplefilter(action="ignore", category=FutureWarning)

app = Dash(external_stylesheets=[dbc.themes.CYBORG])

def dropdown_option(title, options, default_value, _id):
  
  return html.Div(children=[
    html.H2(title),
    dcc.Dropdown(options = options, value = default_value, id=_id)
    ])

app.layout = html.Div(children=[
 
 dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0),
    html.H1(id='timer_display', children=''),
 
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
                    default_value = "0.0001", _id = "aggregation-level"),
    dropdown_option("Pair", options = ["AXSUSDT", "ETHUSDT", "BTCUSDT", "BAKEUSDT", "BONKUSDT", "TIAUSDT"],
                    default_value = "AXSUSDT", _id = "pair-select"),
    dropdown_option("Quantity Precision", options = ["0", "1", "2", "3", "4", "5", "6"],
                    default_value = "3", _id = "quantity-precision"),
    dropdown_option("Price Precision", options = ["0", "1", "2", "3", "4", "5", "6"],
                    default_value = "4", _id = "price-precision"),
  ], style = {"padding-left":"100px"}),
  ], style = {"display": "flex",
              "justify-content": "center",
              "align-items": "center",
              "height":"100vh",}), 

 dcc.Interval(id="timer", interval=2000),
])

@app.callback(
    # Output('label1', 'children'),
    # Input('interval1', 'n_intervals')
    Output("timer_display", "children"),
    Input("interval-component", "n_intervals"),
)

def update_interval(n):
  
  current_time = datetime.now().time()

  
  print(current_time.strftime('%H-%M-%S'))
  
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
  Input("aggregation-level", "value"),
  Input("quantity-precision", "value"),
  Input("price-precision", "value"),
  Input("pair-select", "value"),
  Input("timer", "n_intervals"),
)


def update_orderbook(agg_level,quantity_precision, price_precision, symbol, n_intervals):
  
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
  print("Largest BID: " ,bid_df.price.iloc[0])
  # print(ask_df.price) 
  print("Smallest ASK: " ,ask_df.price.iloc[0])
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
  
  bid_df.quantity = bid_df.quantity.apply(
    lambda x: f"%.{quantity_precision}f" % x)
  
  bid_df.price = bid_df.price.apply(
    lambda x: f"%.{price_precision}f" % x)
  
  
  ask_df.quantity = ask_df.quantity.apply(
    lambda x: f"%.{quantity_precision}f" % x)
  
  ask_df.price = ask_df.price.apply(
     lambda x: f"%.{price_precision}f" % x)
    
  # print(bid_df.to_dict("records"))
  
  
  
  return (bid_df.to_dict("records"), table_styling(bid_df, "bid"),  
          ask_df.to_dict("records"),  table_styling(ask_df, "ask"), mid_price)
  pass


if __name__ == "__main__":
  app.run_server(debug=True)
