import requests
import sys

# Enable verbose output
requests_log = sys.stderr

# From Zuora Specification
#
#   curl --location --request POST 'https://rest.zuora.com/oauth/token' \
#         --header 'Content-Type: application/x-www-form-urlencoded' \
#         --data-urlencode 'client_id={{your client ID}}' \
#         --data-urlencode 'client_secret={{your client secret}}' \
#         --data-urlencode 'grant_type=client_credentials'



# Application base URLs of Zuora Central Sandbox:
# For the US Data Center customers: https://test.zuora.com
# For the EU Data Center customers: https://test.eu.zuora.com
# API base URLs of Zuora Central Sandbox
# For the US Data Center customers:
# For REST API: https://rest.test.zuora.com 
# For SOAP API: https://test.zuora.com
# For the EU Data Center customers:
# For REST API: https://rest.test.eu.zuora.com 



# Zuora OAuth Token Endpoint
token_endpoint_prod_rest_api = "https://rest.zuora.com/oauth/token"
test_endpoint_us_data_center = "https://test.zuora.com"
test_endpoint_eu_data_center = "https://test.eu.zuora.com"
test_endpoint_us_rest_api = "https://rest.test.zuora.com/oauth/token"
test_endpoint_us_soap_api = "https://test.zuora.com"
test_endpoint_eu_data_center_rest_api = "https://rest.test.eu.zuora.com"

# Client Credentials
client_id = "f50b1c58-c026-49e5-860c-13dc699a6940"
client_secret = "+d2Z+MJc5hEXSqBH9kn=/28TBE8FWGzxtT91ht"

# Token Request Parameters
token_request_data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
}

# Make Token Request
token_response = requests.post(test_endpoint_us_rest_api, data=token_request_data,  stream=requests_log)

# Check if request was successful
if token_response.status_code == 200:
    # Parse Token Response
    token_data = token_response.json()
    access_token = token_data['access_token']
    token_type = token_data['token_type']
    expires_in = token_data['expires_in']

    # Accessing response content or any other operation
    print(token_request_data)

    print("Access Token:", access_token)
    print("Token Type:", token_type)
    print("Expires In:", expires_in, "seconds")
    
    
else:
    print("Failed to obtain OAuth token. Status code:", token_response.status_code)
    print("Response:", token_response.text)
