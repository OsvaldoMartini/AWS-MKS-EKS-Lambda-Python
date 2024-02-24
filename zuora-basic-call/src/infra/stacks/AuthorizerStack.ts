import { Stack, StackProps } from 'aws-cdk-lib'
import { Code, Function as LambdaFunction, Runtime, IFunction} from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { join } from 'path';



export class AuthorizerStack extends Stack {

    public readonly authorizer: IFunction

    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props)

        const authorizerLambda = new LambdaFunction(this, 'AuthorizerLambda', {
            runtime: Runtime.NODEJS_18_X,
            handler: 'authorizer.handler',
            code: Code.fromAsset(join(__dirname, '..','..', 'services/shared'))
        })
        this.authorizer = authorizerLambda;
    }
}