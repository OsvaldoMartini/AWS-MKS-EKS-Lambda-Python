# Amazon API Gateway data validation models

This pattern creates an Amazon API Gateway with a usage plan that demonstrates stage level quotas and throttling as well as method level throttling.

Learn more about this pattern at Serverless Land Patterns: [https://serverlessland.com/patterns/apigw-usage-plans](https://serverlessland.com/patterns/apigw-usage-plans)

Important: this application uses various AWS services and there are costs associated with these services after the Free Tier usage - please see the [AWS Pricing page](https://aws.amazon.com/pricing/) for details. You are responsible for any AWS costs incurred. No warranty is implied in this example.

## Requirements

* [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
* [Git Installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) (AWS SAM) installed

## Deployment Instructions

1. Create a new directory, navigate to that directory in a terminal and clone the GitHub repository:
    ``` 
    git clone https://github.com/aws-samples/serverless-patterns
    ```
1. Change directory to the pattern directory:
    ```
    apigw-usage-plans
    ```
1. From the command line, use AWS SAM to deploy the AWS resources for the pattern as specified in the template.yml file:
    ```
    sam deploy --guided
    ```
1. During the prompts:
    * Enter a stack name
    * Enter the desired AWS Region
    * Allow SAM CLI to create IAM roles with the required permissions.

    Once you have run `sam deploy --guided` mode once and saved arguments to a configuration file (samconfig.toml), you can use `sam deploy` in future to use these defaults.

1. Note the outputs from the SAM deployment process. These contain the resource names and/or ARNs which are used for testing.

## How it works

The stack creates an Amazon API Gteway REST API with a Usage Plan and an API Key for testing. The usage plan limits requests to 15 requests per second with a burst limit of 30 on the entire stage. However, the `/plantest/POST:` endpoint has an override of 5 requests per second with a burst rate of 10. 

## Testing

1. Obtain the API Key value: In the API Gateway console of the newly created API, navigate to *API Keys* on the left menu. Click on the created key and click *Show* to get the value.
2. Update the values in the folllowing and use this curl command to test.
```
curl --location <API endpoint> --header 'x-api-key: <API key>'
```
## Cleanup
 
1. Delete the stack
    ```bash
    sam delete --stack-name STACK_NAME
    ```
1. Confirm the stack has been deleted
    ```bash
    aws cloudformation list-stacks --query "StackSummaries[?contains(StackName,'STACK_NAME')].StackStatus"
    ```
----
Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: MIT-0
