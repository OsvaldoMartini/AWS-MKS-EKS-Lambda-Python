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
    if percentage_growths:    
        return sum(percentage_growths) / len(percentage_growths)
    else:
        return 0

class RoiHistory():
    """
    Option B — Chronological ring buffer of the last `maxlen` ROI readings.
    - get_values()[0]  = oldest entry
    - get_values()[-1] = most recent entry  (use peak() for all-time high)
    - push() appends in time order; oldest is auto-dropped when full
    - peak()     = highest ROI ever seen in the buffer
    - baseline() = oldest ROI in the buffer (growth reference point)
    - average_percentage_growth() = avg growth across time-ordered samples
    """
    from collections import deque

    def __init__(self, maxlen):
        from collections import deque
        self._maxlen = maxlen
        self._data = deque(maxlen=maxlen)

    def restart(self):
        self._data.clear()

    def push(self, value):
        """Append value in chronological order. Oldest dropped when full."""
        self._data.append(value)

    def get_values(self):
        """Return list in chronological order (oldest first)."""
        return list(self._data)

    def get_size(self):
        return len(self._data)

    def peak(self):
        """Highest ROI currently in the buffer."""
        return max(self._data) if self._data else 0

    def baseline(self):
        """Oldest ROI in the buffer (used as growth reference)."""
        return self._data[0] if self._data else 0

    def average_percentage_growth(self):
        """Average % growth across chronologically ordered samples."""
        data = list(self._data)
        if len(data) < 2:
            return 0
        growths = [
            ((data[i+1] - data[i]) / data[i]) * 100
            for i in range(len(data) - 1)
            if data[i] != 0
        ]
        return round(float(sum(growths) / len(growths)), DECIMAL_CALC) if growths else 0

def aware_cetnow():
    # return datetime.now(timezone.utc) # uct
    return datetime.now(tz=timezone(timedelta(hours=2)))

def loggin_setup(filename):
    ts = initial_procces_date.strftime('%Y%m%d_%H-%M-%S')
    log_filename = filename.lower() + "_" + ts + '.log'
    log_dir = os.path.dirname(log_filename)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        fmt='%(levelname)-8s | %(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    # Silence noisy third-party loggers
    logging.getLogger("websocket").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("binance").setLevel(logging.WARNING)

    # File handler — all levels, structured lines
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Console handler — WARNING and above only (INFO goes to file only)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    logger.info(
        f"[INIT] | started={initial_procces_date.strftime('%Y-%m-%d %H:%M:%S')} "
        f"| symbol={TRADE_SYMBOL} | type={TRADE_TYPE} | leverage={TRADE_LEVERAGE}x "
        f"| qty={QTY_BUY} | rsi_period={RSI_PERIOD} | rsi_ob={RSI_OVERBOUGHT} | rsi_os={RSI_OVERSOLD} "
        f"| roi_profit={ROI_PROFIT}% | roi_stop={ROI_STOP_LOSS}% "
        f"| block_order={BLOCK_ORDER} | bypass={ByPass}"
    )

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
trail_percent = 10   # was 2 — trail stop at 10% below ROI peak
# Example: ROI peaks at 0.54% → trail stop = 0.54 * 0.90 = 0.49%
# Gives more room before exiting
RSI_PERIOD = 14
RSI_OVERBOUGHT = 55
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
ACTION_SELL = True  
USE_FUTURES_PRICE_FOR_DECISION = True   # ← ADD THIS
# True  = use futures_current_price for PNL, trailing, exit (current behavior)
# False = use spot_current_price for PNL, trailing, exit


ATTEMPT_RATIO = 0.00005

ROI_PROFIT = 0.15
# Option A — Widen stop loss (accept more risk per trade)
ROI_STOP_LOSS = -2.0   # was -1.20
# Option B — Reduce leverage (same stop, less sensitivity)
TRADE_LEVERAGE = 20    # was 75

# PERCENTAGE AVARAGE BETWEEN TWO NUMBERS (MORE INTELIGENTTELY)
ROI_PERC_GROWS = 200   # was 20 — require 3x growth before counting
ROI_PERC_ATTEMPTS = 1
ROI_PERC_MAX_ATTEMPTS = 8   # was 4 — more patience

# PERCENTAGE AVARAGE GROWS FOR ALL ITEMS OF THE ARRAY
ROI_AVG_GROWS = 50     # was 5
ROI_AVG_GROWS_ATTEMPTS = 1
ROI_AVG_MAX_ATTEMPTS = 8

roi_stack_size = 6
sorted_roi = RoiHistory(roi_stack_size)
sorted_roi.push(ROI_PROFIT)


sorted_last_profits_buy = RoiHistory(10)
sorted_last_losses_buy = RoiHistory(10)

sorted_last_profits_sell = RoiHistory(10)
sorted_last_losses_sell = RoiHistory(10)

# PRECISION_PROFIT_LOSS = 7 # CFXUSDT
PRECISION_PROFIT_LOSS = 5 # BTCUSDT 1  / SAHARAUSDT  5 

# BTCUSDT
BUY_PROFIT_CALC = 1.005   
BUY_LOSS_CALC = 0.99913     # BTCUSDT
SELL_PROFIT_CALC = 1.005   # BTCUSDT
SELL_LOSS_CALC = 0.99913     # BTCUSDT

# SAHARAUSDT
# BUY_PROFIT_CALC = 1.008   # SAHARAUSDT
# BUY_LOSS_CALC = 0.992     # SAHARAUSDT
# SELL_PROFIT_CALC = 1.008   # SAHARAUSDT
# SELL_LOSS_CALC = 0.992     # SAHARAUSDT


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
in_position_sell = False
last_close_time = None
COOLDOWN_SECONDS = 10  # don't re-enter for 30 seconds after close

# futures_entry_price = 39570.01 
futures_entry_price = 0
spot_entry_price = 0
# forceSell = 39800.94000000

# ── SHORT SIDE GLOBALS ──────────────────────────────────────────────────────
futures_entry_price_sell = 0
volume_sell = QTY_BUY
last_close_time_sell = None

PROFITS_SELL = {}
PROFITS_SELL["TRAIL_STOP_ROI_SELL"] = ROI_PROFIT
PROFITS_SELL["TRAIL_LAST_ROI_SELL"] = ROI_PROFIT
LOSSES_SELL = {}

ROI_PERC_ATTEMPTS_SELL    = 0
ROI_AVG_GROWS_ATTEMPTS_SELL = 0

sorted_roi_sell = RoiHistory(roi_stack_size)
sorted_roi_sell.push(ROI_PROFIT)
# ────────────────────────────────────────────────────────────────────────────

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
    order = False
    try:
        # logger.info("Cancel All open Orders / Closing All  {} ".format( symbol))
        # cleardualSidePosition='false', 
        order = client.futures_cancel_all_open_orders(symbol=symbol, 
                                            # timeInForce='GTC',  # GTC (Good 'Til Canceled)
                                            recvWindow = 60000)
        # logger.info(order)
    except Exception as e:
        logger.error(f"[ERROR] | fn=order_future_cancel_all | symbol={symbol} | error={e}")
    return order     

# FUTURES
def order_future_create_order(side, symbol, quantity, positionSide, order_type):
    order = False
    try:
        logger.info(f"[TRADE] | event=ORDER_SENT | mode=REAL | side={side} | symbol={symbol} | qty={quantity} | type={order_type}")
        # dualSidePosition='false', 
        order = client.futures_create_order(symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide,  
                                            type=order_type, 
                                            quantity=quantity, 
                                            recvWindow = 60000)
        logger.debug(f"[TRADE] | event=ORDER_RESPONSE | orderId={order.get('orderId')} | status={order.get('status')}")
    except Exception as e:
        logger.error(f"[ERROR] | fn=order_future_create | side={side} | symbol={symbol} | qty={quantity} | error={e}")
    return order

