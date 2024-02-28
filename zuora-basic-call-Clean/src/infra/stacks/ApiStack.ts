import { Stack, StackProps } from 'aws-cdk-lib'
import { LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

interface ApiStackProps extends StackProps {
    zuoraCallOutLambdaIntegration: LambdaIntegration
}

export class ApiStack extends Stack {

    constructor(scope: Construct, id: string, props: ApiStackProps) {
        super(scope, id, props);

        const api = new RestApi(this, 'ZuoraCalloutRestApi');
        const spacesResource = api.root.addResource('callOut');
        spacesResource.addMethod('GET', props.zuoraCallOutLambdaIntegration)
    }
}