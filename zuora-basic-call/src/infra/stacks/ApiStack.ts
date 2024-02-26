import { Stack, StackProps } from 'aws-cdk-lib'
import { Code, Function as LambdaFunction, Runtime, IFunction} from 'aws-cdk-lib/aws-lambda';
import { TokenAuthorizer, LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway'; //MethodOptions, ResourceOptions, 
import { Role, ServicePrincipal, PolicyStatement } from 'aws-cdk-lib/aws-iam';
// import { HttpLambdaAuthorizer, HttpLambdaResponseType } from 'aws-cdk-lib/aws-apigatewayv2-authorizers';
// import { HttpJwtAuthorizer } from 'aws-cdk-lib/aws-apigatewayv2-authorizers';
// import { HttpUrlIntegration, HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations';
// import { HttpMethod } from '@aws-cdk/aws-apigatewayv2';
import { Construct } from 'constructs';
import { join } from 'path';


// interface ApiStackProps extends StackProps {
//     zuoraCallOutLambdaIntegration: LambdaIntegration,
//     // authorizer: IFunction
// }

export class ApiStack extends Stack {

    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

      // API Gateway Definition
      const api = new RestApi(this, "ZuoraCalloutRestApi", {
        restApiName: "Zuora Call Out  API",
        description: "This API exposes Zuora call outs."
      });

      const JWKS_ENDPOINT = `https://${process.env.DOMAIN_NAME}${process.env.JWKS_URI}`

      // Lambda Authorizer
      const LambdaAuthorizeRole = new Role(this, 'LambdaAuthorizerRole', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
      });

    LambdaAuthorizeRole.addToPolicy(new PolicyStatement({
      resources: ['*'],
      actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents', 'secretsmanager:GetSecretValue', 'sts:AssumeRole'],
    }));
      
    const jwtAuthorizer = new LambdaFunction(this, "LambdaAuthHandler", {
      runtime: Runtime.NODEJS_18_X,
      handler: 'authorizer.handler',
      code: Code.fromAsset(join(__dirname, '..','..', 'services/shared')),
      role: LambdaAuthorizeRole,
      environment: {
        JWKS_ENDPOINT: JWKS_ENDPOINT,
        API_ID: api.restApiId,
        ACCOUNT_ID: <string>process.env.CDK_DEFAULT_ACCOUNT,
        SM_JWKS_SECRET_NAME: <string>process.env.SM_JWKS_SECRET_NAME
      }
    });

    // Lambda Backend Integration
    const backendHandler = new LambdaFunction(this, "BackendHandler", {
      runtime: Runtime.NODEJS_18_X,
      code: Code.fromAsset(join(__dirname, '..','..', 'services/shared')),
      handler: "backend.handler"
    });


    // Add Lambda Authorizer to Gateway
    const authorizer = new TokenAuthorizer(this, 'JWTAuthorizer', {
      handler: jwtAuthorizer,
      validationRegex: "^(Bearer )[a-zA-Z0-9\-_]+?\.[a-zA-Z0-9\-_]+?\.([a-zA-Z0-9\-_]+)$"
    });

    // Create Protected Resource
    const getApiIntegration = new LambdaIntegration(backendHandler, {
      requestTemplates: { "application/json": '{ "statusCode": "200" }' }
    });

    // Define HTTP Method for Resource with Lambda Authorizer
    api.root.addMethod("GET", getApiIntegration, { authorizer }); // GET 

    // ------ END OF API GATEWAY CONFIGURATION

      //   const authorizerLambda = new LambdaFunction(this, 'AuthorizerLambda', {
      //     runtime: Runtime.NODEJS_18_X,
      //     handler: 'authorizer.handler',
      //     code: Code.fromAsset(join(__dirname, '..','..', 'services/shared'))
      // })

        // const authorizer = new RequestAuthorizer(this, 'ZuoraAuthorizer', {
        //   handler: authorizerLambda,
        //   identitySources: [IdentitySource.header('Authorization')]
        // });
        // const spacesResource = api.root.addResource('zuoraCallOut');
        // //spacesResource.addMethod('GET', new HttpIntegration('http://amazon.com'), {
        // spacesResource.addMethod('GET', props.zuoraCallOutLambdaIntegration, {authorizer: authorizer});
        // // spacesResource.addMethod('GET', props.zuoraCallOutLambdaIntegration);

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