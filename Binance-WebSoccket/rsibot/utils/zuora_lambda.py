import boto3
import json

def invoke_lambda_function(function_name, payload_json):
    # Create a boto3 client for Lambda
    lambda_client = boto3.client('lambda')

    # Define parameters for invoking the Lambda function
    params = {
        'FunctionName': function_name,
        'InvocationType': 'RequestResponse',  # Use 'Event' for asynchronous invocation
        'Payload': payload_json
    }

    # Invoke the Lambda function
    response = lambda_client.invoke(**params)

    # Parse and return the response
    response_payload = response['Payload'].read().decode('utf-8')
    return response_payload

def main():
    # Replace 'YourLambdaFunctionName' with the name of your Lambda function
    function_name = 'stage-ME-33737-subscriptionBilling-ChildAccount'
    
    # Define the payload as a dictionary
    payload_dict = "8a8aa2028ef98921018efa7375fa52ec"
    
    # Convert the payload dictionary to a JSON string
    payload_json = json.dumps(payload_dict)
    
    # Invoke the Lambda function
    response = invoke_lambda_function(function_name, payload_dict)
    
    # Print the response
    print(response)

if __name__ == "__main__":
    main()
