from datetime import datetime, timedelta

# Get current UTC time
utc_now = datetime.utcnow()

# CET is UTC + 1 hour
cet_now = utc_now + timedelta(hours=2)

print("Current time in CET:", cet_now)
