import { Stack, StackProps } from "aws-cdk-lib"
import { LambdaIntegration, RestApi } from "aws-cdk-lib/aws-apigateway"
import { Construct} from "constructs"

interface ApiStackProps extends StackProps {
  zuoraTokenLambdaIntegration : LambdaIntegration;
}

export class ApiStack extends Stack {

  constructor(scope: Construct, id: string, props?: ApiStackProps) {
    super(scope, id, props)

    const api = new RestApi(this, 'ZuoraTokenApi');
    const zouraTokenResource  = api.root.addResource('zuoraToken');
    zouraTokenResource.addMethod('POST', props.zuoraTokenLambdaIntegration);
  }
}