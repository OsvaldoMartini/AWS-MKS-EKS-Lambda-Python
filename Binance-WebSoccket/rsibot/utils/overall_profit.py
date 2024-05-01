def calculate_percentage_positive_negative(positive_value, negative_value):
    absolute_positive = abs(positive_value)
    absolute_negative = abs(negative_value)
    
    total_change = absolute_positive + absolute_negative
    if absolute_positive > 0:
        percentage_change = ((total_change / absolute_positive) * 100) / 2
    else:
        percentage_change = 0
        
    return percentage_change

# Example usage:
positive_value = 241.31  # Positive value
negative_value = -2.72  # Negative value
percentage = calculate_percentage_positive_negative(positive_value, negative_value)
if positive_value - abs(negative_value) > 0:
    print(f"The percentage increase is {percentage:.2f}%.")
else:
    percentage = -1 * percentage
    print(f"The percentage decrease is {percentage:.2f}%.")
# print(f"The percentage change between {positive_value} and {negative_value} is {percentage:.2f}%.")
