import { Stack, StackProps } from "aws-cdk-lib";
import { LambdaIntegration } from "aws-cdk-lib/aws-apigateway";
import { Runtime, Code, Function as LambdaFunction } from "aws-cdk-lib/aws-lambda";
import { Construct} from "constructs";
import { join} from 'path';


export class LambdaStack extends Stack {

  public readonly zuoraTokenLambdaIntegration:LambdaIntegration;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)

    const zuoraTokenLambda =  new LambdaFunction(this, 'ZuoraGetTokenLambda', {
      //Runtime
      runtime: Runtime.NODEJS_18_X,
      handler: 'getZuoraToken.main',
      //Join works with all operation System Now We navigate in the syste like VS Terminal 
      // UP ONE  Levels '..'
      // FOR TWO levels '..', '..'
      code: Code.fromAsset(join(__dirname, '..','..', 'services')), 
    })

    this.zuoraTokenLambdaIntegration = new LambdaIntegration(zuoraTokenLambda);
  }
}