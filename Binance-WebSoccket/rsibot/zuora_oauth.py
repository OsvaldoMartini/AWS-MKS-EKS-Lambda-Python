import requests

# Authorization Endpoint URL
authorization_endpoint = "https://api.zuora.com/apps/oauth/token"

# Client Credentials
client_id = "your_client_id"
client_secret = "your_client_secret"
redirect_uri = "your_redirect_uri"

# Authorization Code (received after user authorization)
authorization_code = "authorization_code_received_from_zuora"

# Token Request Parameters
token_request_data = {
    "grant_type": "authorization_code",
    "code": authorization_code,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri
}

# Exchange Authorization Code for Access Token
token_response = requests.post(authorization_endpoint, data=token_request_data)
token_response_data = token_response.json()

# Extract Access Token
access_token = token_response_data["access_token"]

# Make API Request to Zuora
api_url = "https://rest.zuora.com/v1/object/account"
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(api_url, headers=headers)
print(response.json())  # Print Zuora API response
