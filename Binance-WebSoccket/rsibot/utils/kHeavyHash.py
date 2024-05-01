def k_heavy_hash(string, k):
    hash_value = 0
    
    for i, char in enumerate(string):
        hash_value += (ord(char) - ord('a') + 1) * (k ** i)
    
    return hash_value

# Example usage:
string = "hello"
k = 3
print("K-Heavy Hash of '{}' with k={} is: {}".format(string, k, k_heavy_hash(string, k)))
