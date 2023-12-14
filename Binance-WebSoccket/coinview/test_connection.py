import requests, json, time, hashlib


apikey = "fpqeCxqgGWHjRxK4qmunjAFOEzB7CsQabuwUhhnkshgNEPi5kW5zsMH2TuO2CEmp"
secret = "NzU4udKNZ1bl3VM5VpYlEG2S9FstbmeYwv5ZTnWOcZxfS4cQf4dQmhSJRpRwihar"
test = requests.get("https://api.binance.com/api/v1/ping")
servertime = requests.get("https://api.binance.com/api/v1/time")

servertimeobject = json.loads(servertime.text)
servertimeint = servertimeobject['serverTime']

hashedsig = hashlib.sha256(secret).hexdigest()

userdata = requests.get("https://api.binance.com/api/v3/account",
    params = {
        "signature" : hashedsig,
        "timestamp" : servertimeint,
    },
    headers = {
        "X-MBX-APIKEY" : apikey,
    }
)
print(userdata)