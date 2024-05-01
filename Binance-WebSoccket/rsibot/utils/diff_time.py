from datetime import datetime

# Get the initial time
initial_time = datetime(2024, 4, 20, 11, 0, 0)  # Example initial time (year, month, day, hour, minute, second)

# Get the current time
current_time = datetime.now()

# Calculate the difference
time_difference = current_time - initial_time


# Extract specific components of the time difference
days = time_difference.days
hours, remainder = divmod(time_difference.seconds, 3600)
minutes, seconds = divmod(remainder, 60)

# Print the difference in a formatted way
print("Time difference: {} days, {} hours, {} minutes, {} seconds".format(days, hours, minutes, seconds))

# Print the difference
print("Time difference:", time_difference)