# FUTURES
def order_future_cancel_REDUCE_only(side, symbol, quantity, positionSide, order_type):
    order= False
    try:
        logger.info(f"[TRADE] | event=REDUCE_CLOSE | symbol={symbol} | qty={quantity} | side={side}")
        # dualSidePosition='false', 
        order = client.futures_create_order(side=side, 
                                            symbol=symbol,
                                            quantity=quantity,
                                            positionSide='BOTH',  
                                            type='MARKET', 
                                            reduceOnly=True, 
                                            recvWindow = 60000)        
        logger.debug(f"[TRADE] | event=ORDER_RESPONSE | orderId={order.get('orderId')} | status={order.get('status')}")
    except Exception as e:
        logger.error(f"[ERROR] | fn=order_future_reduce | symbol={symbol} | qty={quantity} | error={e}")
    return order

# SPOT
def order_spot(side, symbol, quoteOrderQty, order_type):
    try:
        logger.info(f"[TRADE] | event=ORDER_SENT | mode=REAL | side={side} | symbol={symbol} | qty={quoteOrderQty} | type={order_type}")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quoteOrderQty=quoteOrderQty, recvWindow = 60000)
        logger.debug(f"[TRADE] | event=ORDER_RESPONSE | orderId={order.get('orderId')} | status={order.get('status')}")
        return order
    except Exception as e:
        logger.error(f"[ERROR] | fn=order_spot | side={side} | symbol={symbol} | qty={quoteOrderQty} | error={e}")
    return False

def order_sell(side, symbol, quantity, order_type, soldDesc, attemptRatio):
    order= False
    try:
        logger.info(f"[TRADE] | event=ORDER_SENT | mode=REAL | side={side} | symbol={symbol} | qty={quantity} | reason={soldDesc}")
        order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow = 60000)
        logger.debug(f"[TRADE] | event=ORDER_RESPONSE | orderId={order.get('orderId')} | status={order.get('status')}")
    except Exception as e:
        logger.error(f"[ERROR] | fn=order_sell | side={side} | symbol={symbol} | qty={quantity} | error={e}")
        order = False
        MAX_RETRIES = 10
        attempt = 0
        while "insufficient balance" in str(e).lower() and not order and attempt < MAX_RETRIES:
            attempt += 1
            quantity -= attemptRatio
            if quantity <= 0:
                logger.error(f"[ERROR] | fn=order_sell | qty_exhausted | attempt={attempt}")
                break
            logger.warning(f"[TRADE] | event=ORDER_RETRY | side={side} | qty={round(quantity, VOLUME_DEC)} | attempt={attempt}")
            try:
                order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type, recvWindow=60000)
            except Exception as retry_e:
                e = retry_e  # update e so the while condition re-evaluates correctly
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
    
    side = "BUY" if action_buy else "SELL"
    logger.debug(f"[PNL] | side={side} | entry={entry_price:.2f} | exit={exit_price:.2f} | qty={quantity} | pnl={round(pnl, DECIMAL_CALC)}")
    
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

    side = "BUY" if action_buy else "SELL"
    logger.debug(f"[PNL] | side={side} | entry={entry_price:.2f} | exit={exit_price:.2f} | qty={quantity} | leverage={imr}x | roi={round(roi, DECIMAL_CALC)}%")
    
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

    # Position opened — one structured line with full entry context
    side = "BUY" if action_buy else "SELL"
    logger.info(
        f"[TRADE] | event=OPEN | mode={tradeType} | side={side} | symbol={TRADE_SYMBOL} "
        f"| spot_entry={float(spot_entry_price):.2f} | futures_entry={float(futures_entry_price):.2f} "
        f"| qty={volume} | notional={round(futures_entry_price * volume, 2)} USDT"
    )
    logger.info(
        f"[TRADE] | event=TARGETS | side=BUY "
        f"| take_profit={PROFITS['WHEN_BUY']} (roi={roiProfitBuy}% pnl={pnlProfitBuy}) "
        f"| stop_loss={LOSSES['WHEN_BUY']} (roi={roiLossBuy}% pnl={pnlLossBuy}) "
        f"| trail_stop_roi={PROFITS['TRAIL_STOP_ROI_BUY']}% | trail_last_roi={PROFITS['TRAIL_LAST_ROI_BUY']}%"
    )
    logger.info(
        f"[TRADE] | event=TARGETS | side=SELL "
        f"| take_profit={PROFITS['WHEN_SELL']} (roi={roiProfitSell}% pnl={pnlProfitSell}) "
        f"| stop_loss={LOSSES['WHEN_SELL']} (roi={roiLossSell}% pnl={pnlLossSell})"
    )
    print_signals(True)

    perc_profit = round(sorted_last_profits_buy.average_percentage_growth() - abs(sorted_last_losses_buy.average_percentage_growth()), DECIMAL_CALC)
    perc_losses = round(sorted_last_profits_sell.average_percentage_growth() - abs(sorted_last_losses_sell.average_percentage_growth()), DECIMAL_CALC)
    
    profit_buy = round(TOTALS['TOTAL_PROFITS_BUY'] -  abs(TOTALS['TOTAL_LOSSES_BUY']), DECIMAL_CALC)
    profit_sell = round(TOTALS['TOTAL_PROFITS_SELL'] - abs(TOTALS['TOTAL_LOSSES_SELL']), DECIMAL_CALC)

    last_profits_buy = round(sorted_last_profits_buy.average_percentage_growth(), DECIMAL_CALC)
    last_profits_sell = round(sorted_last_profits_sell.average_percentage_growth(), DECIMAL_CALC)

    last_losses_buy = round(sorted_last_losses_buy.average_percentage_growth(), DECIMAL_CALC)
    last_losses_sell = round(sorted_last_losses_sell.average_percentage_growth(), DECIMAL_CALC)
    
    
    logger.info(
        f"[TOTALS] | "
        f"buy_profit={TOTALS['TOTAL_PROFITS_BUY']:.2f} | buy_profit_count={TOTALS['COUNT_PROFITS_BUY']} | "
        f"buy_loss={TOTALS['TOTAL_LOSSES_BUY']:.2f} | buy_loss_count={TOTALS['COUNT_LOSSES_BUY']} | "
        f"buy_net={profit_buy:.2f} | "
        f"sell_profit={TOTALS['TOTAL_PROFITS_SELL']:.2f} | sell_profit_count={TOTALS['COUNT_PROFITS_SELL']} | "
        f"sell_loss={TOTALS['TOTAL_LOSSES_SELL']:.2f} | sell_loss_count={TOTALS['COUNT_LOSSES_SELL']} | "
        f"sell_net={profit_sell:.2f} | session_net={round(profit_buy + profit_sell, DECIMAL_CALC):.2f} USDT"
    )   
         

def on_open(kline_ws):
    logger.info("[WS] | event=OPEN | stream=kline")

def on_close(kline_ws):
    logger.warning("[WS] | event=CLOSED | stream=kline")
  
def print_signals(entryPoint):
    snapshot = (
        f"[SIGNAL] | point={'ENTRY' if entryPoint else 'CLOSE'} "
        f"| buy_hist={SINAIS['BUY_HIST']} | sell_hist={SINAIS['SELL_HIST']} "
        f"| hist_sig={SINAIS['MSG_1']} | vol_sig={SINAIS['MSG_2']} | depth_sig={SINAIS['MSG_3']} "
        f"| buy_imb={SINAIS['BUY_VOL_IMB']} | sell_imb={SINAIS['SELL_VOL_IMB']} "
        f"| buy_vol={SINAIS['BUY_VOL_INC']} | sell_vol={SINAIS['SELL_VOL_DEC']} "
        f"| sma={SINAIS['LAST_SMA']} | rsi={SINAIS['LAST_RSI']}"
    )
    if entryPoint:
        SINAIS['ENTRY_POINT'] = snapshot
    logger.info(snapshot)
    
