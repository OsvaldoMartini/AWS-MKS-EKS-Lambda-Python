# Amazon EventBridge Scheduler to call AWS Lambda

The CDK stack deploys a Lambda function and schedules its execution using AWS EventBridge Scheduler.

Learn more about this pattern at Serverless Land Patterns: https://serverlessland.com/patterns/event-bridge-scheduler-lambda-cdk-dotnet

Important: this application uses various AWS services and there are costs associated with these services after the Free Tier usage - please see the [AWS Pricing page](https://aws.amazon.com/pricing/) for details. You are responsible for any AWS costs incurred. No warranty is implied in this example.

## Requirements

* [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
* [Git Installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [.NET 6](https://dotnet.microsoft.com/en-us/download/dotnet/6.0) installed
* [AWS Cloud Development Kit](https://docs.aws.amazon.com/cdk/latest/guide/cli.html) (AWS CDK) installed

## Deployment Instructions

1. Clone the project to your local working directory
    ```
    git clone https://github.com/aws-samples/serverless-patterns
    ```
2. Change the working directory to this pattern's directory
    ```
    cd event-bridge-scheduler-lambda-cdk-dotnet/cdk/src
    ```
3. Build the application
    ```
    dotnet build
    ```
4. Return one level back to the path `event-bridge-scheduler-lambda-cdk-dotnet/cdk`
    ```
    cd..
    ```
5. Deploy the stack to your default AWS account and region.
    ```
    cdk deploy
    ```

## Testing

In AWS Console, wait for the scheduled event to trigger the Lambda function. Once the event is triggered, check the CloudWatch Logs for the Lambda function to verify that it was executed successfully.

## Cleanup
Run the given command to delete the resources that were created. It might take some time for the CloudFormation stack to get deleted.
```
cdk destroy
```

----
Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: MIT-0
