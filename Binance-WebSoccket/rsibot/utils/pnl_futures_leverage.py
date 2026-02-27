def calculate_binance_pnl(entry_price, exit_price, quantity, leverage):
    # Calculate notional value
    notional_value = entry_price * quantity
    
    # Calculate initial margin (5% for cross margin)
    initial_margin = notional_value / leverage
    
    # Calculate P&L
    pnl = (exit_price - entry_price) * quantity
    
    return pnl, initial_margin

# Example usage
entry_price = 63597.9  # Entry price
exit_price = 63652  # Exit price
quantity = 319  # Quantity
leverage = 75  # Leverage

pnl, initial_margin = calculate_binance_pnl(entry_price, exit_price, quantity, leverage)
print("Total P&L:", pnl)
print("Initial Margin:", initial_margin)
