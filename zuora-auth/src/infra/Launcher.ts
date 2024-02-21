
import {App} from 'aws-cdk-lib';
import { ApiStack } from './stacks/ApiStack';
import { DataStack } from './stacks/DataStack';
import { LambdaStack } from './stacks/LambdaStack';
import { AuthStack } from './stacks/AuthStack';
import { ZuoraOAuth } from './stacks/ZuoraOAuth';

const app = new App();
const dataStack = new DataStack(app, 'DataStack');
const lambdaStack = new LambdaStack(app, 'ZuoraGetTokenLambda', {
  zuoraTables:dataStack.zuoraTables});

const authStack = new AuthStack(app, 'AuthStack');

new ApiStack(app, 'ApiStack', {
  zuoraTokenLambdaIntegration: lambdaStack.zuoraTokenLambdaIntegration,
  userPool: authStack.userPool
});

new ZuoraOAuth(app, 'ZuoraOAuth');
