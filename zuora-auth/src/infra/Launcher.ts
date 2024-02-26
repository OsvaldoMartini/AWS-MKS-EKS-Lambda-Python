
import {App} from 'aws-cdk-lib';
import { ApiStack } from './stacks/ApiStack';
import { DataStack } from './stacks/DataStack';
import { LambdaStack } from './stacks/LambdaStack';
import { AuthStack } from './stacks/AuthStack';
import { ZuoraOAuth } from './stacks/ZuoraOAuth';

const app = new App();
const dataStack = new DataStack(app, 'ZuoraCallOutData');
const lambdaStack = new LambdaStack(app, 'ZuoraCallOutEntryPoint', {
  zuoraTables:dataStack.zuoraTables});

const authStack = new AuthStack(app, 'ZuoraAuthCognito');

new ApiStack(app, 'ZouraCallOutApi', {
  zuoraCallOutLambdaIntegration: lambdaStack.zuoraCallOutLambdaIntegration,
  userPool: authStack.userPool
});

new ZuoraOAuth(app, 'ZuoraGetTokenOAuth');