import requests
import base64

def main():
    client_id = "2ce40d27-796d-4922-8753-0388c196f2a0"
    client_secret = "d6tWFOM5mZznpdpvrZ9KFYi=y1r1NiC7jm2itHU"

    # Step 2: Exchange Client Credentials for Access Token
    token_url = "https://rest.test.zuora.com/oauth/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "client_credentials"
    }

    response = requests.post(token_url, headers=headers, data=payload)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        print("Access Token:", access_token)

        # Step 3: Use the Access Token to make API requests
        # Include the access token in the Authorization header of your API requests to authenticate with Zuora's API
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    main()
