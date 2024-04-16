from binance.client import Client
import config

client = Client(config.API_KEY, config.API_SECRET)

# Replace these with your API keys
api_key = 'your_api_key'
api_secret = 'your_api_secret'

client = Client(api_key, api_secret)

def calculate_pnl(entry_price, exit_price, quantity, side):
    if side == 'BUY':
        pnl = (exit_price - entry_price) * quantity
    elif side == 'SELL':
        pnl = (entry_price - exit_price) * quantity
    else:
        raise ValueError("Invalid side provided")
    return pnl

def calculate_roi(entry_price, exit_price):
    roi = ((exit_price - entry_price) / entry_price) * 100
    return roi

def get_trade_history(symbol):
    trades = client.get_my_trades(symbol=symbol)
    return trades

if __name__ == "__main__":
    symbol = 'BTCUSDT'  # Replace this with the symbol you traded
    trades = get_trade_history(symbol)

    total_pnl = 0
    total_roi = 0

    for trade in trades:
        entry_price = float(trade['price'])
        quantity = float(trade['qty'])
        side = trade['side']
        
        # Assuming you only have filled trades
        if 'commissionAsset' in trade:
            exit_price = float(trade['commission'])
        else:
            continue

        pnl = calculate_pnl(entry_price, exit_price, quantity, side)
        roi = calculate_roi(entry_price, exit_price)

        total_pnl += pnl
        total_roi += roi

    print("Total PNL:", total_pnl)
    print("Total ROI:", total_roi)