def print_logger_results(tradeType, soldDesc, soldDesc1, curr_roiProfitBuy):
    outcome = "PROFIT" if curr_roiProfitBuy >= 0 else "LOSS"
    logger.info(
        f"[TRADE] | event=CLOSE | mode={tradeType} | outcome={outcome} "
        f"| roi={curr_roiProfitBuy}% | reason={soldDesc} | detail={soldDesc1}"
    )
    logger.info(f"[SIGNAL] | point=ENTRY_SNAPSHOT | {SINAIS['ENTRY_POINT']}")
    print_signals(False)    

def print_decisions(current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES):
    soldDesc = "Empty"
    soldDesc1 ="Empty"
    if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)): # STOP LOSS
        soldDesc = "{} STOP LOSS (roi={}% <= stop={}%)".format(TRADE_TYPE, curr_roiProfitBuy, ROI_STOP_LOSS)
        soldDesc1 = "exit_price={} roi={}% pnl={}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=STOP_LOSS | roi={curr_roiProfitBuy}% | threshold={ROI_STOP_LOSS}%")

    if (float(current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC))) and curr_pnlProfitBuy > 0: # STOP PROFIT TRIGGERED
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Price {} <= Losses Price {}) ROI {} > 0".format(TRADE_TYPE, current_price,  LOSSES["WHEN_BUY"], curr_pnlProfitBuy)
        soldDesc1 = "Losses At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy) 
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=TRAILING_PROFIT | price={current_price} | loss_price={LOSSES['WHEN_BUY']} | pnl={curr_pnlProfitBuy}")
    
    if (float(current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC))) and curr_pnlProfitBuy < 0: # STOP LOSS TRIGGERED
        soldDesc = "{} STOP LOSSES LOSSES (Curr Price {} <= Losses Price {}) ROI {} < 0".format(TRADE_TYPE, current_price,  LOSSES["WHEN_BUY"], curr_pnlProfitBuy)
        soldDesc1 = "Losses At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy) 
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=PRICE_STOP_LOSS | price={current_price} | loss_price={LOSSES['WHEN_BUY']} | pnl={curr_pnlProfitBuy}")
    
    if ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and float(PROFITS["TRAIL_LAST_ROI_BUY"]) > ROI_PROFIT): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Profit ROI Buy {}% > {}%)".format(TRADE_TYPE, curr_roiProfitBuy, PROFITS["TRAIL_LAST_ROI_BUY"]) 
        soldDesc1 = "1) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=PERC_ATTEMPTS | attempts={ROI_PERC_ATTEMPTS} | max={ROI_PERC_MAX_ATTEMPTS} | trail_roi={PROFITS['TRAIL_LAST_ROI_BUY']}%")

    if ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and float(PROFITS["TRAIL_LAST_ROI_BUY"]) > ROI_PROFIT): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Profit ROI Buy {}% > Trail Last Roi Buy {}%)".format(TRADE_TYPE, curr_roiProfitBuy, PROFITS["TRAIL_LAST_ROI_BUY"]) 
        soldDesc1 = "2) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=AVG_GROWS_ATTEMPTS | attempts={ROI_AVG_GROWS_ATTEMPTS} | max={ROI_AVG_MAX_ATTEMPTS} | trail_roi={PROFITS['TRAIL_LAST_ROI_BUY']}%")
    
    if (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Profit ROI Buy {}% > {}%)".format(TRADE_TYPE, curr_roiProfitBuy, PROFITS["TRAIL_LAST_ROI_BUY"]) 
        soldDesc1 = "3) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=TRAIL_ROI_EXCEEDED | curr_roi={curr_roiProfitBuy}% | trail_last={PROFITS['TRAIL_LAST_ROI_BUY']}%")
        
    if (curr_roiProfitBuy < float(PROFITS["TRAIL_STOP_ROI_BUY"]) and float(PROFITS["TRAIL_STOP_ROI_BUY"]) > ROI_PROFIT):
        soldDesc = "{} TRAIL STOP HIT (roi={}% < trail_stop={}%)".format(TRADE_TYPE, curr_roiProfitBuy, PROFITS["TRAIL_STOP_ROI_BUY"])
        soldDesc1 = "exit_price={} roi={}% pnl={}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=TRAIL_STOP_ROI | curr_roi={curr_roiProfitBuy}% | trail_stop={PROFITS['TRAIL_STOP_ROI_BUY']}%")    
        
    if (ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS): # PROFIT 
        soldDesc = "{} PROFIT PROFIT PROFIT (ROI AVG GROWS ATTEMPTS {} > ROI AVG MAX ATTEMPTS {})".format(TRADE_TYPE, ROI_AVG_GROWS_ATTEMPTS, ROI_AVG_MAX_ATTEMPTS)
        soldDesc1 = "2) Profits At: {} ROI: {}% PNL: {}".format(current_price, curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=AVG_MAX_ATTEMPTS | attempts={ROI_AVG_GROWS_ATTEMPTS} | max={ROI_AVG_MAX_ATTEMPTS}")
    
    if (float(current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC))): # PROFIT
        soldDesc = "{} PROFIT PROFIT PROFIT (Curr Price {} >= Profit Price {})".format(TRADE_TYPE, current_price,  PROFITS["WHEN_BUY"])
        soldDesc1 = "4) Profits At: {} ROI: {}% PNL: {}".format(round(PROFITS["WHEN_BUY"], DECIMAL_CALC), curr_roiProfitBuy, curr_pnlProfitBuy)
        logger.info(f"[TRADE] | event=EXIT_TRIGGER | reason=TAKE_PROFIT | price={current_price} | target={PROFITS['WHEN_BUY']}")

    return soldDesc, soldDesc1 

def print_status_negative(current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES):
    logger.debug(
        f"[STATUS] | direction=NEGATIVE | futures={current_price:.2f} "
        f"| roi={curr_roiProfitBuy:.2f}% | pnl={curr_pnlProfitBuy:.2f} USDT "
        f"| stop_loss_roi={ROI_STOP_LOSS}% | trail_last={PROFITS['TRAIL_LAST_ROI_BUY']}%"
    )

def print_status_positive(current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES):
    logger.debug(
        f"[STATUS] | direction=POSITIVE | futures={current_price:.2f} "
        f"| roi={curr_roiProfitBuy:.2f}% | pnl={curr_pnlProfitBuy:.2f} USDT "
        f"| trail_stop={PROFITS['TRAIL_STOP_ROI_BUY']}% | trail_last={PROFITS['TRAIL_LAST_ROI_BUY']}%"
    )

