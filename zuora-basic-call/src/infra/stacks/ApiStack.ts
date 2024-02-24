import { Stack, StackProps } from 'aws-cdk-lib'
import { Code, Function as LambdaFunction, Runtime, IFunction} from 'aws-cdk-lib/aws-lambda';
import { RequestAuthorizer, IdentitySource, LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway'; //MethodOptions, ResourceOptions, 
// import { HttpLambdaAuthorizer, HttpLambdaResponseType } from 'aws-cdk-lib/aws-apigatewayv2-authorizers';
// import { HttpJwtAuthorizer } from 'aws-cdk-lib/aws-apigatewayv2-authorizers';
// import { HttpUrlIntegration, HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations';
// import { HttpMethod } from '@aws-cdk/aws-apigatewayv2';
import { Construct } from 'constructs';
import { join } from 'path';


interface ApiStackProps extends StackProps {
    zuoraCallOutLambdaIntegration: LambdaIntegration,
    // authorizer: IFunction
}

export class ApiStack extends Stack {

    constructor(scope: Construct, id: string, props: ApiStackProps) {
        super(scope, id, props);

        const authorizerLambda = new LambdaFunction(this, 'AuthorizerLambda', {
          runtime: Runtime.NODEJS_18_X,
          handler: 'authorizer.handler',
          code: Code.fromAsset(join(__dirname, '..','..', 'services/shared'))
      })

        const authorizer = new RequestAuthorizer(this, 'ZuoraAuthorizer', {
          handler: authorizerLambda,
          identitySources: [IdentitySource.header('Authorization')]
        });

        const api = new RestApi(this, 'ZuoraCalloutRestApi');
        const spacesResource = api.root.addResource('zuoraCallOut');
        //spacesResource.addMethod('GET', new HttpIntegration('http://amazon.com'), {
        spacesResource.addMethod('GET', props.zuoraCallOutLambdaIntegration, {authorizer: authorizer});
        // spacesResource.addMethod('GET', props.zuoraCallOutLambdaIntegration);

        // const issuer = 'https://test.us.auth0.com';
        // const authorizer = new HttpJwtAuthorizer('DefaultAuthorizer', issuer, {
        //   jwtAudience: ['3131231'],
        // });

        // const api = new apigwv2.HttpApi(this, 'HttpApi', {
        //   defaultAuthorizer: authorizer,
        //   defaultAuthorizationScopes: ['manage:books'],
        // });

          // api.addRoutes({
          //   integration: new HttpUrlIntegration('HpptIntegration', 'https://another-url'),
          //   path: '/external-uri',
          //   methods: [HttpMethod.GET],
          //   authorizer,
          // });
          
          // api.addRoutes({
          //   integration: props.zuoraCallOutLambdaIntegration,
          //   path: '/external-uri',
          //   methods: [HttpMethod.GET],
          //   authorizer,
          // });
         
    }
}