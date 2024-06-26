import { App } from "aws-cdk-lib";
import { ApiStack } from "./stacks/ApiStack";
import { DataStack } from "./stacks/DataStack";
import { AuthorizerStack } from "./stacks/AuthorizerStack";
import { LambdaStack } from "./stacks/LambdaStack";



const app = new App();
new DataStack(app, 'ZuoraDataStack');
const lambdaStack = new LambdaStack(app, 'ZuoraLambda')

// const authorizerStack = new AuthorizerStack(app, 'ZuoraAuthorizer');

new ApiStack(app, 'ZuoraApi', {
    // zuoraCallOutLambdaIntegration: lambdaStack.zuoraCallOutLambdaIntegration,
})