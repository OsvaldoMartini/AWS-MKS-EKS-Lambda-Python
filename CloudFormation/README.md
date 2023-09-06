
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

