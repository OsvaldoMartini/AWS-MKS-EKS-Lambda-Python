RSI_OVERSOLD = 5

def increase_rsi():
    global RSI_OVERSOLD
    RSI_OVERSOLD += 1
    print(f"RSI_OVERSOLD increased: {RSI_OVERSOLD}")

def decrease_rsi():
    global RSI_OVERSOLD
    if RSI_OVERSOLD > 0:
        RSI_OVERSOLD -= 1
    print(f"RSI_OVERSOLD decreased: {RSI_OVERSOLD}")

while True:
    key = input("Press 'o' to increase, 'l' to decrease, 'q' to quit: ")
    if key == 'o':
        increase_rsi()
    elif key == 'l':
        decrease_rsi()
    elif key == 'q':
        break
