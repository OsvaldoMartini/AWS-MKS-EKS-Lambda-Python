import time

# ANSI escape codes for moving cursor
move_up = '\x1b[1A'  # Move cursor up one line
clear_line = '\x1b[2K'  # Clear the entire line
move_down = '\x1b[1B'  # Move cursor down one line

SINAIS = {}
SINAIS["BUY_HIST"] = 0 
SINAIS["SELL_HIST"] = 0 
SINAIS["BUY_VOL_INC"] = 0 
SINAIS["SELL_VOL_DEC"] = 0 
SINAIS["BUY_VOL_IMB"] = 0 
SINAIS["SELL_VOL_IMB"] = 0 
SINAIS["MSG_1"] = "" 
SINAIS["MSG_2"] = "" 
SINAIS["MSG_3"] = "" 

spot_current_price = 0
last_rsi = 0
last_sma = 0
futures_current_price = 0
curr_roiProfitBuy = 0

# Print three different lines at the same position
for i in range(100):
    curr_roiProfitBuy = i
    # Move cursor up and clear line
    # Print the new line
    # print("SIGNAL     BUY: {}     SELL: {}  SIGNAL: {}".format(SINAIS["BUY_HIST"], SINAIS["SELL_HIST"], SINAIS["MSG_1"]), end="\r")
    # print(move_down + clear_line, end="")
    # print("SIGNAL VOL BUY: {} VOL SELL: {}".format(SINAIS["BUY_VOL_INC"], SINAIS["SELL_VOL_DEC"] ), end="\r")
    # print(move_down + clear_line, end="")
    # print("SIGNAL IMB BUY: {} IMB SELL: {}  ACTION: {}  {}".format(SINAIS["BUY_VOL_IMB"], SINAIS["SELL_VOL_IMB"], SINAIS["MSG_2"], SINAIS["MSG_3"]), end="\r")
    # print(move_down + clear_line, end="")
    # print("SMA : {:.2f}     RSI: {:.2f}".format(float(last_sma), float(last_rsi)), end="\r")
    # print(move_down + clear_line, end="")
    # print("SPOT   Current Price {:.2f}".format(float(spot_current_price)), end="\r")
    # print(move_down + clear_line, end="")
    # print("FUTURE Current Price {:.2f}".format(float(futures_current_price)), end="\r")
    # print(move_down + clear_line, end="")
    # print("Return on Investment (ROI): {:.2f}%".format(float(curr_roiProfitBuy)), end="\r")
    line1  = "SIGNAL     BUY: {}     SELL: {}  SIGNAL: {}".format(SINAIS["BUY_HIST"], SINAIS["SELL_HIST"], SINAIS["MSG_1"])
    line2  = "SIGNAL VOL BUY: {} VOL SELL: {}".format(SINAIS["BUY_VOL_INC"], SINAIS["SELL_VOL_DEC"] )
    line3  = "SIGNAL IMB BUY: {} IMB SELL: {}  ACTION: {}  {}".format(SINAIS["BUY_VOL_IMB"], SINAIS["SELL_VOL_IMB"], SINAIS["MSG_2"], SINAIS["MSG_3"])
    line4  = "SMA : {:.2f}     RSI: {:.2f}".format(float(last_sma), float(last_rsi))
    line5  = "SPOT   Current Price {:.2f}".format(float(spot_current_price))
    line6  = "FUTURE Current Price {:.2f}".format(float(futures_current_price))
    line7  = "Return on Investment (ROI): {:.2f}%".format(float(curr_roiProfitBuy))
    lines = line1 +"\n" + line2 +"\n" + line3 +"\n" + line4 +"\n" + line5 +"\n" + line6 +"\n" + line7
    print(lines)
    print(move_up + clear_line, end="")
    print(move_up + clear_line, end="")
    print(move_up + clear_line, end="")
    print(move_up + clear_line, end="")
    print(move_up + clear_line, end="")
    print(move_up + clear_line, end="")
    print(move_up + clear_line, end="")
            
    time.sleep(1)  # Just to pause briefly
  