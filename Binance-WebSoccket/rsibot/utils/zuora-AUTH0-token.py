import http.client

conn = http.client.HTTPSConnection("me-dev.us.auth0.com")

payload = "{\"client_id\":\"28GeMcq4wAiZ7ufKr0TmDArwwfZTqtfS\",\"client_secret\":\"uom5RIGgi_OBNCau7loI3elGmPycLdDxXZKOAY9KiCNGm69Kc0MA2TE1g72PxHXa\",\"audience\":\"http://localhost:8090/\",\"grant_type\":\"client_credentials\"}"

headers = { 'content-type': "application/json" }

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))