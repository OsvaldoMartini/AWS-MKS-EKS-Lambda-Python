def average_percentage_growth(arr):
        if len(arr) < 2:
            return 0  # If there's not enough data, return 0 or handle it accordingly
        percentage_growths = []
        count = 0  # Count of valid growth calculations
        for i in range(len(arr) - 1):
            if arr[i] == 0:
                continue  # Skip calculation if the denominator is zero
            growth = ((arr[i+1] - arr[i]) / arr[i]) * 100
            percentage_growths.append(growth)
            count += 1
            
        if count == 0:
            return 0  # If there were no valid growth calculations, return 0    
        return sum(percentage_growths) / len(percentage_growths) 

# Example usage:
# arr = [2.0, 5.54, 5.63, 4, 1.4 , 1.8]
arr = [0, 0, -1.8, -5]

average_growth = average_percentage_growth(arr)
print("Average percentage growth:", average_growth)