import tkinter as tk

# Global variable for RSI_OVERSOLD
RSI_OVERSOLD = 5

# Function to increase RSI_OVERSOLD
def increase_rsi():
    global RSI_OVERSOLD
    RSI_OVERSOLD += 1
    update_label()

# Function to decrease RSI_OVERSOLD
def decrease_rsi():
    global RSI_OVERSOLD
    if RSI_OVERSOLD > 0:  # Prevent negative RSI values
        RSI_OVERSOLD -= 1
    update_label()

# Function to update the label with the current RSI_OVERSOLD value
def update_label():
    rsi_label.config(text=f"RSI_OVERSOLD: {RSI_OVERSOLD}")

# Create the main window
root = tk.Tk()
root.title("RSI Oversold Adjuster")

# Create a label to display the RSI_OVERSOLD value
rsi_label = tk.Label(root, text=f"RSI_OVERSOLD: {RSI_OVERSOLD}")
rsi_label.pack(pady=10)

# Create the increase and decrease buttons
increase_button = tk.Button(root, text="Increase", command=increase_rsi)
increase_button.pack(side=tk.LEFT, padx=20)

decrease_button = tk.Button(root, text="Decrease", command=decrease_rsi)
decrease_button.pack(side=tk.RIGHT, padx=20)

# Run the application
root.mainloop()
