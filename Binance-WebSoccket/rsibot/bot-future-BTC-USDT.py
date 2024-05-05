import os
import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np
import math
import logging
import sys
from datetime import datetime, timezone, timedelta
import time
import threading
import signal
# import ccxt

# ANSI escape codes for moving cursor
move_up = '\x1b[1A'  # Move cursor up one line
move_down = '\x1b[1B'  # Move cursor down one line
clear_line = '\x1b[2K'  # Clear the entire line

def calculate_percentage_positive_negative(positive_value, negative_value):
    absolute_positive = abs(positive_value)
    absolute_negative = abs(negative_value)
    
    total_change = absolute_positive + absolute_negative
    if absolute_positive > 0:
        percentage_change = (total_change / absolute_positive) * 100
    else:
        percentage_change = 0
    
    if positive_value - abs(negative_value) > 0:
        return percentage_change
    else:
        return -1 * percentage_change

def calculate_percentage_change(old_value, new_value):
    if old_value > 0:
        return round(float(((new_value - old_value) / old_value) * 100), DECIMAL_CALC)
    else:
        return 0

def average_percentage_growth(arr):
    percentage_growths = []
    for i in range(len(arr) - 1):
        growth = ((arr[i+1] - arr[i]) / arr[i]) * 100
        percentage_growths.append(growth)
    if percentage_growths > 0:    
        return sum(percentage_growths) / len(percentage_growths)
    else:
        return 0

class LastFiveStack():
    def __init__(self, stack_size):
        self.stack_size = stack_size
        self.stack = []

    def restart(self):
        self.stack = []
        
    def push(self, value):
        if len(self.stack) >= self.stack_size:
            self.pop_until(value)
        else:
            self.insert_sorted(value)

    def insert_sorted(self, value):
        index = 0
        while index < len(self.stack) and self.stack[index] < value:
            index += 1
        self.stack.insert(index, value)

    def pop_until(self, value):
        while self.stack and self.stack[-1] < value and len(self.stack) >= self.stack_size:
            self.stack.pop()
        self.insert_sorted(value)

    def get_values(self):
        return self.stack

    def get_size(self):
        return len(self.stack)
    
    def average_percentage_growth(self):
        if len(self.stack) < 2:
            return 0  # If there's not enough data, return 0 or handle it accordingly
        percentage_growths = []
        count = 0  # Count of valid growth calculations
        for i in range(len(self.stack) - 1):
            if self.stack[i] == 0:
                continue  # Skip calculation if the denominator is zero
            growth = ((self.stack[i+1] - self.stack[i]) / self.stack[i]) * 100
            percentage_growths.append(growth)
            count += 1
            
        if count == 0:
            return 0  # If there were no valid growth calculations, return 0    
        return round(float(sum(percentage_growths) / len(percentage_growths)), DECIMAL_CALC) 

def aware_cetnow():
    # return datetime.now(timezone.utc) # uct
    return datetime.now(tz=timezone(timedelta(hours=2)))

def loggin_setup(filename):
  log_filename = filename.lower() + "_" + str(initial_procces_date.strftime('%d %m %Y %H:%M:%S')).replace(' ','_').replace(':','-') + '.log'
#   log_filename = filename.lower() + "_" + initial_procces_date.replace(' ','_').replace(':','-') + '.log'
  os.makedirs(os.path.dirname(log_filename), exist_ok=True)
  logging.basicConfig(filename=log_filename, format='%(levelname)s | %(asctime)s | %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p', level=logging.DEBUG)

  formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

  logging.getLogger().setLevel(logging.INFO)
  
  # Console Logging
#   stdout_handler = logging.StreamHandler(sys.stdout)
#   stdout_handler.setLevel(logging.DEBUG)
#   stdout_handler.setFormatter(formatter)

#   logging.getLogger().addHandler(stdout_handler)

  logging.info('Initialization Logging')
  # logger.error('This is an error message.')

def print_file_status_name(lines):
  os.makedirs(os.path.dirname(profit_stat_filename), exist_ok=True)
  with open(profit_stat_filename, "w") as f:
      # Redirect print output to the file
      print(lines, file=f)


# Flag to indicate if threads should stop
should_stop = False
initial_procces_date = aware_cetnow()
# PROFIT_SELL = 1.0006
# LOSS_SELL = 0.9995
trail_percent = 2    # Trailing stop percentage (2% in this example)
RSI_PERIOD = 14
RSI_OVERBOUGHT = 80
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
TRADE_TYPE = "FUTURE"

profit_stat_filename = "./daily/profit_status_{}_{}".format(TRADE_TYPE, TRADE_SYMBOL) + "_" + str(initial_procces_date.strftime('%d %m %Y %H:%M:%S')).replace(' ','_').replace(':','-') + '.md'
# profit_stat_filename = "./daily/profit_status_{}".format(TRADE_SYMBOL) + "_" + initial_procces_date.replace(' ','_').replace(':','-') + '.md'

# Decimals
DECIMAL_CALC = 2
DECIMAL_BTCUSDT = 2 # BTC

VOLUME_DEC = 5
# QTY_BUY = 10 # USDT
# QTY_BUY = 0.002 # USDT 0.005
QTY_BUY = 0.05 # USDT 0.005
# quoteOrderQty = #  7   USDT  SPOT
# QTY_BUY = 0.00014
QTY_SELL = 1000 # It Forces to Sell 100%
ONLY_BY_WHEN = 41180
ByPass = True
BLOCK_ORDER = True

ACTION_BUY = True
ATTEMPT_RATIO = 0.00005

ROI_PROFIT = 0.15
ROI_STOP_LOSS = -0.10
TRADE_LEVERAGE = 75

# PERCENTAGE AVARAGE BETWEEN TWO NUMBERS (MORE INTELIGENTTELY)
ROI_PERC_GROWS = 20 
ROI_PERC_ATTEMPTS = 1
ROI_PERC_MAX_ATTEMPTS = 4

# PERCENTAGE AVARAGE GROWS FOR ALL ITEMS OF THE ARRAY
ROI_AVG_GROWS = 5 
ROI_AVG_GROWS_ATTEMPTS = 1
ROI_AVG_MAX_ATTEMPTS = 4

roi_stack_size = 6
sorted_roi = LastFiveStack(roi_stack_size)
sorted_roi.push(ROI_PROFIT)


sorted_last_profits_buy = LastFiveStack(10)
sorted_last_losses_buy = LastFiveStack(10)

sorted_last_profits_sell = LastFiveStack(10)
sorted_last_losses_sell = LastFiveStack(10)

# PRECISION_PROFIT_LOSS = 7 # CFXUSDT
PRECISION_PROFIT_LOSS = 1 # BTCUSDT

BUY_PROFIT_CALC = 1.005   # BTCUSDT
BUY_LOSS_CALC = 0.99913     # BTCUSDT

SELL_PROFIT_CALC = 1.005   # BTCUSDT
SELL_LOSS_CALC = 0.99913     # BTCUSDT

PROFITS = {}
PROFITS["WHEN_BUY"] = 0
PROFITS["WHEN_SELL"] = 0
# PROFITS["TRAIL_STOP_PRICE_BUY"] = 0
PROFITS["TRAIL_LAST_ROI_BUY"] = 0
PROFITS["TRAIL_STOP_ROI_BUY"] = 0
LOSSES = {}
LOSSES["WHEN_BUY"] = 0
LOSSES["WHEN_SELL"] = 0
LOSSES["TRAILING_STOP_BUY"] = 0
LOSSES["TRAILING_STOP_SELL"] = 0

pnlProfitBuy = 0
roiProfitBuy = 0
pnlLossBuy = 0
roiLossBuy = 0

curr_roiProfitBuy = 0
curr_roiProfitSell = 0

curr_pnlProfitBuy = 0
curr_pnlProfitSell = 0
        
pnlProfitSell = 0
roiProfitSell = 0
pnlLossSell = 0
roiLossSell = 0


