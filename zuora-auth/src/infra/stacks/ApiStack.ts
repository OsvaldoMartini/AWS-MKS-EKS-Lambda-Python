import { Stack, StackProps } from "aws-cdk-lib"
import { AuthorizationType, CognitoUserPoolsAuthorizer, Cors, LambdaIntegration, MethodOptions, ResourceOptions, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Construct} from "constructs"

import { IUserPool } from 'aws-cdk-lib/aws-cognito';

interface ApiStackProps extends StackProps {
  zuoraTokenLambdaIntegration : LambdaIntegration;
  userPool: IUserPool;
}

export class ApiStack extends Stack {

  constructor(scope: Construct, id: string, props?: ApiStackProps) {
    super(scope, id, props)

    const api = new RestApi(this, 'ZuoraTokenApi');

    const authorizer = new CognitoUserPoolsAuthorizer(this, 'ZuoraApiAuthorizer', {
      cognitoUserPools:[props.userPool],
      identitySource: 'method.request.header.Auhtorization'
    });
    authorizer._attachToApi(api);

      const optionsWithAuth: MethodOptions = {
            authorizationType: AuthorizationType.COGNITO,
            authorizer: {
                authorizerId: authorizer.authorizerId
            }
        }


    const zouraTokenResource  = api.root.addResource('zuoraToken');
    zouraTokenResource.addMethod('GET', props.zuoraTokenLambdaIntegration, optionsWithAuth);
    zouraTokenResource.addMethod('POST', props.zuoraTokenLambdaIntegration, optionsWithAuth);
    zouraTokenResource.addMethod('PUT', props.zuoraTokenLambdaIntegration, optionsWithAuth);
    zouraTokenResource.addMethod('DELETE', props.zuoraTokenLambdaIntegration, optionsWithAuth);
  }
}