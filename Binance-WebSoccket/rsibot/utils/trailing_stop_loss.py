class TrailingStopLoss:
    def __init__(self, initial_price, trail_percent):
        self.initial_price = initial_price
        self.trail_percent = trail_percent
        self.stop_loss_price = initial_price * (1 - trail_percent / 100)

    def update(self, current_price):
        if current_price > self.initial_price:
            self.stop_loss_price = max(self.stop_loss_price, current_price * (1 - self.trail_percent / 100))

    def get_stop_loss_price(self):
        return self.stop_loss_price

# Example usage:
initial_price = 100  # Initial price of the asset
trail_percent = 2    # Trailing stop percentage (2% in this example)

# Create a TrailingStopLoss object
trailing_stop_loss = TrailingStopLoss(initial_price, trail_percent)

# Simulate price changes
prices = [110, 115, 120, 115, 125, 130, 120, 125]

# Update and track stop-loss price
for price in prices:
    trailing_stop_loss.update(price)
    stop_loss_price = trailing_stop_loss.get_stop_loss_price()
    print(f"Current Price: {price}, Trailing Stop Loss Price: {stop_loss_price}")