logger = logging.getLogger()
loggin_setup("./logs/bot_A_{}_{}_mcda_rsi".format(TRADE_TYPE, TRADE_SYMBOL))

closes = []
in_position = False

# futures_entry_price = 39570.01 
futures_entry_price = 0
spot_entry_price = 0
# forceSell = 39800.94000000

SINAIS = {}
SINAIS["BUY_HIST"] = 0 
SINAIS["SELL_HIST"] = 0 
SINAIS["BUY_VOL_INC"] = 0 
SINAIS["SELL_VOL_DEC"] = 0 
SINAIS["BUY_VOL_IMB"] = 0 
SINAIS["SELL_VOL_IMB"] = 0 
SINAIS["MSG_1"] = "NEUTRAL" 
SINAIS["MSG_2"] = "NEUTRAL" 
SINAIS["MSG_3"] = "NEUTRAL" 
SINAIS["ENTRY_POINT"] = "" 
SINAIS["LAST_SMA"] = 0
SINAIS["LAST_RSI"] = 0

TOTALS = {}
TOTALS['TOTAL_PROFITS_BUY'] = 0 
TOTALS['TOTAL_LOSSES_BUY']= 0
TOTALS['TOTAL_PROFITS_SELL'] = 0
TOTALS['TOTAL_LOSSES_SELL'] = 0
TOTALS['COUNT_PROFITS_BUY'] = 0
TOTALS['COUNT_PROFITS_SELL'] = 0
TOTALS['COUNT_LOSSES_BUY'] = 0
TOTALS['COUNT_LOSSES_SELL'] = 0


# Initialize DataFrame for keeping track of historical data
historical_data = []
timeframe = '1m'  # adjust timeframe as needed

# Parameters for moving averages
short_window = 20
long_window = 50

# Initialize variables
previous_volume = None

# Parameters to Calculate Buy using Volume
volume_threshold_buy = 1.5  # Threshold for volume increase, e.g., volume doubled

# Parameters to Calculate Sell using Volume
volume_threshold_sell = 0.5  # Threshold for volume decrease, e.g., volume halved


# Calculate Signal Base on Depth
# Parameters
imbalance_threshold = 0.8  # Threshold for order book imbalance, e.g., 80% buy orders
volume_threshold_depth = 100  # Minimum volume for a significant buy order


client = Client(config.API_KEY, config.API_SECRET) #, tld='us'
# exchange = ccxt.binance({'apiKey': config.API_KEY, 'secret': config.API_SECRET})

# params = {'fromAsset': 'BTCUSDT', 'toAsset': 'USDT', 'fromAmount': 10000, 'recvWindow': 60000}
# response = exchange.sapi_post_convert_getquote(params)
# print("Direct Trade {}".format(response.status))

def calculate_by_volume(current_volume, previous_volume):
    if previous_volume is not None:
        # Check for buy signal based on volume increase
        # logger.info("Current Volume: {} / Previous Volume {}".format(current_volume, previous_volume))
        if previous_volume > 0 and current_volume > 0: 
            volume_increase = current_volume / previous_volume

            # logger.info("Previous Volume: {} / Current Volume: {}".format(previous_volume, current_volume))
            volume_decrease = previous_volume / current_volume
            if volume_increase >= volume_threshold_buy:
                SINAIS["BUY_VOL_INC"] = SINAIS["BUY_VOL_INC"]  + 1 
                SINAIS["MSG_2"] = "Volume INCREASED !  Buy signal detected!"
                # print("Volume increased significantly!  Buy signal detected! ")
                # print("Volume increased significantly!  Buy signal detected! ")
                # print("Volume increased significantly!  Buy signal detected! ")
                # print("Volume increased significantly!  Buy signal detected! ")
                
            # Check for sell signal based on volume decrease
            elif volume_decrease >= volume_threshold_sell:
                SINAIS["SELL_VOL_DEC"] = SINAIS["SELL_VOL_DEC"] + 1  
                SINAIS["MSG_2"] = "Volume DECREASED !  Sell signal detected"
                # print("Volume decreased significantly!  Sell signal detected!")
                # print("Volume decreased significantly!  Sell signal detected!")
                # print("Volume decreased significantly!  Sell signal detected!")
                # print("Volume decreased significantly!  Sell signal detected!")
         
    # Update previous volume
    return current_volume

def calculate_signal_by_historical(close):
    historical_data.append(close) # -> current_close
    if len(historical_data) > long_window:
        # Calculate moving averages
        short_ma = pd.Series(historical_data).rolling(window=short_window, min_periods=1).mean().iloc[-1]
        long_ma = pd.Series(historical_data).rolling(window=long_window, min_periods=1).mean().iloc[-1]
        # Check for sell signal
        if short_ma < long_ma:
            SINAIS["SELL_HIST"] = 1 
            SINAIS["BUY_HIST"] = 0
            SINAIS["MSG_1"] = "SELL SIGNAL"  
            # print("Sell signal detected! Sell signal detected!")
        if short_ma > long_ma:
            SINAIS["BUY_HIST"] = 1 
            SINAIS["SELL_HIST"] = 0 
            SINAIS["MSG_1"] = "BUY  SIGNAL"  
            # print("Buy signal detected! Buy signal detected!")
        if short_ma == long_ma:
            SINAIS["BUY_HIST"] = 0
            SINAIS["SELL_HIST"] = 0 
            SINAIS["MSG_1"] = "NEUTRAL"  
            # print("Buy signal detected! Buy signal detected!")
      
      
# FUTURES
def order_future_cancel_all_open_order(symbol):
    try:
        # logger.info("Cancel All open Orders / Closing All  {} ".format( symbol))
        # cleardualSidePosition='false', 
        order = client.futures_cancel_all_open_orders(symbol=symbol, 
                                            timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            recvWindow = 60000)
        # logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order     

