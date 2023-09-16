# Must have Docker

## SAM Uses Docker to simulate Lambda, Gateways, etc.

```bash
  mkdir sam-project

  sam -h  # To see al commands

  sam init

  1 - AWS Quick Start Templates

  2 - zip # Because we are not deploy on ECR

  3 - python

  4 - Hello Example


  sam build

  # It Creates the folder
  ".aws-sam"
```


## Deploy On AWS S3
```bash
 # It creates S3 Bucket  - one time creation 
 sam deploy --guided # It creates S3 Bucket  - one time creation

 We can see 2 Stacks
  - sam-app 
  - aws-sam ....(One time deploy)
```

## Deploy LOCAL
```bash

```

## Test locally
```bash

  sam local invoke HelloWorldFunction -e events/event.json
  
```

## Running API Gateway locally
```bash
  sam local start-api -d 5858 # Debugging

  # Throubleshooting
  > Template does not have any APIs connected to Lambda functions
```


