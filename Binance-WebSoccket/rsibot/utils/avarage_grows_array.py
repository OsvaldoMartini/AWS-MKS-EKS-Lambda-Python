def average_percentage_growth(arr):
    percentage_growths = []
    for i in range(len(arr) - 1):
        growth = ((arr[i+1] - arr[i]) / arr[i]) * 100
        percentage_growths.append(growth)
    return sum(percentage_growths) / len(percentage_growths)

# Example usage:
arr = [2.0, 5.54, 5.63]

average_growth = average_percentage_growth(arr)
print("Average percentage growth:", average_growth)