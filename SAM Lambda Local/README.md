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

## Use Tap
```bash
	npm install -g tap 

```

## Use wscat to connect to a WebSocket API and send messages to it
```bash
	npm install -g wscat

  wscat -c wss://aabbccddee.execute-api.us-east-1.amazonaws.com/test/

  wscat -c http://localhost:3000

```

## Translate Servelles Application Model into (SAM) tempate to CloudFormation
[1] https://stackoverflow.com/questions/56226935/get-cloudformation-script-from-sam
```bash
	pip install aws-sam-translator docopt

	wget https://raw.githubusercontent.com/aws/serverless-application-model/develop/bin/sam-translate.py

 # Rename File
	wget -O sam-translate.py https://raw.githubusercontent.com/aws/serverless-application-model/develop/bin/sam-translate.py

	python sam-translate.py --template-file=serverless-example.yml --output-template=serverless-cloudformation.yml

  python sam-translate.py --template-file=template.yaml --output-template=template-cloudformation.yml
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


