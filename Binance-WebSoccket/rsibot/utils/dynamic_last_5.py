class LastFiveStack:
    def __init__(self):
        self.stack = []

    def restart(self):
        self.stack = []
        
    def push(self, value):
        if len(self.stack) >= 5:
            self.pop_until(value)
        else:
            self.insert_sorted(value)

    def insert_sorted(self, value):
        index = 0
        while index < len(self.stack) and self.stack[index] < value:
            index += 1
        self.stack.insert(index, value)

    def pop_until(self, value):
        while self.stack and self.stack[-1] < value and len(self.stack) >= 5:
            self.stack.pop()
        self.insert_sorted(value)

    def get_values(self):
        return self.stack

    def get_size(self):
        return len(self.stack)

    def average_percentage_growth(self):
        percentage_growths = []
        for i in range(len(self.stack) - 1):
            growth = ((self.stack[i+1] - self.stack[i]) / self.stack[i]) * 100
            percentage_growths.append(growth)
        return sum(percentage_growths) / len(percentage_growths)
  
# Example usage:
last_five = LastFiveStack()
values = [5, 2]

if (last_five.get_size() > 1):
    print(last_five.average_percentage_growth())

for value in values:
    last_five.push(value)

if (last_five.get_size() > 0):
    print(last_five.average_percentage_growth())


print("Last five values in ascending order:", last_five.get_values())
print("Last :", last_five.get_values()[0])
