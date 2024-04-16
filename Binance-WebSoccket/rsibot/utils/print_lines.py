# Open a file in write mode
with open("output.txt", "w") as f:
    # Redirect print output to the file
    print("Hello, world!", file=f)
    print("This is a test message.", file=f)
    print("Saving print output to a file.", file=f)