# FUTURES
def order_future_create_order(side, symbol, quantity, positionSide, order_type):
    try:
        logger.info("FUTURES sending order  SIDE {} QTD {} ".format( side, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide,  
                                            type=order_type, 
                                            quantity=quantity, 
                                            recvWindow = 60000)
        logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order

# FUTURES
def order_future_cancel_REDUCE_only(side, symbol, quantity, positionSide, order_type):
    try:
        logger.info("reduce 100% Cancel Order / Closing Order  {} QTY {} ".format(symbol, quantity))
        # dualSidePosition='false', 
        order = client.futures_create_order(side=side, 
                                            symbol=symbol,
                                            quantity=quantity,
                                            positionSide='BOTH',  
                                            type='MARKET', 
                                            reduceOnly=True, 
                                            recvWindow = 60000)        
        logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return order

# SPOT
def order_spot(side, symbol, quoteOrderQty, order_type):
    try:
        logger.info("sending order  SIDE {} QTY {} ".format( side, quoteOrderQty ))
        order = client.create_order(symbol=symbol, side=side, type=order_type, quoteOrderQty=quoteOrderQty, recvWindow = 60000)
        logger.info(order)
        return order
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
    return False

def order_sell(side, symbol, quantity, order_type, soldDesc, attemptRatio):
    try:
        logger.info("sending order  SIDE {} QTY {} SOLD MOTIVE: {}".format(side, quantity , soldDesc))
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
        logger.info(order)
    except Exception as e:
        logger.info("an exception occured - {}".format(e))
        order = False
        while str(e).find("Account has insufficient balance for requested") >= 0 and not order:
            quantity -= attemptRatio
            # quantity = math.trunc(quantity) 
            logger.info("Attempt to SELL {}".format(round(quantity, VOLUME_DEC)))
            order = order_sell(side, symbol, quantity , order_type, soldDesc, attemptRatio)    
    return order

def get_current_price_futures(symbol):
    ticker = client.futures_symbol_ticker(symbol=symbol)
    # date = datetime(ticker['time'])
    # ticker['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ticker['time']))
    # logger.info("TICKER {}".format(ticker))
    return ticker


def calculate_pnl_futures(entry_price, exit_price, quantity, action_buy):
    
    if action_buy:
        pnl = (exit_price - entry_price) * quantity
    elif not action_buy:
        pnl = (entry_price - exit_price) * quantity
    else:
        raise ValueError("Invalid side provided")
    
    if action_buy:
        logger.info("TRADE BUY  Entry Price {} Exit Price {} QTD {} PNL {}".format(entry_price, exit_price, quantity, round(pnl, DECIMAL_CALC)))
    if not action_buy:
        logger.info("TRADE SELL Entry Price {} Exit Price {} QTD {} PNL {}".format(entry_price, exit_price, quantity, round(pnl, DECIMAL_CALC)))

    
    # if action_buy:
    #     logger.info("BUY  PNL Calc Entry: {}   Current: {}   QTY {}  PNL {}".format(entry_price, exit_price, quantity, pnl))
    # if not action_buy:    
    #     logger.info("SELL PNL Calc Entry: {}   Current: {}   QTY {}  PNL {}".format(entry_price, exit_price, quantity, pnl))
    
    
    return round(float(pnl), DECIMAL_CALC)  

def mine_calculate_roi_with_imr(entry_price, exit_price, quantity, action_buy, imr):
    
    # Calculate the total value at entry and exit
    # total_entry_value = entry_price * quantity
    # total_exit_value = exit_price * quantity

    # logger.info("entry_price {}".format(entry_price)) 
    # logger.info("exit_price {}".format(exit_price)) 
    # logger.info("quantity {}".format(quantity)) 
    # logger.info("imr {}".format(imr)) 
    
    
    if entry_price > 0:
        roi = (((exit_price - entry_price) * imr ) / entry_price) * 100
    else:
        roi = 0    

    if action_buy:
        logger.info("TRADE BUY  Entry Price {} Exit Price {} QTD {} Leverage {} ROI {}".format(entry_price, exit_price, quantity, imr, round(roi, DECIMAL_CALC)))
    if not action_buy:
        logger.info("TRADE SELL Entry Price {} Exit Price {} QTD {} Leverage {} ROI {}".format(entry_price, exit_price, quantity, imr, round(roi, DECIMAL_CALC)))
    

    # if action_buy:
    #     logger.info("BUY  ROI Calc Entry: {}   Current: {}   QTY {}  Lev: {} ROI: {}".format(entry_price, exit_price, quantity, imr, roi))
    # if not action_buy:    
    #     logger.info("SELL ROI Calc Entry: {}   Current: {}   QTY {}  Lev: {} ROI: {}".format(exit_price, entry_price, quantity, imr, roi))
    
    
    # logger.info("FUTURES ROI {} TOTAL ENTRY {} TOTAL EXIT {} ".format( round(roi, 2), round(total_entry_value, 1), round(total_exit_value, 1)))

    # Calculate the profit or loss
    # pnl = total_exit_value - total_entry_value

    return round(float(roi), DECIMAL_CALC)

def profit_calculus(tradeType, action_buy, spot_entry_price, futures_entry_price, volume):
    # if action_buy:
    #     logger.info("{} BOUGHT PRICE: {}".format(tradeType, entry_price))

    # if not action_buy:
    #     logger.info("{} SELL   PRICE: {}".format(tradeType, entry_price))

    #Futures Prices Profit & Loss When Buy
    PROFITS["WHEN_BUY"] = round(float(futures_entry_price) * float(BUY_PROFIT_CALC), PRECISION_PROFIT_LOSS)  
    LOSSES["WHEN_BUY"] = round(float(futures_entry_price) * float(BUY_LOSS_CALC), PRECISION_PROFIT_LOSS) 
    
    # Create a Trailing Stop Profit Price Entry
    # PROFITS["TRAIL_STOP_PRICE_BUY"] = LOSSES["WHEN_BUY"] * (1 - trail_percent / 100)
    
    # Create a Trailing Stop Profit ROI Entry
    # PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT

    # Futures Prices Profit & Loss When SELl
    PROFITS["WHEN_SELL"] = round(float(futures_entry_price) / float(SELL_PROFIT_CALC), PRECISION_PROFIT_LOSS)  
    LOSSES["WHEN_SELL"] = round(float(futures_entry_price) / float(SELL_LOSS_CALC), PRECISION_PROFIT_LOSS)  


    pnlProfitBuy = calculate_pnl_futures(futures_entry_price, PROFITS["WHEN_BUY"], volume, True)
    roiProfitBuy = mine_calculate_roi_with_imr(futures_entry_price, PROFITS["WHEN_BUY"], volume, True, TRADE_LEVERAGE)
    pnlLossBuy = calculate_pnl_futures(futures_entry_price, LOSSES["WHEN_BUY"], volume, True)
    roiLossBuy = mine_calculate_roi_with_imr(futures_entry_price, LOSSES["WHEN_BUY"], volume, True, TRADE_LEVERAGE)
            
    pnlProfitSell = calculate_pnl_futures(futures_entry_price, PROFITS["WHEN_SELL"],  volume, False)
    roiProfitSell = mine_calculate_roi_with_imr(PROFITS["WHEN_SELL"], futures_entry_price, volume, False, TRADE_LEVERAGE)
    pnlLossSell = calculate_pnl_futures(futures_entry_price, LOSSES["WHEN_SELL"], volume, False)
    roiLossSell = mine_calculate_roi_with_imr(LOSSES["WHEN_SELL"], futures_entry_price, volume, False, TRADE_LEVERAGE)

    logger.info("----------------------------------            CALCULUS  ENTRY PRICE                       ----------------------------------|")
    logger.info(tradeType)
    logger.info("                                                                                                                            |")
    logger.info("FUTURE Volume {} --->  Quantity USD: {}".format(TRADE_TYPE, volume, round(futures_entry_price * volume, 2)))
    logger.info("----------------------------------------------------------------------------------------------------------------------------|")
    logger.info("  Entry Price SPOT    {}".format(float(spot_entry_price)))
    logger.info("  Entry Price FUTURES {}".format(float(futures_entry_price)))
    print_signals(True)
    logger.info("                                                                                                                            |")
    logger.info("BUY  ENTRY_PRICE {} TAKE_PROFIT_WHEN   {} ROI: {}% PNL: {}".format(futures_entry_price, PROFITS["WHEN_BUY"], roiProfitBuy, pnlProfitBuy))
    logger.info("BUY  ENTRY_PRICE {} REDUCE_LOSSES_WHEN {} ROI: {}% PNL: {}".format(futures_entry_price, LOSSES["WHEN_BUY"], roiLossBuy, pnlLossBuy))
    #logger.info("BUY  TRAILING STOP PRICE PROFIT {}".format(PROFITS["TRAIL_STOP_PRICE_BUY"]))
    logger.info("BUY  TRAILING STOP ROI PROFIT {}%".format(PROFITS["TRAIL_STOP_ROI_BUY"]))
    logger.info("BUY  TRAILING LAST ROI PROFIT {}%".format(PROFITS["TRAIL_LAST_ROI_BUY"]))
    logger.info("                                                                                                                            |")
    logger.info("SELL ENTRY_PRICE {} TAKE_PROFIT_WHEN   {} ROI: {}% PNL: {}".format(futures_entry_price, PROFITS["WHEN_SELL"], roiProfitSell, pnlProfitSell))
    logger.info("SELL ENTRY_PRICE {} REDUCE_LOSSES_WHEN {} ROI: {}% PNL: {}".format(futures_entry_price, LOSSES["WHEN_SELL"], roiLossSell, pnlLossSell))
    logger.info("                                                                                                                            |")
    logger.info("----------------------------------            TOTAL  PROFIT AND LOSS                      ----------------------------------|")
    logger.info("                                                                                                                            |")

    perc_profit = round(sorted_last_profits_buy.average_percentage_growth() - abs(sorted_last_losses_buy.average_percentage_growth()), DECIMAL_CALC)
    perc_losses = round(sorted_last_profits_sell.average_percentage_growth() - abs(sorted_last_losses_sell.average_percentage_growth()), DECIMAL_CALC)
    
    profit_buy = round(TOTALS['TOTAL_PROFITS_BUY'] -  abs(TOTALS['TOTAL_LOSSES_BUY']), DECIMAL_CALC)
    profit_sell = round(TOTALS['TOTAL_PROFITS_SELL'] - abs(TOTALS['TOTAL_LOSSES_SELL']), DECIMAL_CALC)

    last_profits_buy = round(sorted_last_profits_buy.average_percentage_growth(), DECIMAL_CALC)
    last_profits_sell = round(sorted_last_profits_sell.average_percentage_growth(), DECIMAL_CALC)

    last_losses_buy = round(sorted_last_losses_buy.average_percentage_growth(), DECIMAL_CALC)
    last_losses_sell = round(sorted_last_losses_sell.average_percentage_growth(), DECIMAL_CALC)
    
    
    logger.info("PROFITS BUY  $ {}({}% {} tt) LOSSES BUY  $ {}({}% {} tt)  {}%  TOTAL {} USDT".format(TOTALS['TOTAL_PROFITS_BUY'],  last_profits_buy,  TOTALS['COUNT_PROFITS_BUY'],  TOTALS['TOTAL_LOSSES_BUY'],  last_losses_buy,  TOTALS['COUNT_LOSSES_BUY'],   perc_profit, profit_buy))
    logger.info("PROFITS SELL $ {}({}% {} tt) LOSSES SELL $ {}({}% {} tt)  {}%  TOTAL {} USDT".format(TOTALS['TOTAL_PROFITS_SELL'], last_profits_sell, TOTALS['COUNT_PROFITS_SELL'], TOTALS['TOTAL_LOSSES_SELL'], last_losses_sell,  TOTALS['COUNT_LOSSES_SELL'], perc_losses, profit_sell))
    logger.info("                                                                                                                            |")
    logger.info(tradeType)
    logger.info("----------------------------------------------------------------------------------------------------------------------------|")   
         

def on_open(kline_ws):
    logger.info('opened connection')

def on_close(kline_ws):
    logger.info('closed connection')
  
def print_signals(entryPoint):
    if entryPoint:
        SINAIS['ENTRY_POINT'] = "  BUY: {} SELL: {} SIG: {} {} {} IMB BUY: {} IMB SELL: {} VOL BUY: {} VOL SELL: {} SMA : {} RSI: {}".format(SINAIS["BUY_HIST"], SINAIS["SELL_HIST"], SINAIS["MSG_1"], SINAIS["MSG_2"], SINAIS["MSG_3"], SINAIS["BUY_VOL_IMB"], SINAIS["SELL_VOL_IMB"], SINAIS["BUY_VOL_INC"], SINAIS["SELL_VOL_DEC"],  SINAIS["LAST_SMA"], SINAIS["LAST_RSI"]) 
         
    logger.info("  BUY: {} SELL: {} SIG: {} {} {} IMB BUY: {} IMB SELL: {} VOL BUY: {} VOL SELL: {} SMA : {} RSI: {}".format(SINAIS["BUY_HIST"], SINAIS["SELL_HIST"], SINAIS["MSG_1"], SINAIS["MSG_2"], SINAIS["MSG_3"], SINAIS["BUY_VOL_IMB"], SINAIS["SELL_VOL_IMB"], SINAIS["BUY_VOL_INC"], SINAIS["SELL_VOL_DEC"], SINAIS["LAST_SMA"], SINAIS["LAST_RSI"]))

def print_logger_results(tradeType, soldDesc, soldDesc1, curr_roiProfitBuy):
    logger.info("----------------------------------------------------------------------------------------------------------------------------|")    
    logger.info(tradeType)
    logger.info("                                                                                                                            |")
    logger.info("    " + soldDesc)                             
    logger.info("    Return on Investment (ROI): {}%".format(curr_roiProfitBuy))
    logger.info("    " + soldDesc1)
    logger.info("-----------------     ENTRY POINT SIGNALS     ------------------------------------------------------------------------------|")    
    logger.info(SINAIS['ENTRY_POINT'])
    logger.info("-----------------     CLOSE SIGNALS     ------------------------------------------------------------------------------------|")    
    print_signals(False)
    logger.info("                                                                                                                            |")
    logger.info(tradeType)
    logger.info("----------------------------------------------------------------------------------------------------------------------------|")     


def print_decisions(current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES):
    soldDesc = "Empty"
    soldDesc1 ="Empty"
    if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)): # STOP LOSS
        soldDesc = "{} STOP LOSSES LOSSES (Curr Losses ROI Buy {}% < {}%)".format(TRADE_TYPE, curr_roiProfitBuy, ROI_STOP_LOSS) 
        soldDesc1 = "Losses At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info("Reason 1") 

    if (float(current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC))) and curr_pnlProfitBuy > 0: # STOP PROFIT TRIGGERED
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Price {} <= Losses Price {}) ROI {} > 0".format(TRADE_TYPE, current_price,  LOSSES["WHEN_BUY"], curr_pnlProfitBuy)
        soldDesc1 = "Losses At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy) 
        logger.info("Reason 2") 
    
    if (float(current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC))) and curr_pnlProfitBuy < 0: # STOP LOSS TRIGGERED
        soldDesc = "{} STOP LOSSES LOSSES (Curr Price {} <= Losses Price {}) ROI {} < 0".format(TRADE_TYPE, current_price,  LOSSES["WHEN_BUY"], curr_pnlProfitBuy)
        soldDesc1 = "Losses At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy) 
        logger.info("Reason 3") 
    
    if ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and float(PROFITS["TRAIL_LAST_ROI_BUY"]) > ROI_PROFIT): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Profit ROI Buy {}% > {}%)".format(TRADE_TYPE, curr_roiProfitBuy, PROFITS["TRAIL_LAST_ROI_BUY"]) 
        soldDesc1 = "1) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info("Reason 4") 

    if ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and float(PROFITS["TRAIL_LAST_ROI_BUY"]) > ROI_PROFIT): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Profit ROI Buy {}% > Trail Last Roi Buy {}%)".format(TRADE_TYPE, curr_roiProfitBuy, PROFITS["TRAIL_LAST_ROI_BUY"]) 
        soldDesc1 = "2) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info("Reason 5") 
    
    if (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Profit ROI Buy {}% > {}%)".format(TRADE_TYPE, curr_roiProfitBuy, PROFITS["TRAIL_LAST_ROI_BUY"]) 
        soldDesc1 = "3) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info("Reason 6") 
        
    if (ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (ROI AVG GROWS ATTEMPTS {} > ROI AVG MAX ATTEMPTS {})".format(TRADE_TYPE, ROI_AVG_GROWS_ATTEMPTS, ROI_AVG_MAX_ATTEMPTS)
        soldDesc1 = "2) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info("Reason 7")     
    
    if (float(current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC))): # PROFIT
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Price {} >= Profit Price {})".format(TRADE_TYPE, current_price,  PROFITS["WHEN_BUY"])
        soldDesc1 = "4) Profits At: {} ROI: {}% PNL: {}".format(round(PROFITS["WHEN_BUY"], DECIMAL_CALC), curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info("Reason 8")
        
    return soldDesc, soldDesc1 

def print_status_negative(current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES):
    # logger.info("LOSSES {} ".format(curr_roiProfitBuy < float(ROI_STOP_LOSS)))
    logger.info("NEGATIVE")
    # logger.info("current_price {} curr_roiProfitBuy {} curr_pnlProfitBuy {} \n  ROI_PROFIT {} ROI_STOP_LOSS {} \n  PROFITS {} LOSSES {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)) 
    logger.info("current_price {} curr_roiProfitBuy {} curr_pnlProfitBuy {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)) 

def print_status_positive(current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES):
    logger.info("POSITIVE")
    logger.info("current_price {} curr_roiProfitBuy {} curr_pnlProfitBuy {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)) 

def process_kline_message(kline_ws, message):
    global closes, in_position, curr_roiProfitBuy, curr_pnlProfitBuy, curr_roiProfitSell, curr_pnlProfitSell, spot_entry_price, futures_entry_price, amountQty, volume, historical_data, previous_volume, PROFITS, LOSSES, ROI_PROFIT, ROI_STOP_LOSS, trail_percent, ROI_PERC_GROWS, ROI_PERC_ATTEMPTS, ROI_AVG_GROWS, ROI_AVG_GROWS_ATTEMPTS, sorted_roi, sorted_last_profits_buy, sorted_last_losses_buy, sorted_last_profits_sell, sorted_last_losses_sell  
    
    # df = pd.DataFrame(message, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # df.set_index('timestamp', inplace=True)
    # df['close'] = pd.to_numeric(df['close'])
    # print(df)
    
    # print(message)
    
    # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
        
    current_volume = float(candle['v'])
    
    if is_candle_closed:
  
  
        # Initialize MACD
        # if init_MACD: 
        #   macd = MACD(close=binance.fetch_ohlcv(symbol, timeframe)[-100:], window_fast=12, window_slow=26, window_sign=9)
        #   init_MACD = False

  
  
        # print("candle closed at {}".format(close))
        closes.append(float(close))
        
        if len(closes) > RSI_PERIOD:
            # Calculates Buy or Sell Based on Volume
            previous_volume = calculate_by_volume(current_volume, previous_volume)

            # Calculate Signal Base on Historical close
            calculate_signal_by_historical(close)
    
            np_closes = numpy.array(closes)
            np.set_printoptions(suppress = True)
            # print("Numpy tt: {} Closes {}".format(len(np_closes), np_closes))
        
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            sma = talib.SMA(np_closes, RSI_PERIOD)
            last_sma = sma[-1]
            
            
            
            # print("all rsis calculated so far")
            # np_rsi = numpy.array(rsi)
            # print("Numpy RSIs {}".format(rsi))
        
            last_rsi = rsi[-1]
            # print("RSI: {}                SMA: {}".format(round(last_rsi, 2), last_sma))
            
            if (TRADE_SYMBOL == 'BTCUSDT'): 
                SINAIS["LAST_SMA"] = round(last_sma, DECIMAL_BTCUSDT)
            else:
                SINAIS["LAST_SMA"] = last_sma
            
            SINAIS["LAST_RSI"] = round(last_rsi, DECIMAL_CALC)
            
            # SPOT Entry Price
            spot_current_price = float(close)
            # logger.info("SPOT   Entry Price {}".format(float(spot_current_price)))

            # FUTURE Entry
            ticker_future = get_current_price_futures(TRADE_SYMBOL)
            # logger.info("TICKER {}".format(ticker_future))
            futures_current_price = float(ticker_future['price'])
            # logger.info("{} Entry Price {}".format(TRADE_TYPE, float(futures_current_price)))
            # Get the current time
            current_time = aware_cetnow()

            # Calculate the difference
            time_difference = current_time - initial_procces_date

            # Extract specific components of the time difference
            days = time_difference.days
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Print the difference in a formatted way
            # init   = "    Initiate at: {} - cet  Run: {} days, {} hours, {} minutes, {} seconds ".format(initial_procces_date, time_difference)
            init   = "    Initiate at: {} - cet  Run: {} days, {} hours, {} minutes, {} seconds".format(str(initial_procces_date.strftime('%d %m %Y %H:%M:%S')), days, hours, minutes, seconds)
            line1  = "    SIG BUY: {} SIG SELL: {}  {}".format(SINAIS["BUY_HIST"], SINAIS["SELL_HIST"], SINAIS["MSG_1"])
            line2  = "    VOL BUY: {} VOL SELL: {}".format(SINAIS["BUY_VOL_INC"], SINAIS["SELL_VOL_DEC"] )
            line3  = "    IMB BUY: {} IMB SELL: {}  {}  {}".format(SINAIS["BUY_VOL_IMB"], SINAIS["SELL_VOL_IMB"], SINAIS["MSG_2"], SINAIS["MSG_3"])
            line4  = "    SMA : {}     RSI: {}".format(float(SINAIS["LAST_SMA"]), float(SINAIS["LAST_RSI"]))
            line5  = "    SPOT   Current Price {}".format(float(spot_current_price))
            line6  = "    FUTURE Current Price {}".format(float(futures_current_price))
            line7  = "    Return on Investment BUY  (ROI): {}%  Profit/Loss: {} USDT".format(curr_roiProfitBuy, curr_pnlProfitBuy)
            line8  = "    Return on Investment SELL (ROI): {}%  Profit/Loss: {} USDT".format(curr_roiProfitSell, float(curr_pnlProfitSell))
            
            perc_profit = round(sorted_last_profits_buy.average_percentage_growth() - abs(sorted_last_losses_buy.average_percentage_growth()), DECIMAL_CALC)
            perc_losses = round(sorted_last_profits_sell.average_percentage_growth() - abs(sorted_last_losses_sell.average_percentage_growth()), DECIMAL_CALC)
            
            profit_buy = round(TOTALS['TOTAL_PROFITS_BUY'] -  abs(TOTALS['TOTAL_LOSSES_BUY']), DECIMAL_CALC)
            profit_sell = round(TOTALS['TOTAL_PROFITS_SELL'] - abs(TOTALS['TOTAL_LOSSES_SELL']), DECIMAL_CALC)
            
            last_profits_buy = round(sorted_last_profits_buy.average_percentage_growth(), DECIMAL_CALC)
            last_profits_sell = round(sorted_last_profits_sell.average_percentage_growth(), DECIMAL_CALC)
            
            last_losses_buy = round(sorted_last_losses_buy.average_percentage_growth(), DECIMAL_CALC)
            last_losses_sell = round(sorted_last_losses_sell.average_percentage_growth(), DECIMAL_CALC)
    
            line9  = "    PROFITS BUY  $ {}({}% {} tt) LOSSES BUY  $ {}({}% {} tt)  {}%  TOTAL {} USDT".format(TOTALS['TOTAL_PROFITS_BUY'], last_profits_buy, TOTALS['COUNT_PROFITS_BUY'],    TOTALS['TOTAL_LOSSES_BUY'],  last_losses_buy,  TOTALS['COUNT_LOSSES_BUY'], perc_profit,  profit_buy)
            line10 = "    PROFITS SELL $ {}({}% {} tt) LOSSES SELL $ {}({}% {} tt)  {}%  TOTAL {} USDT".format(TOTALS['TOTAL_PROFITS_SELL'], last_profits_sell, TOTALS['COUNT_PROFITS_SELL'], TOTALS['TOTAL_LOSSES_SELL'], last_losses_sell, TOTALS['COUNT_LOSSES_SELL'], perc_losses, profit_sell)
            line11 = "    TRAILING STOP ROI  BUY {}%".format(PROFITS["TRAIL_STOP_ROI_BUY"])
            line12 = "    TRAILING LAST ROI  BUY {}%".format(PROFITS["TRAIL_LAST_ROI_BUY"])
            
            
            lines = init + "\n" + line1 +"\n" + line2 +"\n" + line3 +"\n" + line4 +"\n" + line5 +"\n" + line6 +"\n" + line7 +"\n" + line8 +"\n" + line9 +"\n" + line10 +"\n" + line11  +"\n" + line12
            
            ## Only Futures 
            if in_position:
                openPos = "    OPEN BUY {} Entry Price: {}" if ACTION_BUY else "    OPEN SELL {} Entry Price: {}"  
                # line13 = openPos.format (TRADE_SYMBOL, futures_entry_price)
                line13 = openPos.format (TRADE_SYMBOL, futures_entry_price)
                lines = lines +"\n" + line13
            
            print(lines)
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            print(move_up + clear_line, end="")
            if in_position:
                print(move_up + clear_line, end="")
            
            # Open a file in write mode
            print_file_status_name(lines)
            
            if not in_position:
                # print("RSI: {}  current Close is {}  SMA: {}".format (round(last_rsi, 2),  close, last_sma))
                buyPassWhen = "By Pass Active" if ByPass else "BUY WHEN {}".format(ONLY_BY_WHEN)  
                # logger.info("SPOT   Current Close is {}  {}  RSI: {}".format (float(spot_current_price), buyPassWhen, float(last_rsi)))
                # logger.info("FUTURE Current Close is {}  {}  RSI: {}".format (float(futures_current_price), buyPassWhen, float(last_rsi)))
            if in_position:
                
                # Stop Loss: 0.998 To near, We Don't get the Chance to have Profits
                # logger.info("SPOT:   {} Buy Price {} Volume {} Qty {} Target Profit {}  Stop Loss {} Current Price {}  RSI: {}".format (TRADE_SYMBOL, float(futures_entry_price), volume, amountQty, float(futures_entry_price * PROFIT_SELL), float(spot_entry_price * 0.995), float(spot_current_price), float(last_rsi)))
                if ACTION_BUY:
                    curr_pnlProfitBuy = calculate_pnl_futures(futures_entry_price, futures_current_price, volume, True)
                    curr_roiProfitBuy = mine_calculate_roi_with_imr(futures_entry_price, futures_current_price, volume, True, TRADE_LEVERAGE)

                    if (curr_roiProfitBuy < 0 or curr_pnlProfitBuy < 0):
                        print_status_negative(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)
                    if (curr_roiProfitBuy > 0 or curr_pnlProfitBuy > 0):
                        print_status_positive(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)

					# Triggers Low Prices
                    if (curr_roiProfitBuy < 0) or (curr_pnlProfitBuy < 0):
                        sorted_roi.restart()
                        sorted_roi.push(ROI_PROFIT)
                        logger.info("Initial Sorted ROI: {}".format(sorted_roi.get_values())) 
                        PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT     
                        PROFITS["TRAIL_LAST_ROI_BUY"] = ROI_PROFIT
                        ROI_PERC_ATTEMPTS = 0
                        ROI_AVG_GROWS_ATTEMPTS = 0
                    
                    # Trailing Stop ROI Buy
                    if curr_roiProfitBuy > float(sorted_roi.get_values()[-1]) and sorted_roi.get_size() < roi_stack_size:
                        logger.info("Trailing Stop ROI Buy: curr_roiProfitBuy {}  > ROI (Last 6) {}".format(curr_roiProfitBuy, float(sorted_roi.get_values()[-1])))
                        # sorted_roi.push(round(max(sorted_roi.get_values()[-1], curr_roiProfitBuy * (1 - trail_percent / 100)), DECIMAL_CALC))
                        PROFITS["TRAIL_STOP_ROI_BUY"] = round(max(sorted_roi.get_values()[-1], curr_roiProfitBuy * (1 - trail_percent / 100)), DECIMAL_CALC)
                        sorted_roi.push(curr_roiProfitBuy)
                        PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.get_values()[-1]
                        logger.info("ROI: {}".format(curr_roiProfitBuy))
                        logger.info("ROI (Last {}) {}".format(roi_stack_size, sorted_roi.get_values()))
                        logger.info("NEW TRAILING STOP ROI {}".format(PROFITS["TRAIL_STOP_ROI_BUY"]))
                        logger.info("NEW TRAILING LAST ROI {}".format(sorted_roi.get_values()[-1]))
                        print_signals(False)
                    else:
                        PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.get_values()[-1]
                    
                    # Condition where ROI 100% ABOVE INITIAL ROI
                    ## Verifies the AVG between Initial and Last Added above 200% triggers
                    ROIS_GROWS_CALC = calculate_percentage_change(sorted_roi.get_values()[0], sorted_roi.get_values()[-1])
                    if (ROIS_GROWS_CALC > ROI_PERC_GROWS):
                        logger.info("ROI: {}".format(curr_roiProfitBuy))
                        logger.info("ROI (Last {}) {}".format(roi_stack_size, sorted_roi.get_values()))
                        logger.info("Calculate Percentage Change: {}%  >  ROIS_GROWS_CALC {}%".format(ROIS_GROWS_CALC, ROI_PERC_GROWS))
                        logger.info("ATTEMPTS: {} ROI_PERC_GROWS {}%  ROI {}% LAST ROI {}".format(ROI_PERC_ATTEMPTS, ROI_PERC_GROWS, ROIS_GROWS_CALC, sorted_roi.get_values()[-1]))
                        print_signals(False)
                        ROI_PERC_ATTEMPTS = ROI_PERC_ATTEMPTS + 1
                        if (ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS):
                            PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.get_values()[-1]
                    
                    ## Verifies the AVG between All ROIs within the array Above 50% triggers
                    if (sorted_roi.get_size() > 1) and sorted_roi.average_percentage_growth() > ROI_AVG_GROWS:
                        logger.info("ROI: {}".format(curr_roiProfitBuy))
                        logger.info("ROI (Last {}) {}".format(roi_stack_size, sorted_roi.get_values()))
                        logger.info("Average Percentage Growth: {}%  >  ROI_AVG_GROWS {}%".format(sorted_roi.average_percentage_growth(), ROI_AVG_GROWS))
                        logger.info("ATTEMPTS: {} ROI_AVG_GROWS {} GROWS {} LAST ROI {}".format(ROI_AVG_GROWS_ATTEMPTS, ROI_AVG_GROWS, sorted_roi.average_percentage_growth(), sorted_roi.get_values()[-1]))
                        print_signals(False)
                        ROI_AVG_GROWS_ATTEMPTS = ROI_AVG_GROWS_ATTEMPTS + 1
                        if ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS:
                            PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.get_values()[-1]


                    # Stop Losses or Take Profits
                    if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) or float(futures_current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0):
                        
                        soldDesc, soldDesc1 = print_decisions(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)

                        if not BLOCK_ORDER:
                            # order_spot = order_sell(SIDE_SELL, TRADE_SYMBOL.upper(), round(volume, VOLUME_DEC), ORDER_TYPE_MARKET, soldDesc, ATTEMPT_RATIO)
                            # logger.info("SPOT Order Closed: {}".format(order_spot))
                            
                            # FUTURES CLOSE BY REDUCING 100% THE ORDER
                            order_future = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
                            order_future = order_future_cancel_all_open_order(TRADE_SYMBOL)
                            logger.info("{} Order Closed: {}".format(TRADE_TYPE, order_future))
                            
                            if order_future:
                                in_position = False
                                
                                print_logger_results("REAL TRADE", soldDesc, soldDesc1, curr_roiProfitBuy)
                                SINAIS['ENTRY_POINT'] = ""
                                
                                if curr_pnlProfitBuy >= 0:
                                    TOTALS['TOTAL_PROFITS_BUY'] += curr_pnlProfitBuy
                                    TOTALS['TOTAL_PROFITS_BUY'] = round(TOTALS['TOTAL_PROFITS_BUY'], DECIMAL_CALC)
                                    TOTALS['COUNT_PROFITS_BUY'] = TOTALS['COUNT_PROFITS_BUY'] + 1
                                    sorted_last_profits_buy.push(curr_pnlProfitBuy)
                                else:
                                    TOTALS['TOTAL_LOSSES_BUY'] -= abs(curr_pnlProfitBuy)
                                    TOTALS['TOTAL_LOSSES_BUY'] = round(TOTALS['TOTAL_LOSSES_BUY'], DECIMAL_CALC)
                                    TOTALS['COUNT_LOSSES_BUY'] = TOTALS['COUNT_LOSSES_BUY'] + 1    
                                    sorted_last_losses_buy.push(curr_pnlProfitBuy)
                                    
                                curr_roiProfitBuy = 0
                                curr_pnlProfitBuy = 0
                                ROI_PERC_ATTEMPTS = 1
                                ROI_AVG_GROWS_ATTEMPTS = 1
                            
                            
                        else:
                            
                            in_position = False
                            
                            print_logger_results("SIMULATED", soldDesc, soldDesc1, curr_roiProfitBuy)
                            SINAIS['ENTRY_POINT'] = ""
                            
                            if curr_pnlProfitBuy >= 0:
                                TOTALS['TOTAL_PROFITS_BUY'] += curr_pnlProfitBuy
                                TOTALS['TOTAL_PROFITS_BUY'] = round(TOTALS['TOTAL_PROFITS_BUY'], DECIMAL_CALC)
                                TOTALS['COUNT_PROFITS_BUY'] = TOTALS['COUNT_PROFITS_BUY'] + 1
                                sorted_last_profits_buy.push(curr_pnlProfitBuy)
                            else:
                                TOTALS['TOTAL_LOSSES_BUY'] -= abs(curr_pnlProfitBuy)
                                TOTALS['TOTAL_LOSSES_BUY'] = round(TOTALS['TOTAL_LOSSES_BUY'], DECIMAL_CALC)
                                TOTALS['COUNT_LOSSES_BUY'] = TOTALS['COUNT_LOSSES_BUY'] + 1    
                                sorted_last_losses_buy.push(curr_pnlProfitBuy)
                                
                            curr_roiProfitBuy = 0
                            curr_pnlProfitBuy = 0
                            ROI_PERC_ATTEMPTS = 1
                            ROI_AVG_GROWS_ATTEMPTS = 1
                            # logger.info("-------- SLEEP TIME  CLOSED POSITION {} seconds------------------------------------------------------------------------------|".format(SLEEP_CLOSED))    
                            # time.sleep(SLEEP_CLOSED)
                            # logger.info("-----------------------------------------------------------------------------------------------------------------------------|".format(SLEEP_CLOSED))    
                            # Forcing the Condition to read again from beggining
                            # last_rsi = RSI_OVERSOLD


                if not ACTION_BUY:        
                    curr_pnlProfitSell = calculate_pnl_futures(futures_entry_price, futures_current_price, volume, False)
                    curr_roiProfitSell = mine_calculate_roi_with_imr(futures_entry_price, futures_current_price, volume, False, TRADE_LEVERAGE)
                    
                    if (curr_roiProfitBuy < 0 or curr_pnlProfitBuy < 0):
                        print_status_negative(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)
                    if (curr_roiProfitBuy > 0 or curr_pnlProfitBuy > 0):
                        print_status_positive(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)

                
                
            if last_rsi > RSI_OVERBOUGHT:
                if in_position:

                     logger.info("Overbought! Waiting Profit Target {}  to  Sell! Sell! Sell!".format(PROFITS["WHEN_SELL"]))
                     
                     if ACTION_BUY:
                        if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) or float(futures_current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0):
                        
                            soldDesc, soldDesc1 = print_decisions(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)

                            if not BLOCK_ORDER:  
                                logger.info("Overbought! Sell! Sell! Sell!")
                                
                                # SPOT
                                # order_spot = order_sell(SIDE_SELL, TRADE_SYMBOL.upper(), round(volume, VOLUME_DEC), ORDER_TYPE_MARKET, soldDesc, ATTEMPT_RATIO)
                                # logger.info("SPOT Order Closed: {}".format(order_spot))
                                
                                order_future = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
                                order_future = order_future_cancel_all_open_order(TRADE_SYMBOL)
                                logger.info("FUTURE Order Closed: {}".format(order_future))
                                
                                
                                # FUTURES CLOSE BY REDUCING 100% THE ORDER
                                # orderFuture = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
                                # orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
                                # logger.info(orderFuture)
                                
                                if order_future:
                                    in_position = False
                                    
                                    print_logger_results("REAL TRADE",soldDesc, soldDesc1, curr_roiProfitBuy)
                                    SINAIS['ENTRY_POINT'] = ""

                                    if curr_pnlProfitBuy >= 0:
                                        TOTALS['TOTAL_PROFITS_BUY'] += curr_pnlProfitBuy
                                        TOTALS['TOTAL_PROFITS_BUY'] = round(TOTALS['TOTAL_PROFITS_BUY'], DECIMAL_CALC)
                                        TOTALS['COUNT_PROFITS_BUY'] = TOTALS['COUNT_PROFITS_BUY'] + 1
                                        sorted_last_profits_buy.push(curr_pnlProfitBuy)
                                    else:
                                        TOTALS['TOTAL_LOSSES_BUY'] -= abs(curr_pnlProfitBuy)
                                        TOTALS['TOTAL_LOSSES_BUY'] = round(TOTALS['TOTAL_LOSSES_BUY'], DECIMAL_CALC)
                                        TOTALS['COUNT_LOSSES_BUY'] = TOTALS['COUNT_LOSSES_BUY'] + 1    
                                        sorted_last_losses_buy.push(curr_pnlProfitBuy)
                                        
                                    curr_roiProfitBuy = 0
                                    curr_pnlProfitBuy = 0
                                    ROI_PERC_ATTEMPTS = 1
                                    ROI_AVG_GROWS_ATTEMPTS = 1
                                    
                                
                            else:
                                logger.info("SIMULATED Overbought! Sell! Sell! Sell!")
                                
                                in_position = False
                                
                                print_logger_results("SIMULATED", soldDesc, soldDesc1, curr_roiProfitBuy)
                                SINAIS['ENTRY_POINT'] = ""
                                
                                if curr_pnlProfitBuy >= 0:
                                    TOTALS['TOTAL_PROFITS_BUY'] += curr_pnlProfitBuy
                                    TOTALS['TOTAL_PROFITS_BUY'] = round(TOTALS['TOTAL_PROFITS_BUY'], DECIMAL_CALC)
                                    TOTALS['COUNT_PROFITS_BUY'] = TOTALS['COUNT_PROFITS_BUY'] + 1
                                    sorted_last_profits_buy.push(curr_pnlProfitBuy)
                                else:
                                    TOTALS['TOTAL_LOSSES_BUY'] -= abs(curr_pnlProfitBuy)
                                    TOTALS['TOTAL_LOSSES_BUY'] = round(TOTALS['TOTAL_LOSSES_BUY'], DECIMAL_CALC)
                                    TOTALS['COUNT_LOSSES_BUY'] = TOTALS['COUNT_LOSSES_BUY'] + 1    
                                    sorted_last_losses_buy.push(curr_pnlProfitBuy)
                                
                                curr_roiProfitBuy = 0
                                curr_pnlProfitBuy = 0
                                ROI_PERC_ATTEMPTS = 1
                                ROI_AVG_GROWS_ATTEMPTS = 1
                                    
                                    
                              
                else:
                    logger.info("It is overbought, but we don't own any. Nothing to do.")
            
            # if last_rsi < RSI_OVERSOLD and SINAIS["MSG_3"] == "BUY IMBALANCE" and SINAIS["MSG_1"] == "BUY  SIGNAL":             
            if last_rsi < RSI_OVERSOLD:             
                if in_position:
                    logger.info("It is oversold, but you already own it, nothing to do.")
                else:
                    
                    # logger.info("Oversold! Buy! Buy! Buy! QTY: {} Futures Curr. Price: {}".format(round(QTY_BUY, VOLUME_DEC), futures_current_price))
                    logger.info("Oversold! Buy! Buy! Buy! QTY: {} Spot Curr  Price: {}, Futures Curr  Price: {}".format(round(QTY_BUY, VOLUME_DEC), spot_current_price, futures_current_price))
                    
                    # put binance buy order logic here
                    if float(futures_current_price) > 0:
                        if ACTION_BUY:  
                            if not BLOCK_ORDER:
                                
                                # SPOT Volume Calc
                                # volume = QTY_BUY
                                
                                # FUTURE Volume Calc
                                # volume = round(QTY_BUY / futures_current_price, VOLUME_DEC)
                                volume = QTY_BUY
                                
                                # SPOT CREATE ORDER
                                order_spot = order_spot(SIDE_BUY, TRADE_SYMBOL.upper(), volume, ORDER_TYPE_MARKET)
                                
                                # FUTURES CANCEL ALL ORDER 
                                # order_future = order_future_cancel_all_open_order(TRADE_SYMBOL)
                                
                                # FUTURE CREATE ORDER
                                # order_future = order_future_create_order(SIDE_BUY, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
                                
                                
                                # if order_future:
                                #     # Get open futures positions
                                #     positions = client.futures_position_information(symbol=TRADE_SYMBOL, timestamp = int(time.time() * 1000), recvWindow = 60000)
                                #     # Print positions
                                #     for position in positions:
                                #         logger.info("Open futures position: {}".format(position))
                                #         futures_entry_price = float(position['entryPrice']) 
                                #         unRealizedProfit = float(position['unRealizedProfit'])
                                #         positionAmt = float(position['positionAmt'])
                                #         notional = float(position['notional'])
                                        
                                #     origQty = positionAmt
                                    
                                #     orderId = order_future['orderId']
                                #     clientOrderId = order_future['clientOrderId']
                                #     orderStatus = order_future['status']
                                #     # origQty = order_future['origQty']
                                #     logger.info("OrderId  {}  clientOrderId {} status {} origQty {} Entry Price {}".format(orderId, clientOrderId, orderStatus, origQty, futures_entry_price))  
                                    
                                #     amountQty = origQty
                                #     volume = origQty
                                    
                                if order_spot:
                                    spot_entry_price = float(order_spot['fills'][0]['price'])
                                    amountQty = float(order_spot['fills'][0]['qty'])
                                    volume = amountQty
                                        
                                    in_position = True
                                        
                                    sorted_roi.restart()
                                    sorted_roi.push(ROI_PROFIT)
                                    logger.info("Initial Sorted ROI: {}".format(sorted_roi.get_values())) 
                                    PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT     
                                    PROFITS["TRAIL_LAST_ROI_BUY"] = ROI_PROFIT
                                    ROI_PERC_ATTEMPTS = 0
                                    ROI_AVG_GROWS_ATTEMPTS = 0
                                    profit_calculus("REAL TRADE", ACTION_BUY, float(spot_entry_price), float(futures_entry_price), float(volume))
                                    # print_signals(futures_current_price, spot_current_price, True)
                                    in_position = True
                                
                                    
                                    
                            else:  # SIMULATED
                                
                                volume = QTY_BUY
                                
                                # FUTURE Volume Calc
                                # volume = round(QTY_BUY / futures_current_price, VOLUME_DEC)
                                    
                                amountQty = QTY_BUY
                                futures_entry_price = float(futures_current_price)
                                spot_entry_price = float(spot_current_price)
                                    
                                # volume = round(float(futures_current_price) * float(QTY_BUY), 2)
                                volume = amountQty
                                
                                #  if (sorted_roi.get_size() > (roi_stack_size-1) ):
                                sorted_roi.restart()
                                sorted_roi.push(ROI_PROFIT)
                                logger.info("Initial Sorted ROI: {}".format(sorted_roi.get_values())) 
                                PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT     
                                PROFITS["TRAIL_LAST_ROI_BUY"] = ROI_PROFIT
                                ROI_PERC_ATTEMPTS = 0
                                ROI_AVG_GROWS_ATTEMPTS = 0
                                profit_calculus("SIMULATED", ACTION_BUY, float(spot_entry_price), float(futures_entry_price), float(volume))
                                    
                                # print_signals(futures_current_price, spot_current_price, True)
                                in_position = True
                                
# Function to process Depth WebSocket messages
def process_depth_message(depth_ws, message):
    
     # print('received message')
    json_message = json.loads(message)
    # print(json_message)

    bids = json_message['b']
    asks = json_message['a']
    
    # Calculate total volume of buy and sell orders
    total_buy_volume = sum(float(bid[1]) for bid in bids)
    total_sell_volume = sum(float(ask[1]) for ask in asks)
    # logger.info(message)
    # for bid in bids:
    #     price, volume = float(bid[0]), float(bid[1])
    #     buy_volume += volume
    # for ask in asks:
    #     price, volume = float(ask[0]), float(ask[1])
    #     sell_volume += volume

    # Calculate Signal order book imbalance to sell
    total_volume = total_buy_volume + total_sell_volume
    if total_volume > 0:
        imbalance_sell = total_buy_volume / total_volume
    else:
        imbalance_sell = 0

    # Check for sell signal based on order book imbalance and significant buy volume
    if imbalance_sell >= imbalance_threshold and total_buy_volume >= volume_threshold_depth:
        # print("Sell signal detected! Order book imbalance:", imbalance_sell, "Total buy volume:", total_buy_volume)
        logger.info("Depth Thread: Sell signal detected! Order book imbalance SELL: {} Total buy volume: {}".format(imbalance_sell, total_buy_volume))
        SINAIS["SELL_VOL_IMB"] = SINAIS["SELL_VOL_IMB"] + 1
        SINAIS["MSG_3"] = "SELL IMBALANCE"  
         

    # Calculate Signal order book imbalance to buy
    if total_volume > 0:
        imbalance_buy = total_sell_volume / total_volume
    else:
        imbalance_buy = 0


    # Check for buy signal based on order book imbalance and significant buy volume
    if imbalance_buy >= imbalance_threshold and total_sell_volume  >= volume_threshold_depth:
        # print("Buy signal detected! Order book imbalance:", imbalance_buy, "Total buy volume:", total_buy_volume)
        logger.info("Depth Thread: Buy  signal detected! Order book imbalance BUY: {} Total buy volume: {}".format(imbalance_buy, total_sell_volume))
        SINAIS["BUY_VOL_IMB"] = SINAIS["BUY_VOL_IMB"] + 1 
        SINAIS["MSG_3"] = "BUY IMBALANCE"  
            
        

# Start WebSocket for Kline data
SOCKET_SPOT_KLINE = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL.lower())
# Start WebSocket for Depth data
SOCKET_SPOT_DEPTH = "wss://stream.binance.com:9443/ws/{}@depth".format(TRADE_SYMBOL.lower())
              
              

