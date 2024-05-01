def calculate_percentage_change(old_value, new_value):
    percentage_change = ((new_value - old_value) / old_value) * 100
    return percentage_change

# Example usage:
old_value = 100  # Old value
new_value = -10  # New value
percentage = calculate_percentage_change(old_value, new_value)
print(f"The percentage change from {old_value} to {new_value} is {percentage:.2f}%.")
