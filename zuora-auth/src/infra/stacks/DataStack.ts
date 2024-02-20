import { Stack, StackProps } from "aws-cdk-lib"
import { Construct} from "constructs"
import { AttributeType, ITable, Table } from 'aws-cdk-lib/aws-dynamodb';
import { getSuffixFromStack} from "../Utils";

export class DataStack extends Stack {
  
  public readonly zuoraTables: ITable;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)

    const suffix = getSuffixFromStack(this);

    this.zuoraTables =  new Table(this, "ZuoraTables", {
      partitionKey : {
        name: 'id',
        type: AttributeType.STRING
      },
      tableName:  `ZuoraTable-${suffix}`// Very Important to be Individual 
    })
  }
}