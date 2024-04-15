class LastFiveStack:
    def __init__(self):
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
  

# Example usage:
last_five = LastFiveStack()
values = [5, 2, 7, 3, 1, 4, 6]

for value in values:
    last_five.push(value)

print("Last five values in ascending order:", last_five.get_values())
print("Last :", last_five.get_values()[-2])
