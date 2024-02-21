import * as cdk from '@aws-cdk/core';
import * as apigateway from '@aws-cdk/aws-apigateway';

export class ZuoraApiGatewayStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create an API Gateway
    const api = new apigateway.RestApi(this, 'ZuoraApi', {
      restApiName: 'Zuora API Gateway',
      description: 'API Gateway to interact with Zuora',
    });

    // Define Zuora resource
    const zuora = api.root.addResource('zuora');

    // Define Zuora OAuth authorizer
    const authorizer = new apigateway.CfnAuthorizer(this, 'ZuoraOAuthAuthorizer', {
      restApiId: api.restApiId,
      name: 'ZuoraOAuthAuthorizer',
      type: apigateway.AuthorizationType.OAUTH2,
      identitySource: 'method.request.header.Authorization',
      providerArns: ['arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_abc123'], // Replace with your Cognito User Pool ARN
    });

    // Add GET method to Zuora resource
    zuora.addMethod('GET', new apigateway.HttpIntegration('https://api.zuora.com', {
      options: {
        authorizationType: apigateway.AuthorizationType.OAUTH2,
        authorizerId: authorizer.ref,
      },
    }));
  }
}

// const app = new cdk.App();
// new ZuoraApiGatewayStack(app, 'ZuoraApiGatewayStack');
