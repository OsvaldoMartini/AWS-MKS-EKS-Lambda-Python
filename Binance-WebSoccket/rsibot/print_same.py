import time

# ANSI escape codes for moving cursor
move_up = '\x1b[1A'  # Move cursor up one line
clear_line = '\x1b[2K'  # Clear the entire line
move_down = '\x1b[1B'  # Move cursor down one line

# Print three different lines at the same position
for i in range(3):
    # Move cursor up and clear line
    # Print the new line
    print(f"This is line {i+1}", end="\r")
    print(move_down + clear_line, end="")
    print(f"This is line {i+2}", end="\r")
    print(move_down + clear_line, end="")
    print(f"This is line {i+3}", end="\r")
    print(move_up + clear_line, end="")
    print(move_up + clear_line, end="")
    time.sleep(1)  # Just to pause briefly
