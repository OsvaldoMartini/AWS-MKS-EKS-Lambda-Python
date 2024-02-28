import { Stack, StackProps } from 'aws-cdk-lib'
import { LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Code, Function as LambdaFunction, Runtime} from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';


export class ApiGatewayHeaderRequestEventStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)


    // Lambda function
    const handler = new LambdaFunction(this, 'ZuoraLambdaFunction', {
      runtime: Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: Code.fromInline(`
        exports.handler = async (event) => {
          // Log the headers
          console.log('Headers:', event.headers);

          return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Success' }),
          };
        };
      `),
    });

    // API Gateway
    const api = new RestApi(this, 'ZuoraHeaderGateway');

    // Lambda integration
    const lambdaIntegration = new LambdaIntegration(handler);

    const spacesResource = api.root.addResource('callOutHeader');
    spacesResource.addMethod('GET', lambdaIntegration)
  }
}
