# 1 - Imports
import requests, hashlib, hmac, time, urllib
from urllib.parse import urlparse, parse_qs

# 2 - Your parameters : Modify the values below
binance_base_url_api = "https://api.binance.com"
endpoint_account = "/api/v3/account"

binance_base_url_fapi = "https://fapi.binance.com"
endpoint_future_openOrders = "/fapi/v1/openOrders"

api_key = "fpqeCxqgGWHjRxK4qmunjAFOEzB7CsQabuwUhhnkshgNEPi5kW5zsMH2TuO2CEmp"
api_secret = "NzU4udKNZ1bl3VM5VpYlEG2S9FstbmeYwv5ZTnWOcZxfS4cQf4dQmhSJRpRwihar"
    
params = {
    # Add here your endpoint params
    "timestamp" : int(time.time() * 1E3),
    "recvWindow": 5000,  
}

# 3 - Generating the signature and the headers
query_string = urllib.parse.urlencode(params)
signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
params["signature"] = signature
headers = {
    "X-MBX-APIKEY": api_key
}

# 4 - Making the API call
# API Account
# response = requests.get(binance_base_url + endpoint, params = params, headers = headers)
# FAPI openOrders
response = requests.get(binance_base_url_fapi + endpoint_future_openOrders, params = params, headers = headers)

print(response.json())