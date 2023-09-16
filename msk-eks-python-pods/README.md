
## Create pod on EKS
```bash
  
  export AWS_PROFILE=eks-admin
  
  //PowerShell Set Variable
  [System.Environment]::SetEnvironmentVariable('AWS_PROFILE','eks-admin')
  //Print
  $env:AWS_PROFILE 
  //Windows
  set AWS_PROFILE=eks-admin

  //Create a namespace
  kubectl create namespace anum-dev

  // Pode for dev_sub
  kubectl create -f .dev/pod_dev.yaml

  // Pode for dev_pub
  kubectl create -f .dev/pod_dev_pub.yaml

```

## Communicate wit my cluster
```bash
  aws eks update-kubeconfig --region us-west-2 --name lotto-audit-eks-cluster
```

## Creating PODs in Imperative Way
```bash

  kubectl run pod_dev --image python:3.8-slim

```

## K9S interaction and instalations
```bash
  <s>  Shell   -> cmd line insede of the pod, etc.

  apt-get update

  apt-get -y upgrade

  // Install some Tools and Softwares
  apt-get -y install nano vim tar wget default-jre

  // Install Kafka
  wget https://downloads.apache.org/kafka/3.4.1/kafka_2.12-3.4.1.tgz

  // untar
  tar -xzvf kafka_2.12-3.4.1.tgz
  
  //remove zip file
  rm -rf kafka_2.12-3.4.1.tgz

  // Get the AWS IAM Connector
  // Kafka can connects via IAM
  wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.6/aws-msk-iam-auth-1.1.6-all.jar
  
  //Move to Kafka /libs
  mv aws-msk-iam-auth-1.1.6-all.jar kafka_2.12-3.4.1/libs

 // Authentication Kafka credentials
 nano kafka_2.12-3.4.1/client.properties 
 or
 printf 'security.protocol=SASL_SSL  \n
sasl.mechanism=AWS_MSK_IAM              \n
sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;    \n
sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler' >> kafka_2.12-3.4.1/client.properties


export AWS_ACCESS_KEY_ID=AKIAUF3KVCK7PFGQR23Y
export AWS_SECRET_ACCESS_KEY=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

//Create topic
./kafka_2.12-3.4.1/bin/kafka-topics.sh create --bootstrap-server <bootstrap-servers> --replication-factor 2 --partition 1 --topic <topic-name> --command-config ./kafka_2.12-3.4.1/client.properties




```

