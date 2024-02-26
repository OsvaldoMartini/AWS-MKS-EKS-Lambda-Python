import {  APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import jwt from 'jsonwebtoken';

export async function handler(event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> {
  try {
    // Extract JWT token from the Authorization header
    const token = event.headers?.Authorization?.split(' ')[1];
    
    // Verify and decode the JWT token
    const decodedToken = jwt.verify(token, 'your_secret_key_here') as { [key: string]: any };
    
    // Your application logic here
    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Authorized', user: decodedToken }),
    };
  } catch (error) {
    return {
      statusCode: 401,
      body: JSON.stringify({ message: 'Unauthorized' }),
    };
  }
}
