
## Firt elect the Profile to Use
```bash
  export AWS_PROFILE=eks-admin

  and/or

  --profile eks-admin
 
```

## Create a Policy for "ks-admin"
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:*",
                "eks:*",
                "ec2:*"
            ],
            "Resource": "*"
        }
    ]
}

```

## Create CloudFormation EKS VPC
```bash
  aws cloudformation create-stack \
  --profile eks-admin \
  --region us-west-2 \
  --stack-name lotto-audit-vpc \
  --template-body file://lottoaudit-eks-vpc-private-subnets.yaml


or

aws cloudformation create-stack --region us-west-2 --stack-name lotto-audit-vpc --template-body file://lottoaudit-eks-vpc-private-subnets.yaml

```


## Create CloudFormation EKS Cluster
```bash
  //  To Create some roles
  //  --capabilities CAPABILITY_NAMED_IAM \      

  aws cloudformation create-stack \
  --region us-west-2 \
  --profile eks-admin \
  --stack-name lotto-audit-eks-cluster \
  --capabilities CAPABILITY_NAMED_IAM \      
  --template-body file://eks-stack.yaml


or

 aws cloudformation create-stack --profile eks-admin --region us-west-2 --stack-name lotto-audit-eks-cluster --capabilities CAPABILITY_NAMED_IAM --template-body file://eks-stack.yaml
```

## Create Cluster from Amazon Instructions
> https://docs.aws.amazon.com/eks/latest/userguide/create-cluster.html
```bash
aws eks create-cluster --region region-code --name my-cluster --kubernetes-version 1.27 \
   --role-arn arn:aws:iam::111122223333:role/myAmazonEKSClusterRole \
   --resources-vpc-config subnetIds=subnet-ExampleID1,subnet-ExampleID2,securityGroupIds=sg-ExampleID1
```

## Accessing EKS 
```bash
  aws eks --region us-west-2 update-kubeconfig --name lotto-audit-eks-cluster
```

## Communicate wit my cluster
```bash
  aws eks update-kubeconfig --region us-west-2 --name lotto-audit-eks-cluster
```


## Get Nodes from my cluster
```bash
  kubectl get nodes
    ip-192-168-151-129.us-west-2.compute.internal   Ready    <none>   90m   v1.27.4-eks-8ccc7ba
    ip-192-168-248-42.us-west-2.compute.internal    Ready    <none>   90m   v1.27.4-eks-8ccc7ba

  kubectl get nodes -o wide

```

## Creating PODs in Imperative Way
```bash

//Imperative
kubectl run pod_dev --image python:3.8-slim


 //Declarative
 kubectl create -f pod_dev.yaml

 kubectl apply -f pod_dev_pub.yaml



```








Throuleshooting
Any Authentication error
```bash
aws eks update-kubeconfig \
    --region us-west-2 \
    --name lotto-audit-eks-cluster \
    --role-arn arn:aws:eks:eu-west-2:287449617086:cluster/lotto-audit-eks-Cluster
    
```
