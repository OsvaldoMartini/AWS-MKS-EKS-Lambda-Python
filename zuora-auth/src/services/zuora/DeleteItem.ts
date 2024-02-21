import { DeleteItemCommand, DynamoDBClient, UpdateItemCommand } from "@aws-sdk/client-dynamodb";
import { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda";
import { hasAdminGroup } from "../shared/Utils";



export async function deleteSpace(event: APIGatewayProxyEvent, ddbClient: DynamoDBClient): Promise<APIGatewayProxyResult> {

    if (!hasAdminGroup(event)) {
        return {
            statusCode: 401,
            body: JSON.stringify(`Not authorized!`)
        }
    }

    if(event.queryStringParameters && ('id' in event.queryStringParameters)) {

        const itemId = event.queryStringParameters['id'];

        await ddbClient.send(new DeleteItemCommand({
            TableName: process.env.TABLE_NAME,
            Key: {
                'id': {S: itemId}
            }
        }));

        return {
            statusCode: 200,
            body: JSON.stringify(`Deleted item with id ${itemId}`)
        }

    }
    return {
        statusCode: 400,
        body: JSON.stringify('Please provide right args!!')
    }

}