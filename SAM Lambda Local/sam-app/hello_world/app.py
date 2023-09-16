import json

def lambda_handler(event, context):

    body = json.loads(event["body"])
    first_name = body["first_name"]
    last_name = body["last_name"]
    message = body["message"]

    print(f"{message} {first_name} {last_name}")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"{message} {first_name} {last_name}"
        }),
    }