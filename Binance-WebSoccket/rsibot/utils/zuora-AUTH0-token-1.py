import http.client

conn = http.client.HTTPSConnection("me-dev.us.auth0.com")

payload = "{\"client_id\":\"82aMcR8vqmLr0mqPMYlQrZiO83vCisVL\",\"client_secret\":\"pv5lhOpn6Zu_P420GV3ThbzoWBeHpKha77u3lxtzZml8WFiCS7wRv9Rq_yatBGV-\",\"audience\":\"http://localhost:8090/\",\"grant_type\":\"client_credentials\"}"

headers = { 'content-type': "application/json" }

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))