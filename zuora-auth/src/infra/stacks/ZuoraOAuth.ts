import { Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import {
  HttpIntegration,
  PassthroughBehavior,
  RestApi,
} from "aws-cdk-lib/aws-apigateway";

export class ZuoraOAuth extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Create an API Gateway
    const api = new RestApi(this, "ZuoraApi", {
      restApiName: "Zuora API Gateway",
      description: "API Gateway to interact with Zuora",
    });

    // Resource and method
    const zuoraResource = api.root.addResource("ZuoraGetOAuth");
    const integration = new HttpIntegration(
      "https://rest.test.zuora.com/oauth/token",
      {
        httpMethod: "POST",
        options: {
          // Specify the content handling strategy
          integrationResponses: [
            {
              statusCode: "200",
              responseTemplates: {
                // Define response templates if needed
              },
            },
          ],
          requestParameters: {
            // Define any request parameters if needed
          },
          requestTemplates: {
            "application/x-www-form-urlencoded": "$input.body",
          },
          passthroughBehavior: PassthroughBehavior.NEVER,
        },
      }
    );

    zuoraResource.addMethod("POST", integration);
  }
}
