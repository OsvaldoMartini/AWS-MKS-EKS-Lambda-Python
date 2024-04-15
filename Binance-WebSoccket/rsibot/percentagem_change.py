def calculate_percentage_change(old_value, new_value):
    return ((new_value - old_value) / old_value) * 100

# Example usage:
old_value = 2.0
new_value = 6.1

percentage_change = calculate_percentage_change(old_value, new_value)
print(f"Percentage Change: {percentage_change}%")
