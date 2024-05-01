from datetime import datetime

class AverageTimeCalculator:
    def __init__(self, time_strings):
        self.time_strings = time_strings

    def calculate_average_time(self):
        # Convert time strings to datetime objects
        times = [datetime.strptime(t, "%H:%M") for t in self.time_strings]

        # Calculate differences between consecutive times
        differences = [(times[i+1] - times[i]).total_seconds() / 60 for i in range(len(times)-1)]

        # Calculate average time difference
        average_difference = sum(differences) / len(differences)

        return average_difference

# Example usage:
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

calculator = AverageTimeCalculator(time_strings)
average_time = calculator.calculate_average_time()
print("Average time between the 10 times:", average_time, "minutes")
