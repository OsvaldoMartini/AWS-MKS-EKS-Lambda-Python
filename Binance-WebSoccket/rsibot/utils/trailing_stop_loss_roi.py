class TrailingStopROI:
    def __init__(self, initial_price, trail_roi):
        self.initial_price = initial_price
        self.trail_roi = trail_roi
        self.trailing_roi = trail_roi
        self.stop_loss_price = initial_price * (1 - trail_roi / 100)

    def update(self, current_price):
        current_roi = ((current_price - self.initial_price) / self.initial_price) * 100
        if current_roi > self.trailing_roi:
            self.trailing_roi = current_roi
            self.stop_loss_price = current_price * (1 - self.trail_roi / 100)

    def get_stop_loss_price(self):
        return self.stop_loss_price

# Example usage:
initial_price = 100  # Initial price of the asset
trail_roi = 2       # Trailing ROI percentage (2% in this example)

# Create a TrailingStopROI object
trailing_stop_roi = TrailingStopROI(initial_price, trail_roi)

# Simulate price changes
prices = [110, 115, 120, 115, 125, 130, 120, 125]

# Update and track stop-loss price
for price in prices:
    trailing_stop_roi.update(price)
    stop_loss_price = trailing_stop_roi.get_stop_loss_price()
    print(f"Current Price: {price}, Trailing Stop Loss Price: {stop_loss_price}")