# Start WebSocket for Kline data
def run_kline_ws():
    global should_stop
    kline_ws = websocket.WebSocketApp(SOCKET_SPOT_KLINE, on_open=on_open, on_close=on_close, on_message=process_kline_message)
    kline_ws.run_forever()

# Start WebSocket for Depth data
def run_depth_ws():
    global should_stop
    depth_ws = websocket.WebSocketApp(SOCKET_SPOT_DEPTH, on_open=on_open, on_close=on_close, on_message=process_depth_message)
    depth_ws.run_forever()

# Create threads for each WebSocket connection
kline_thread = threading.Thread(target=run_kline_ws)
depth_thread = threading.Thread(target=run_depth_ws)

             
# Function to stop all threads
def stop_all_threads():
    global should_stop
    should_stop = True              

# Stop all threads
# Function to handle Ctrl+C
def signal_handler(signum, frame):
    print("Ctrl+C pressed, stopping threads...")
    stop_all_threads()
    sys.exit(0)
 
# Register signal handler for Ctrl+C
# Assign the new handler
signal.signal(signal.SIGINT, signal_handler)

# Start threads
kline_thread.start()
depth_thread.start()


# Wait for threads to finish
kline_thread.join()
depth_thread.join()              

              
# ws = websocket.WebSocketApp(SOCKET_SPOT, on_open=on_open, on_close=on_close, on_message=on_message)
# ws.run_forever()