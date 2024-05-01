from datetime import datetime

# Sample list of time strings
time_strings = [
    "08:00",
    "08:15",
    "09:00",
    "09:30",
    "10:00",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "13:00"
]

# Convert time strings to datetime objects
times = [datetime.strptime(t, "%H:%M") for t in time_strings]

# Calculate differences between consecutive times
differences = [(times[i+1] - times[i]).total_seconds() / 60 for i in range(len(times)-1)]

# Calculate average time difference
average_difference = sum(differences) / len(differences)

print("Average time between the 10 times:", average_difference, "minutes")
