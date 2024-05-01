import threading
import time
import random

class BitcoinPriceSimulator:
    def __init__(self, initial_price, initial_roi):
        self.price = initial_price
        self.roi = initial_roi
        self.lock = threading.Lock()  # Lock for thread safety

    def increase_decrease_price(self):
        for i in range(8):  # Loop 8 times
            increase_percentage = random.uniform(0.001, 0.002)  # Random increase between 0.1% and 0.2%
            self.price *= (1 + increase_percentage)
            increase_percentage = random.uniform(0.1, 0.5)  # Random increase between 10% and 50%
            self.roi *= (1 + increase_percentage)
            print("Bitcoin price decreased to: {:.2f} ROI : {:.2f}".format(self.price, self.roi))
            time.sleep(1)
            

        for i in range(8, 0, -1):  # Loop 8 times, decreasing
            decrease_percentage = random.uniform(0.001, 0.002)  # Random decrease between 0.1% and 0.2%
            self.price *= (1 - decrease_percentage)
            increase_percentage = random.uniform(0.1, 0.5)  # Random increase between 10% and 50%
            self.roi *= (1 - increase_percentage)
            print("Bitcoin price decreased to: {:.2f} ROI : {:.2f}".format(self.price, self.roi))
            time.sleep(1)
            
    def get_price(self):
        with self.lock:
            return self.price

    def get_roi(self):
        with self.lock:
            return self.roi            
            

# Creating an instance of the BitcoinPriceSimulator with initial price $64,000
btc_simulator = BitcoinPriceSimulator(64000, 30)

# Creating a thread for the price simulation
thread = threading.Thread(target=btc_simulator.increase_decrease_price)

# Starting the thread
thread.start()

# Main program continues while the thread is running
# You can add other tasks here if needed

# Catching values from another thread
for _ in range(10):  # Just for demonstration, catching values 10 times
    time.sleep(2)  # Wait for 2 seconds
    current_price = btc_simulator.get_price()
    current_roi = btc_simulator.get_roi()
    print("Current Bitcoin price:", round(current_price, 2))
    print("Current ROI:", round(current_roi, 4))


# Wait for the thread to finish
thread.join()


print("Thread finished")
