

## Choco install kubernetes-cli
```bash
	choco install kubernetes-cli --force
```


## K9s Install
```bash
	choco install k9s
```


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
  kubectl create namespace shifthunter

  // Pode for dev_sub
  kubectl create -f .dev/pod_dev.yaml

  // Pode for dev_pub
  kubectl create -f .dev/pod_dev_pub.yaml


  //Create a namespace
  kubectl create namespace first-cluster

 //CDRs Install first
 curl -L http://strimzi.io/install/latest sed 's/namespace: .*/namespace: kafka/' | kubectl apply -f - -n kafka

curl -L http://strimzi.io/install/latest sed 's/namespace: .*/namespace: first-cluster/' | kubectl apply -f - -n kafka

  kubectl create -f kafka-deployment-metric.yaml	

```

## Communicate wit my cluster
```bash
  aws eks update-kubeconfig --region us-west-2 --name lotto-audit-eks-cluster
```

## Creating PODs in Imperative Way
```bash

  kubectl run pod_dev --image python:3.8-slim

```

## Install Kubernete zinside a pod
```bash
	sudo apt-get update && sudo apt-get install -y apt-transport-https
	curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmour -o /usr/share/keyrings/kubernetes.gpg
	echo "deb [arch=amd64 signed-by=/usr/share/keyrings/kubernetes.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
	sudo apt-get update
	sudo apt-get install -y kubectl
```

## Describe pod
```bash
	kubectl exec -it kafka-publisher -- /bin/bash -c "cat /etc/os-release;uname -r"
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

  //Kafka Brokers
  nano kafka_2.12-3.4.1/client.properties 

  nano /kafka_2.12-3.4.1/config/zookeeper.properties
  
	printf 'dataDir=/usr/local/kafka_2.12-3.4.1/zookeeper-logs \n
		clientPort=2181 \n
		maxClientCnxns=0 \n
		admin.enableServer=false \n' >> kafka_2.12-3.4.1/config/zookeeper.properties
	
	
	dataDir=/usr/local/kafka_2.12-3.4.1/zookeeper-logs
	clientPort=2181
	maxClientCnxns=0
	admin.enableServer=false
	
	//Start zookeeper
  ./kafka_2.12-3.4.1/bin/zookeeper-server-start.sh kafka_2.12-3.4.1/config/zookeeper.properties


 Get the AWS IAM Connector
  // Kafka can connects via IAM
  wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.6/aws-msk-iam-auth-1.1.6-all.jar
  
  //Move to Kafka /libs
  mv aws-msk-iam-auth-1.1.6-all.jar kafka_2.12-3.4.1/libs

 // Authentication Kafka credentials
 nano kafka_2.12-3.4.1/client.properties 
 
	security.protocol=SASL_SSL
	sasl.mechanism=AWS_MSK_IAM
	sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;
	sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler

 or
	
	printf 'security.protocol=SASL_SSL  \n
	sasl.mechanism=AWS_MSK_IAM              \n
	sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;    \n
	sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler' >> kafka_2.12-3.4.1/client.properties


export AWS_ACCESS_KEY_ID=AKIAUF3KVCK7PFGQR23Y
export AWS_SECRET_ACCESS_KEY=nl94vmC2mEfCcdbFxNylg18bQRvk7WThetK5q8S0

# If Not on AWS
# Run Kafak in your Local Kubernetes Pod
./kafka_2.12-3.4.1/bin/kafka-server-start.sh --create --
kafka_2.12-2.5.0\bin\windows\kafka-server-start.bat C:\Martini\kafka_2.12-2.5.0\config\server-0.properties

//Create topic
./kafka_2.12-3.4.1/bin/kafka-topics.sh --create --bootstrap-server <bootstrap-servers> --replication-factor 2 --partitions 1 --topic <topic-name> --command-config ./kafka_2.12-3.4.1/client.properties


./kafka_2.12-3.4.1/bin/kafka-server-start.sh kafka_2.12-3.4.1/config/server-0.properties


./kafka_2.12-3.4.1/bin/kafka-topics.sh --create --bootstrap-server http://localhost:9093 --replication-factor 2 --partitions 1 --topic test-topic --command-config ./kafka_2.12-3.4.1/client.properties


```

## kubectl config
```bash

  kubectl config get-contexts
  
  Available Commands:
  current-context   Display the current-context
  delete-cluster    Delete the specified cluster from the kubeconfig
  delete-context    Delete the specified context from the kubeconfig
  delete-user       Delete the specified user from the kubeconfig
  get-clusters      Display clusters defined in the kubeconfig
  get-contexts      Describe one or many contexts
  get-users         Display users defined in the kubeconfig
  rename-context    Rename a context from the kubeconfig file
  set               Set an individual value in a kubeconfig file
  set-cluster       Set a cluster entry in kubeconfig
  set-context       Set a context entry in kubeconfig
  set-credentials   Set a user entry in kubeconfig
  unset             Unset an individual value in a kubeconfig file
  use-context       Set the current-context in a kubeconfig file
  view              Display merged kubeconfig settings or a specified kubeconfig file
  

```

