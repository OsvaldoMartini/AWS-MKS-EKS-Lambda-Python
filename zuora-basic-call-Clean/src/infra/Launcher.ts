import { App } from "aws-cdk-lib";
import { ApiStack } from "./stacks/ApiStack";
import { DataStack } from "./stacks/DataStack";
import { LambdaStack } from "./stacks/LambdaStack";
import { ApiGatewayHeaderRequestEventStack } from "./stacks/LambdaZuora";



const app = new App();
new DataStack(app, 'ZuoraDataStack');
const lambdaStack = new LambdaStack(app, 'ZuoraLambda')
new ApiStack(app, 'ZuoraApi', {
    zuoraCallOutLambdaIntegration: lambdaStack.zuoraCallOutLambdaIntegration
})
new ApiGatewayHeaderRequestEventStack(app, 'ApiGatewayHeaderRequestEventStack');