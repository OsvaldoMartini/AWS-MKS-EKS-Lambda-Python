import requests
import time
import hashlib
import hmac
import configMexc


def get_signature(params):
    params['api_key'] = configMexc.API_KEY
    params['req_time'] = int(time.time() * 1000)
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    signature = hmac.new(configMexc.API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def make_trade_request(method, endpoint, params={}):
    url = f"https://www.mexc.com/open/api/{endpoint}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    signature = get_signature(params)
    params['sign'] = signature
    response = requests.request(method, url, headers=headers, params=params)
    return response.json()

# Example: Place an order
params = {
    'symbol': 'BTC_USDT',
    'price': 60000,
    'quantity': 0.001,
    'trade_type': 'BUY',
    'order_type': 'LIMIT'
}
response = make_trade_request('POST', 'order', params=params)
print(response)
