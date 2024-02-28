import { Stack, StackProps } from "aws-cdk-lib"
import { AuthorizationType, CognitoUserPoolsAuthorizer, Cors, LambdaIntegration, MethodOptions, ResourceOptions, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Construct} from "constructs"

import { IUserPool } from 'aws-cdk-lib/aws-cognito';  

interface ApiStackProps extends StackProps {
  zuoraCallOutLambdaIntegration : LambdaIntegration;
  userPool: IUserPool;
}

export class ApiStack extends Stack {

  constructor(scope: Construct, id: string, props?: ApiStackProps) {
    super(scope, id, props)

    const api = new RestApi(this, 'ZuoraCallOutRestApi');

    const authorizer = new CognitoUserPoolsAuthorizer(this, 'ZuoraApiAuthorizer', {
      cognitoUserPools:[props.userPool],
      identitySource: 'method.request.header.Auhtorization'
    });
    authorizer._attachToApi(api);

    const optionsWithAuth: MethodOptions = {
          authorizationType: AuthorizationType.CUSTOM,
          authorizer: {
              authorizerId: authorizer.authorizerId
          }
      }


    const zouraCallOutResource  = api.root.addResource('zuoraCallout');
    zouraCallOutResource.addMethod('GET', props.zuoraCallOutLambdaIntegration, optionsWithAuth);
    zouraCallOutResource.addMethod('POST', props.zuoraCallOutLambdaIntegration, optionsWithAuth);
    zouraCallOutResource.addMethod('PUT', props.zuoraCallOutLambdaIntegration, optionsWithAuth);
    zouraCallOutResource.addMethod('DELETE', props.zuoraCallOutLambdaIntegration, optionsWithAuth);
  }
}