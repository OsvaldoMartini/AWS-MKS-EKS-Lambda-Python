def calculate_original_value_with_percentage_profit(profit_percentage, new_value):
    original_value = new_value / (1 + profit_percentage / 100)
    return original_value

# Example usage:
profit_percentage = 20  # Percentage profit
new_value = 120  # New value
original_value = calculate_original_value_with_percentage_profit(profit_percentage, new_value)
print(f"The original value with a {profit_percentage}% profit is {original_value:.2f}.")
