from zeep import Client

# Zuora SOAP API WSDL URL
# wsdl = 'https://www.zuora.com/apps/services/a/zuora-sandbox-wsdl-v83?wsdl'
wsdl = 'https://apisandbox.zuora.com/apps/servlet/GenerateWsdl?version=83'

# Zuora API username and password
username = 'omartini@marginedge.com_sandbox'
password = 'Martini!383940'

# Create a Zeep SOAP client
client = Client(wsdl)

# Authenticate with Zuora
session = client.service.login(username, password)

# Print the session ID
print("Session ID:", session)
