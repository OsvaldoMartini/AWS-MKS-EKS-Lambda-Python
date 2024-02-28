import { Stack, StackProps } from 'aws-cdk-lib'
import { LambdaIntegration } from 'aws-cdk-lib/aws-apigateway';
import { Code, Function as LambdaFunction, Runtime} from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { join } from 'path';


export class LambdaStack extends Stack {

    public readonly zuoraCallOutLambdaIntegration: LambdaIntegration

    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props)


        const zuoraCallOutLambda = new LambdaFunction(this, 'ZouraCallOutLambda', {
            runtime: Runtime.NODEJS_18_X,
            handler: 'zuoraCallOut.main',
            code: Code.fromAsset(join(__dirname, '..','..', 'services'))
        })

        this.zuoraCallOutLambdaIntegration = new LambdaIntegration(zuoraCallOutLambda)

    }
}