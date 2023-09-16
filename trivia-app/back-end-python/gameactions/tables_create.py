
import boto3

DYNAMODB = boto3.resource('dynamodb',
                          aws_access_key_id="anything",
                          aws_secret_access_key="anything",
                          region_name="us-west-2",
                          endpoint_url="http://localhost:8000")

table = DYNAMODB.create_table(
    TableName='mock-table',
    KeySchema=[
        {
            'AttributeName': 'gameId',
            'KeyType': 'HASH'  #Partition_key
        },
        {
            'AttributeName': 'connectionId',
            'KeyType': 'RANGE'  #Sort_key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'connectionId',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'gameId',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    }
)

print("Table status:", table.table_status)
print("Tables:", DYNAMODB.tables.all())