def process_kline_message(kline_ws, message):
    global closes, in_position, curr_roiProfitBuy, curr_pnlProfitBuy, curr_roiProfitSell, curr_pnlProfitSell, spot_entry_price, futures_entry_price, amountQty, volume, historical_data, previous_volume, PROFITS, LOSSES, ROI_PROFIT, ROI_STOP_LOSS, trail_percent, ROI_PERC_GROWS, ROI_PERC_ATTEMPTS, ROI_AVG_GROWS, ROI_AVG_GROWS_ATTEMPTS, sorted_roi, sorted_last_profits_buy, sorted_last_losses_buy, sorted_last_profits_sell, sorted_last_losses_sell, last_close_time, in_position_sell
    global futures_entry_price_sell, volume_sell, last_close_time_sell, PROFITS_SELL, LOSSES_SELL, ROI_PERC_ATTEMPTS_SELL, ROI_AVG_GROWS_ATTEMPTS_SELL, sorted_roi_sell
    
    # df = pd.DataFrame(message, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # df.set_index('timestamp', inplace=True)
    # df['close'] = pd.to_numeric(df['close'])
    # print(df)
    
    # print(message)
    
    # print('received message')
    try:
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
                        decision_price = futures_current_price if USE_FUTURES_PRICE_FOR_DECISION else spot_current_price
                        decision_entry = futures_entry_price   if USE_FUTURES_PRICE_FOR_DECISION else spot_entry_price
                        curr_pnlProfitBuy = calculate_pnl_futures(decision_entry, decision_price, volume, True)
                        curr_roiProfitBuy = mine_calculate_roi_with_imr(decision_entry, decision_price, volume, True, TRADE_LEVERAGE)

                        if (curr_roiProfitBuy < 0 or curr_pnlProfitBuy < 0):
                            print_status_negative(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)
                        if (curr_roiProfitBuy > 0 or curr_pnlProfitBuy > 0):
                            print_status_positive(futures_current_price, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)

                        # Triggers Low Prices
                        if (curr_roiProfitBuy < 0) or (curr_pnlProfitBuy < 0):
                            sorted_roi.restart()
                            sorted_roi.push(ROI_PROFIT)
                            logger.info(f"[TRAIL] | event=RESET | reason=negative_roi | roi={curr_roiProfitBuy}% | history={sorted_roi.get_values()}") 
                            PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT     
                            PROFITS["TRAIL_LAST_ROI_BUY"] = ROI_PROFIT
                            ROI_PERC_ATTEMPTS = 0
                            ROI_AVG_GROWS_ATTEMPTS = 0
                        
                        # Trailing Stop ROI Buy
                        if curr_roiProfitBuy > float(sorted_roi.peak()) and sorted_roi.get_size() < roi_stack_size:
                            # curr_roiProfitBuy is a new all-time high in the buffer
                            PROFITS["TRAIL_STOP_ROI_BUY"] = round(max(sorted_roi.peak(), curr_roiProfitBuy * (1 - trail_percent / 100)), DECIMAL_CALC)
                            sorted_roi.push(curr_roiProfitBuy)          # appended chronologically
                            PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.peak()  # peak() scans for max
                            logger.info(
                                f"[TRAIL] | event=NEW_HIGH | curr_roi={curr_roiProfitBuy}% "
                                f"| new_trail_stop={PROFITS['TRAIL_STOP_ROI_BUY']}% "
                                f"| new_trail_last={sorted_roi.peak()}% "
                                f"| history={sorted_roi.get_values()}"
                            )
                            print_signals(False)
                        else:
                            PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.peak()
                        
                        # Condition where ROI 100% ABOVE INITIAL ROI
                        ## Verifies the AVG between Initial and Last Added above 200% triggers
                        ROIS_GROWS_CALC = calculate_percentage_change(sorted_roi.baseline(), sorted_roi.peak())
                        if (ROIS_GROWS_CALC > ROI_PERC_GROWS):
                            logger.info(
                                    f"[TRAIL] | event=PERC_TRIGGER | curr_roi={curr_roiProfitBuy}% "
                                    f"| grows_calc={ROIS_GROWS_CALC}% | grows_threshold={ROI_PERC_GROWS}% "
                                    f"| attempts={ROI_PERC_ATTEMPTS} | max_attempts={ROI_PERC_MAX_ATTEMPTS} "
                                    f"| history={sorted_roi.get_values()}"
                            )
                            print_signals(False)
                            ROI_PERC_ATTEMPTS = ROI_PERC_ATTEMPTS + 1
                            if (ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS):
                                PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.peak()
                        
                        ## Verifies the AVG between All ROIs within the array Above 50% triggers
                        if (sorted_roi.get_size() > 1) and sorted_roi.average_percentage_growth() > ROI_AVG_GROWS:
                            logger.info(
                                f"[TRAIL] | event=AVG_TRIGGER | curr_roi={curr_roiProfitBuy}% "
                                f"| avg_growth={sorted_roi.average_percentage_growth()}% | avg_threshold={ROI_AVG_GROWS}% "
                                f"| attempts={ROI_AVG_GROWS_ATTEMPTS} | max_attempts={ROI_AVG_MAX_ATTEMPTS} "
                                f"| history={sorted_roi.get_values()}"
                            )
                            print_signals(False)
                            ROI_AVG_GROWS_ATTEMPTS = ROI_AVG_GROWS_ATTEMPTS + 1
                            if ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS:
                                PROFITS["TRAIL_LAST_ROI_BUY"] = sorted_roi.peak()


                        # Stop Losses or Take Profits
                        # if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) or float(futures_current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0):
                        # if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) or float(futures_current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or (curr_roiProfitBuy < float(PROFITS["TRAIL_STOP_ROI_BUY"]) and float(PROFITS["TRAIL_STOP_ROI_BUY"]) > ROI_PROFIT):    
                        _dp = futures_current_price if USE_FUTURES_PRICE_FOR_DECISION else spot_current_price
                        if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) \
                            or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) \
                            or float(_dp) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) \
                            or float(_dp) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) \
                            or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) \
                            or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) \
                            or (curr_roiProfitBuy < float(PROFITS["TRAIL_STOP_ROI_BUY"]) and float(PROFITS["TRAIL_STOP_ROI_BUY"]) > ROI_PROFIT):    
                            
                            soldDesc, soldDesc1 = print_decisions(_dp, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)

                            if not BLOCK_ORDER:
                                # order_spot = order_sell(SIDE_SELL, TRADE_SYMBOL.upper(), round(volume, VOLUME_DEC), ORDER_TYPE_MARKET, soldDesc, ATTEMPT_RATIO)
                                # logger.info("SPOT Order Closed: {}".format(order_spot))
                                
                                # FUTURES CLOSE BY REDUCING 100% THE ORDER
                                order_close = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
                                order_future_cancel_all_open_order(TRADE_SYMBOL)
                                logger.info(f"[TRADE] | event=ORDER_CONFIRMED | mode=REAL | type={TRADE_TYPE} | orderId={order_close.get('orderId') if isinstance(order_close, dict) else order_close}")
                                
                                if order_close:
                                    in_position = False
                                    last_close_time = aware_cetnow()  # ← ADD THIS LINE
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
                                    ROI_PERC_ATTEMPTS = 0
                                    ROI_AVG_GROWS_ATTEMPTS = 0
                                
                                
                            else:
                                
                                in_position = False
                                last_close_time = aware_cetnow()  # ← ADD THIS LINE
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
                                ROI_PERC_ATTEMPTS = 0
                                ROI_AVG_GROWS_ATTEMPTS = 0
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

                        logger.info(f"[SIGNAL] | event=OVERBOUGHT_WAIT | rsi={last_rsi:.2f} | profit_target={PROFITS['WHEN_SELL']} | curr_roi={curr_roiProfitBuy}%")
                        
                        if ACTION_BUY:
                            # if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) or float(futures_current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0):
                            # if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) or float(futures_current_price) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) or float(futures_current_price) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) or (curr_roiProfitBuy < float(PROFITS["TRAIL_STOP_ROI_BUY"]) and float(PROFITS["TRAIL_STOP_ROI_BUY"]) > ROI_PROFIT):                            
                            # Line 1012 — add _dp before the if:
                            _dp_ob = futures_current_price if USE_FUTURES_PRICE_FOR_DECISION else spot_current_price
                            if (curr_roiProfitBuy <= float(ROI_STOP_LOSS)) \
                                or (curr_roiProfitBuy > float(PROFITS["TRAIL_LAST_ROI_BUY"])) \
                                or float(_dp_ob) <= float(round(LOSSES["WHEN_BUY"], DECIMAL_CALC)) \
                                or float(_dp_ob) >= float(round(PROFITS["WHEN_BUY"], DECIMAL_CALC)) \
                                or ((ROI_PERC_ATTEMPTS > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) \
                                or ((ROI_AVG_GROWS_ATTEMPTS > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitBuy > 0) \
                                or (curr_roiProfitBuy < float(PROFITS["TRAIL_STOP_ROI_BUY"]) and float(PROFITS["TRAIL_STOP_ROI_BUY"]) > ROI_PROFIT):
                            
                                soldDesc, soldDesc1 = print_decisions(_dp_ob, curr_roiProfitBuy, curr_pnlProfitBuy, ROI_PROFIT, ROI_STOP_LOSS, PROFITS, LOSSES)

                                if not BLOCK_ORDER:  
                                    logger.info(f"[TRADE] | event=OVERBOUGHT_SELL | mode=REAL | rsi={last_rsi:.2f} | futures={futures_current_price:.2f}")
                                    
                                    # SPOT
                                    # order_spot = order_sell(SIDE_SELL, TRADE_SYMBOL.upper(), round(volume, VOLUME_DEC), ORDER_TYPE_MARKET, soldDesc, ATTEMPT_RATIO)
                                    # logger.info("SPOT Order Closed: {}".format(order_spot))
                                    
                                    order_close = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
                                    order_future_cancel_all_open_order(TRADE_SYMBOL)
                                    logger.info(f"[TRADE] | event=ORDER_CONFIRMED | mode=REAL | type={TRADE_TYPE} | orderId={order_close.get('orderId') if isinstance(order_close, dict) else order_close}")
                                    
                                    
                                    # FUTURES CLOSE BY REDUCING 100% THE ORDER
                                    # orderFuture = order_future_cancel_REDUCE_only('SELL', TRADE_SYMBOL, volume, 'BOTH', 'MARKET')
                                    # orderFuture = order_future_cancel_all_open_order(TRADE_SYMBOL)
                                    # logger.info(orderFuture)
                                    
                                    if order_close:
                                        in_position = False
                                        last_close_time = aware_cetnow()  # ← ADD THIS LINE
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
                                        ROI_PERC_ATTEMPTS = 0
                                        ROI_AVG_GROWS_ATTEMPTS = 0
                                        
                                    
                                else:
                                    logger.info(f"[TRADE] | event=OVERBOUGHT_SELL | mode=SIMULATED | rsi={last_rsi:.2f} | futures={futures_current_price:.2f}")
                                    
                                    in_position = False
                                    last_close_time = aware_cetnow()  # ← ADD THIS LINE
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
                                    ROI_PERC_ATTEMPTS = 0
                                    ROI_AVG_GROWS_ATTEMPTS = 0
                    # ── SHORT ENTRY: open short when RSI overbought ──────────────────────
                    if ACTION_SELL and not in_position_sell:
                        if float(futures_current_price) > 0:
                            logger.info(f"[SIGNAL] | event=OVERBOUGHT_SHORT_ENTRY | rsi={last_rsi:.2f} | futures={futures_current_price:.4f}")
                            if not BLOCK_ORDER:
                                # REAL: cancel stale orders, then open short
                                order_future_cancel_all_open_order(TRADE_SYMBOL)
                                order_result_sell = order_future_create_order(SIDE_SELL, TRADE_SYMBOL, QTY_BUY, 'BOTH', ORDER_TYPE_MARKET)
                                if order_result_sell:
                                    # Fetch actual fill from position info (short = negative positionAmt)
                                    positions = client.futures_position_information(symbol=TRADE_SYMBOL, recvWindow=60000)
                                    for position in positions:
                                        if float(position['positionAmt']) < 0:
                                            futures_entry_price_sell = float(position['entryPrice'])
                                            volume_sell = abs(float(position['positionAmt']))
                                            break
                                    if futures_entry_price_sell <= 0:
                                        futures_entry_price_sell = float(futures_current_price)
                                    volume_sell = volume_sell if volume_sell > 0 else QTY_BUY

                                    in_position_sell = True
                                    sorted_roi_sell.restart()
                                    sorted_roi_sell.push(ROI_PROFIT)
                                    PROFITS_SELL["TRAIL_STOP_ROI_SELL"] = ROI_PROFIT
                                    PROFITS_SELL["TRAIL_LAST_ROI_SELL"] = ROI_PROFIT
                                    ROI_PERC_ATTEMPTS_SELL    = 0
                                    ROI_AVG_GROWS_ATTEMPTS_SELL = 0

                                    # Targets for SHORT: profit = price drops, loss = price rises
                                    PROFITS_SELL["WHEN_SELL"] = round(futures_entry_price_sell / BUY_PROFIT_CALC, PRECISION_PROFIT_LOSS)
                                    LOSSES_SELL["WHEN_SELL"]  = round(futures_entry_price_sell / BUY_LOSS_CALC,   PRECISION_PROFIT_LOSS)

                                    pnl_tp = calculate_pnl_futures(futures_entry_price_sell, PROFITS_SELL["WHEN_SELL"], volume_sell, False)
                                    roi_tp = mine_calculate_roi_with_imr(PROFITS_SELL["WHEN_SELL"], futures_entry_price_sell, volume_sell, False, TRADE_LEVERAGE)
                                    pnl_sl = calculate_pnl_futures(futures_entry_price_sell, LOSSES_SELL["WHEN_SELL"], volume_sell, False)
                                    roi_sl = mine_calculate_roi_with_imr(LOSSES_SELL["WHEN_SELL"], futures_entry_price_sell, volume_sell, False, TRADE_LEVERAGE)

                                    logger.info(f"[TRADE] | event=OPEN | mode=REAL | side=SHORT | symbol={TRADE_SYMBOL} | futures_entry={futures_entry_price_sell:.4f} | qty={volume_sell} | notional={round(futures_entry_price_sell * volume_sell, 2)} USDT")
                                    logger.info(f"[TRADE] | event=TARGETS | side=SHORT | take_profit={PROFITS_SELL['WHEN_SELL']} (roi={roi_tp}% pnl={pnl_tp}) | stop_loss={LOSSES_SELL['WHEN_SELL']} (roi={roi_sl}% pnl={pnl_sl}) | trail_stop_roi={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}%")
                                    logger.info(f"[TRAIL] | event=INIT | side=SHORT | history={sorted_roi_sell.get_values()} | trail_stop={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}% | trail_last={PROFITS_SELL['TRAIL_LAST_ROI_SELL']}%")
                                    print_signals(True)

                            else:  # SIMULATED SHORT
                                futures_entry_price_sell = float(futures_current_price)
                                volume_sell = QTY_BUY
                                in_position_sell = True
                                sorted_roi_sell.restart()
                                sorted_roi_sell.push(ROI_PROFIT)
                                PROFITS_SELL["TRAIL_STOP_ROI_SELL"] = ROI_PROFIT
                                PROFITS_SELL["TRAIL_LAST_ROI_SELL"] = ROI_PROFIT
                                ROI_PERC_ATTEMPTS_SELL    = 0
                                ROI_AVG_GROWS_ATTEMPTS_SELL = 0

                                PROFITS_SELL["WHEN_SELL"] = round(futures_entry_price_sell / BUY_PROFIT_CALC, PRECISION_PROFIT_LOSS)
                                LOSSES_SELL["WHEN_SELL"]  = round(futures_entry_price_sell / BUY_LOSS_CALC,   PRECISION_PROFIT_LOSS)

                                pnl_tp = calculate_pnl_futures(futures_entry_price_sell, PROFITS_SELL["WHEN_SELL"], volume_sell, False)
                                roi_tp = mine_calculate_roi_with_imr(PROFITS_SELL["WHEN_SELL"], futures_entry_price_sell, volume_sell, False, TRADE_LEVERAGE)
                                pnl_sl = calculate_pnl_futures(futures_entry_price_sell, LOSSES_SELL["WHEN_SELL"], volume_sell, False)
                                roi_sl = mine_calculate_roi_with_imr(LOSSES_SELL["WHEN_SELL"], futures_entry_price_sell, volume_sell, False, TRADE_LEVERAGE)

                                logger.info(f"[TRADE] | event=OPEN | mode=SIMULATED | side=SHORT | symbol={TRADE_SYMBOL} | futures_entry={futures_entry_price_sell:.4f} | qty={volume_sell} | notional={round(futures_entry_price_sell * volume_sell, 2)} USDT")
                                logger.info(f"[TRADE] | event=TARGETS | side=SHORT | take_profit={PROFITS_SELL['WHEN_SELL']} (roi={roi_tp}% pnl={pnl_tp}) | stop_loss={LOSSES_SELL['WHEN_SELL']} (roi={roi_sl}% pnl={pnl_sl}) | trail_stop_roi={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}%")
                                logger.info(f"[TRAIL] | event=INIT | side=SHORT | history={sorted_roi_sell.get_values()} | trail_stop={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}% | trail_last={PROFITS_SELL['TRAIL_LAST_ROI_SELL']}%")
                                print_signals(True)
                    # ── END SHORT ENTRY ──────────────────────────────────────────────────

                    # ── SHORT MANAGEMENT: monitor open short position ─────────────────
                    if ACTION_SELL and in_position_sell:
                        curr_pnlProfitSell = calculate_pnl_futures(futures_entry_price_sell, futures_current_price, volume_sell, False)
                        curr_roiProfitSell = mine_calculate_roi_with_imr(futures_entry_price_sell, futures_current_price, volume_sell, False, TRADE_LEVERAGE)

                        if curr_roiProfitSell < 0 or curr_pnlProfitSell < 0:
                            logger.debug(f"[STATUS] | direction=NEGATIVE | side=SHORT | futures={futures_current_price:.4f} | roi={curr_roiProfitSell:.2f}% | pnl={curr_pnlProfitSell:.2f} USDT | stop_loss_roi={ROI_STOP_LOSS}% | trail_last={PROFITS_SELL['TRAIL_LAST_ROI_SELL']}%")
                            # Reset trail when short goes negative
                            sorted_roi_sell.restart()
                            sorted_roi_sell.push(ROI_PROFIT)
                            PROFITS_SELL["TRAIL_STOP_ROI_SELL"] = ROI_PROFIT
                            PROFITS_SELL["TRAIL_LAST_ROI_SELL"] = ROI_PROFIT
                            logger.info(f"[TRAIL] | event=RESET | side=SHORT | reason=negative_roi | roi={curr_roiProfitSell}% | history={sorted_roi_sell.get_values()}")
                        else:
                            logger.debug(f"[STATUS] | direction=POSITIVE | side=SHORT | futures={futures_current_price:.4f} | roi={curr_roiProfitSell:.2f}% | pnl={curr_pnlProfitSell:.2f} USDT | trail_stop={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}% | trail_last={PROFITS_SELL['TRAIL_LAST_ROI_SELL']}%")

                        # Trailing stop for SHORT (mirrors BUY logic)
                        if curr_roiProfitSell > float(sorted_roi_sell.peak()) and sorted_roi_sell.get_size() < roi_stack_size:
                            PROFITS_SELL["TRAIL_STOP_ROI_SELL"] = round(max(sorted_roi_sell.peak(), curr_roiProfitSell * (1 - trail_percent / 100)), DECIMAL_CALC)
                            sorted_roi_sell.push(curr_roiProfitSell)
                            PROFITS_SELL["TRAIL_LAST_ROI_SELL"] = sorted_roi_sell.peak()
                            logger.info(f"[TRAIL] | event=NEW_HIGH | side=SHORT | curr_roi={curr_roiProfitSell}% | new_trail_stop={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}% | new_trail_last={PROFITS_SELL['TRAIL_LAST_ROI_SELL']}% | history={sorted_roi_sell.get_values()}")
                        else:
                            PROFITS_SELL["TRAIL_LAST_ROI_SELL"] = sorted_roi_sell.peak()

                        ROIS_GROWS_CALC_SELL = calculate_percentage_change(sorted_roi_sell.baseline(), sorted_roi_sell.peak())
                        if ROIS_GROWS_CALC_SELL > ROI_PERC_GROWS:
                            ROI_PERC_ATTEMPTS_SELL += 1
                            logger.info(f"[TRAIL] | event=PERC_TRIGGER | side=SHORT | curr_roi={curr_roiProfitSell}% | grows_calc={ROIS_GROWS_CALC_SELL}% | attempts={ROI_PERC_ATTEMPTS_SELL}/{ROI_PERC_MAX_ATTEMPTS}")
                        if sorted_roi_sell.get_size() > 1 and sorted_roi_sell.average_percentage_growth() > ROI_AVG_GROWS:
                            ROI_AVG_GROWS_ATTEMPTS_SELL += 1
                            logger.info(f"[TRAIL] | event=AVG_TRIGGER | side=SHORT | avg_growth={sorted_roi_sell.average_percentage_growth()}% | attempts={ROI_AVG_GROWS_ATTEMPTS_SELL}/{ROI_AVG_MAX_ATTEMPTS}")

                        # ── SHORT EXIT CONDITIONS ─────────────────────────────────────────
                        should_close_short = (
                            curr_roiProfitSell <= float(ROI_STOP_LOSS)                                                                     # stop loss
                            or curr_roiProfitSell > float(PROFITS_SELL["TRAIL_LAST_ROI_SELL"])                                              # new peak (take profit at trail)
                            or float(futures_current_price) >= float(round(LOSSES_SELL["WHEN_SELL"], DECIMAL_CALC))                         # price rose to stop level
                            or float(futures_current_price) <= float(round(PROFITS_SELL["WHEN_SELL"], DECIMAL_CALC))                        # price fell to take profit
                            or ((ROI_PERC_ATTEMPTS_SELL > ROI_PERC_MAX_ATTEMPTS) and curr_pnlProfitSell > 0)                                # patience exhausted with profit
                            or ((ROI_AVG_GROWS_ATTEMPTS_SELL > ROI_AVG_MAX_ATTEMPTS) and curr_pnlProfitSell > 0)                            # avg growth patience exhausted
                            or (curr_roiProfitSell < float(PROFITS_SELL["TRAIL_STOP_ROI_SELL"]) and float(PROFITS_SELL["TRAIL_STOP_ROI_SELL"]) > ROI_PROFIT)  # trail stop hit
                        )

                        if should_close_short:
                            # Determine exit reason
                            if curr_roiProfitSell <= float(ROI_STOP_LOSS):
                                soldDesc_s  = f"{TRADE_TYPE} SHORT STOP LOSS (roi={curr_roiProfitSell}% <= stop={ROI_STOP_LOSS}%)"
                                soldDesc1_s = f"exit_price={futures_current_price} roi={curr_roiProfitSell}% pnl={curr_pnlProfitSell}"
                                logger.info(f"[TRADE] | event=EXIT_TRIGGER | side=SHORT | reason=STOP_LOSS | roi={curr_roiProfitSell}% | threshold={ROI_STOP_LOSS}%")
                            elif curr_roiProfitSell < float(PROFITS_SELL["TRAIL_STOP_ROI_SELL"]) and float(PROFITS_SELL["TRAIL_STOP_ROI_SELL"]) > ROI_PROFIT:
                                soldDesc_s  = f"{TRADE_TYPE} SHORT TRAIL STOP HIT (roi={curr_roiProfitSell}% < trail_stop={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}%)"
                                soldDesc1_s = f"exit_price={futures_current_price} roi={curr_roiProfitSell}% pnl={curr_pnlProfitSell}"
                                logger.info(f"[TRADE] | event=EXIT_TRIGGER | side=SHORT | reason=TRAIL_STOP | curr_roi={curr_roiProfitSell}% | trail_stop={PROFITS_SELL['TRAIL_STOP_ROI_SELL']}%")
                            elif float(futures_current_price) <= float(round(PROFITS_SELL["WHEN_SELL"], DECIMAL_CALC)):
                                soldDesc_s  = f"{TRADE_TYPE} SHORT TAKE PROFIT (price={futures_current_price} <= target={PROFITS_SELL['WHEN_SELL']})"
                                soldDesc1_s = f"exit_price={futures_current_price} roi={curr_roiProfitSell}% pnl={curr_pnlProfitSell}"
                                logger.info(f"[TRADE] | event=EXIT_TRIGGER | side=SHORT | reason=TAKE_PROFIT | price={futures_current_price} | target={PROFITS_SELL['WHEN_SELL']}")
                            else:
                                soldDesc_s  = f"{TRADE_TYPE} SHORT PROFIT (roi={curr_roiProfitSell}%)"
                                soldDesc1_s = f"exit_price={futures_current_price} roi={curr_roiProfitSell}% pnl={curr_pnlProfitSell}"
                                logger.info(f"[TRADE] | event=EXIT_TRIGGER | side=SHORT | reason=PATIENCE | roi={curr_roiProfitSell}%")

                            if not BLOCK_ORDER:
                                # REAL: close short with BUY reduce-only
                                order_close_sell = order_future_cancel_REDUCE_only('BUY', TRADE_SYMBOL, volume_sell, 'BOTH', 'MARKET')
                                order_future_cancel_all_open_order(TRADE_SYMBOL)
                                logger.info(f"[TRADE] | event=ORDER_CONFIRMED | mode=REAL | side=SHORT_CLOSE | orderId={order_close_sell.get('orderId') if isinstance(order_close_sell, dict) else order_close_sell}")
                                if order_close_sell:
                                    in_position_sell = False
                                    last_close_time_sell = aware_cetnow()
                                    outcome_s = "PROFIT" if curr_roiProfitSell >= 0 else "LOSS"
                                    logger.info(f"[TRADE] | event=CLOSE | mode=REAL | side=SHORT | outcome={outcome_s} | roi={curr_roiProfitSell}% | reason={soldDesc_s} | detail={soldDesc1_s}")
                                    print_signals(False)
                                    SINAIS['ENTRY_POINT'] = ""
                                    if curr_pnlProfitSell >= 0:
                                        TOTALS['TOTAL_PROFITS_SELL'] += curr_pnlProfitSell
                                        TOTALS['TOTAL_PROFITS_SELL'] = round(TOTALS['TOTAL_PROFITS_SELL'], DECIMAL_CALC)
                                        TOTALS['COUNT_PROFITS_SELL'] += 1
                                        sorted_last_profits_sell.push(curr_pnlProfitSell)
                                    else:
                                        TOTALS['TOTAL_LOSSES_SELL'] -= abs(curr_pnlProfitSell)
                                        TOTALS['TOTAL_LOSSES_SELL'] = round(TOTALS['TOTAL_LOSSES_SELL'], DECIMAL_CALC)
                                        TOTALS['COUNT_LOSSES_SELL'] += 1
                                        sorted_last_losses_sell.push(curr_pnlProfitSell)
                                    curr_roiProfitSell = 0
                                    curr_pnlProfitSell = 0
                                    ROI_PERC_ATTEMPTS_SELL    = 0
                                    ROI_AVG_GROWS_ATTEMPTS_SELL = 0
                            else:
                                # SIMULATED close short
                                in_position_sell = False
                                last_close_time_sell = aware_cetnow()
                                outcome_s = "PROFIT" if curr_roiProfitSell >= 0 else "LOSS"
                                logger.info(f"[TRADE] | event=CLOSE | mode=SIMULATED | side=SHORT | outcome={outcome_s} | roi={curr_roiProfitSell}% | reason={soldDesc_s} | detail={soldDesc1_s}")
                                print_signals(False)
                                SINAIS['ENTRY_POINT'] = ""
                                if curr_pnlProfitSell >= 0:
                                    TOTALS['TOTAL_PROFITS_SELL'] += curr_pnlProfitSell
                                    TOTALS['TOTAL_PROFITS_SELL'] = round(TOTALS['TOTAL_PROFITS_SELL'], DECIMAL_CALC)
                                    TOTALS['COUNT_PROFITS_SELL'] += 1
                                    sorted_last_profits_sell.push(curr_pnlProfitSell)
                                else:
                                    TOTALS['TOTAL_LOSSES_SELL'] -= abs(curr_pnlProfitSell)
                                    TOTALS['TOTAL_LOSSES_SELL'] = round(TOTALS['TOTAL_LOSSES_SELL'], DECIMAL_CALC)
                                    TOTALS['COUNT_LOSSES_SELL'] += 1
                                    sorted_last_losses_sell.push(curr_pnlProfitSell)
                                curr_roiProfitSell = 0
                                curr_pnlProfitSell = 0
                                ROI_PERC_ATTEMPTS_SELL    = 0
                                ROI_AVG_GROWS_ATTEMPTS_SELL = 0
                    # ── END SHORT MANAGEMENT ─────────────────────────────────────────────
                
                # if last_rsi < RSI_OVERSOLD and SINAIS["MSG_3"] == "BUY IMBALANCE" and SINAIS["MSG_1"] == "BUY  SIGNAL":             
                # if last_rsi < RSI_OVERSOLD:             
                if last_rsi < RSI_OVERSOLD and SINAIS["MSG_3"] != "SELL IMBALANCE":
                    if in_position:
                        logger.debug(f"[SIGNAL] | event=OVERSOLD_SKIP | rsi={last_rsi:.2f} | in_position=True")
                    elif last_close_time is not None and (aware_cetnow() - last_close_time).total_seconds() < COOLDOWN_SECONDS:
                        # ↑ ADD THIS elif BLOCK
                        elapsed = (aware_cetnow() - last_close_time).total_seconds()
                        logger.debug(f"[COOLDOWN] | event=ENTRY_BLOCKED | elapsed={elapsed:.1f}s | required={COOLDOWN_SECONDS}s")

                    # ── SHORT CLOSE at OVERSOLD ───────────────────────────────────────
                    if ACTION_SELL and in_position_sell:
                        logger.info(f"[SIGNAL] | event=OVERSOLD_SHORT_CLOSE | rsi={last_rsi:.2f} | roi={curr_roiProfitSell}% | pnl={curr_pnlProfitSell}")
                        soldDesc_s  = f"{TRADE_TYPE} SHORT CLOSE AT OVERSOLD RSI={last_rsi:.2f}"
                        soldDesc1_s = f"exit_price={futures_current_price} roi={curr_roiProfitSell}% pnl={curr_pnlProfitSell}"
                        logger.info(f"[TRADE] | event=EXIT_TRIGGER | side=SHORT | reason=RSI_OVERSOLD | rsi={last_rsi:.2f}")
                        if not BLOCK_ORDER:
                            order_close_sell = order_future_cancel_REDUCE_only('BUY', TRADE_SYMBOL, volume_sell, 'BOTH', 'MARKET')
                            order_future_cancel_all_open_order(TRADE_SYMBOL)
                            logger.info(f"[TRADE] | event=ORDER_CONFIRMED | mode=REAL | side=SHORT_CLOSE | orderId={order_close_sell.get('orderId') if isinstance(order_close_sell, dict) else order_close_sell}")
                            if order_close_sell:
                                in_position_sell = False
                                last_close_time_sell = aware_cetnow()
                                outcome_s = "PROFIT" if curr_roiProfitSell >= 0 else "LOSS"
                                logger.info(f"[TRADE] | event=CLOSE | mode=REAL | side=SHORT | outcome={outcome_s} | roi={curr_roiProfitSell}% | reason={soldDesc_s}")
                                print_signals(False)
                                SINAIS['ENTRY_POINT'] = ""
                                if curr_pnlProfitSell >= 0:
                                    TOTALS['TOTAL_PROFITS_SELL'] += curr_pnlProfitSell
                                    TOTALS['TOTAL_PROFITS_SELL'] = round(TOTALS['TOTAL_PROFITS_SELL'], DECIMAL_CALC)
                                    TOTALS['COUNT_PROFITS_SELL'] += 1
                                    sorted_last_profits_sell.push(curr_pnlProfitSell)
                                else:
                                    TOTALS['TOTAL_LOSSES_SELL'] -= abs(curr_pnlProfitSell)
                                    TOTALS['TOTAL_LOSSES_SELL'] = round(TOTALS['TOTAL_LOSSES_SELL'], DECIMAL_CALC)
                                    TOTALS['COUNT_LOSSES_SELL'] += 1
                                    sorted_last_losses_sell.push(curr_pnlProfitSell)
                                curr_roiProfitSell = 0
                                curr_pnlProfitSell = 0
                                ROI_PERC_ATTEMPTS_SELL    = 0
                                ROI_AVG_GROWS_ATTEMPTS_SELL = 0
                        else:  # SIMULATED
                            in_position_sell = False
                            last_close_time_sell = aware_cetnow()
                            outcome_s = "PROFIT" if curr_roiProfitSell >= 0 else "LOSS"
                            logger.info(f"[TRADE] | event=CLOSE | mode=SIMULATED | side=SHORT | outcome={outcome_s} | roi={curr_roiProfitSell}% | reason={soldDesc_s}")
                            print_signals(False)
                            SINAIS['ENTRY_POINT'] = ""
                            if curr_pnlProfitSell >= 0:
                                TOTALS['TOTAL_PROFITS_SELL'] += curr_pnlProfitSell
                                TOTALS['TOTAL_PROFITS_SELL'] = round(TOTALS['TOTAL_PROFITS_SELL'], DECIMAL_CALC)
                                TOTALS['COUNT_PROFITS_SELL'] += 1
                                sorted_last_profits_sell.push(curr_pnlProfitSell)
                            else:
                                TOTALS['TOTAL_LOSSES_SELL'] -= abs(curr_pnlProfitSell)
                                TOTALS['TOTAL_LOSSES_SELL'] = round(TOTALS['TOTAL_LOSSES_SELL'], DECIMAL_CALC)
                                TOTALS['COUNT_LOSSES_SELL'] += 1
                                sorted_last_losses_sell.push(curr_pnlProfitSell)
                            curr_roiProfitSell = 0
                            curr_pnlProfitSell = 0
                            ROI_PERC_ATTEMPTS_SELL    = 0
                            ROI_AVG_GROWS_ATTEMPTS_SELL = 0
                    # ── END SHORT CLOSE ──────────────────────────────────────────────

                    else:
                        # logger.info(f"[SIGNAL] | event=OVERSOLD_BUY | rsi={last_rsi:.2f} | qty={round(QTY_BUY, VOLUME_DEC)} | spot={spot_current_price:.2f} | futures={futures_current_price:.2f}")
                        logger.info(f"[SIGNAL] | event=OVERSOLD_BUY | rsi={last_rsi:.2f} | qty={round(QTY_BUY, VOLUME_DEC)} | futures={futures_current_price:.4f}")
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
                                    # order_result = order_spot(SIDE_BUY, TRADE_SYMBOL.upper(), volume, ORDER_TYPE_MARKET)
                                    
                                    # FUTURES CANCEL ALL ORDER 
                                    order_future_cancel_all_open_order(TRADE_SYMBOL)
                                    
                                    # FUTURE CREATE ORDER
                                    order_result = order_future_create_order(SIDE_BUY, TRADE_SYMBOL, volume, 'BOTH', ORDER_TYPE_MARKET)
                                    
                                    
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
                                        
                                    # SPOT
                                    # if order_result:
                                    #     spot_entry_price = float(order_result['fills'][0]['price'])
                                    #     amountQty = float(order_result['fills'][0]['qty'])
                                    #     volume = amountQty
                                            
                                    #     in_position = True
                                            
                                    #     sorted_roi.restart()
                                    #     sorted_roi.push(ROI_PROFIT)
                                    #     logger.info(f"[TRAIL] | event=INIT | history={sorted_roi.get_values()} | trail_stop={PROFITS['TRAIL_STOP_ROI_BUY']}% | trail_last={PROFITS['TRAIL_LAST_ROI_BUY']}%")
                                    #     PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT     
                                    #     PROFITS["TRAIL_LAST_ROI_BUY"] = ROI_PROFIT
                                    #     ROI_PERC_ATTEMPTS = 0
                                    #     ROI_AVG_GROWS_ATTEMPTS = 0
                                    #     profit_calculus("REAL TRADE", ACTION_BUY, float(spot_entry_price), float(futures_entry_price), float(volume))
                                    #     # print_signals(futures_current_price, spot_current_price, True)
                                    
                                    # FUTURES:
                                    if order_result:
                                        # Fetch actual fill price from futures position
                                        positions = client.futures_position_information(symbol=TRADE_SYMBOL, recvWindow=60000)
                                        for position in positions:
                                            if float(position['positionAmt']) != 0:
                                                futures_entry_price = float(position['entryPrice'])
                                                volume = abs(float(position['positionAmt']))
                                                amountQty = volume
                                                break
                                        
                                        # Fallback if position fetch fails
                                        if futures_entry_price <= 0:
                                            futures_entry_price = float(futures_current_price)
                                        
                                        spot_entry_price = futures_entry_price  # align both references

                                        in_position = True

                                        sorted_roi.restart()
                                        sorted_roi.push(ROI_PROFIT)
                                        logger.info(f"[TRAIL] | event=INIT | history={sorted_roi.get_values()} | trail_stop={PROFITS['TRAIL_STOP_ROI_BUY']}% | trail_last={PROFITS['TRAIL_LAST_ROI_BUY']}%")
                                        PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT
                                        PROFITS["TRAIL_LAST_ROI_BUY"] = ROI_PROFIT
                                        ROI_PERC_ATTEMPTS = 0
                                        ROI_AVG_GROWS_ATTEMPTS = 0
                                        profit_calculus("REAL TRADE", ACTION_BUY, float(spot_entry_price), float(futures_entry_price), float(volume))    
                                        
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
                                    logger.info(f"[TRAIL] | event=INIT | history={sorted_roi.get_values()} | trail_stop={PROFITS['TRAIL_STOP_ROI_BUY']}% | trail_last={PROFITS['TRAIL_LAST_ROI_BUY']}%") 
                                    PROFITS["TRAIL_STOP_ROI_BUY"] = ROI_PROFIT     
                                    PROFITS["TRAIL_LAST_ROI_BUY"] = ROI_PROFIT
                                    ROI_PERC_ATTEMPTS = 0
                                    ROI_AVG_GROWS_ATTEMPTS = 0
                                    profit_calculus("SIMULATED", ACTION_BUY, float(spot_entry_price), float(futures_entry_price), float(volume))
                                        
                                    # print_signals(futures_current_price, spot_current_price, True)
                                    in_position = True
    except Exception as e:
        logger.error(f"[ERROR] | fn=process_kline_message | error={e}", exc_info=True)                                
                                
# Function to process Depth WebSocket messages
def process_depth_message(depth_ws, message):
    try:
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
            logger.info(f"[SIGNAL] | source=depth | type=SELL_IMBALANCE | imbalance={imbalance_sell:.4f} | volume={total_buy_volume:.4f}")
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
            logger.info(f"[SIGNAL] | source=depth | type=BUY_IMBALANCE | imbalance={imbalance_buy:.4f} | volume={total_sell_volume:.4f}")
            SINAIS["BUY_VOL_IMB"] = SINAIS["BUY_VOL_IMB"] + 1 
            SINAIS["MSG_3"] = "BUY IMBALANCE"  
    except Exception as e:
            logger.error(f"[ERROR] | fn=process_depth_message | error={e}", exc_info=True)            
        

# Start WebSocket for Kline data
SOCKET_SPOT_KLINE = "wss://stream.binance.com:9443/ws/{}@kline_1s".format(TRADE_SYMBOL.lower())
# Start WebSocket for Depth data
SOCKET_SPOT_DEPTH = "wss://stream.binance.com:9443/ws/{}@depth".format(TRADE_SYMBOL.lower())
              
              

# Start WebSocket for Kline data
def run_kline_ws():
    global should_stop
    while not should_stop:
        kline_ws = websocket.WebSocketApp(   # recreated on each reconnect
            SOCKET_SPOT_KLINE, on_open=on_open, on_close=on_close, on_message=process_kline_message
        )
        kline_ws.run_forever()

# Start WebSocket for Depth data
def run_depth_ws():
    global should_stop
    while not should_stop:
        kline_ws = websocket.WebSocketApp(   # recreated on each reconnect
            SOCKET_SPOT_DEPTH, on_open=on_open, on_close=on_close, on_message=process_depth_message
        )
        kline_ws.run_forever()        

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