import { Stack, StackProps } from "aws-cdk-lib";
import { LambdaIntegration } from "aws-cdk-lib/aws-apigateway";
import { Runtime, Code, Function as LambdaFunction } from "aws-cdk-lib/aws-lambda";
import { ITable } from 'aws-cdk-lib/aws-dynamodb';
import { Construct} from "constructs";
import { join} from 'path';

interface LambdaStackProps extends StackProps{
  zuoraTables: ITable
}

export class LambdaStack extends Stack {

  public readonly zuoraCallOutLambdaIntegration:LambdaIntegration;

  constructor(scope: Construct, id: string, props?: LambdaStackProps) {
    super(scope, id, props)

    const zuoraCallOutLambda =  new LambdaFunction(this, 'ZuoraCallOutLambda', {
      //Runtime
      runtime: Runtime.NODEJS_18_X,
      handler: 'getCallOut.main',
      //Join works with all operation System Now We navigate in the syste like VS Terminal 
      // UP ONE  Levels '..'
      // FOR TWO levels '..', '..'
      code: Code.fromAsset(join(__dirname, '..','..', 'services')),
      environment: {
        TABLE_NAME: props.zuoraTables.tableName
      } 
    })

    this.zuoraCallOutLambdaIntegration = new LambdaIntegration(zuoraCallOutLambda);
  }
}