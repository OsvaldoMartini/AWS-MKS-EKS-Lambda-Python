## EKSCTL  Kuberbetes Cluster
> Instal EKSCTL from AWS EKSCTL Pages
```bash
	eksctl create cluster \
	--name lottoaudit-eks-cluster \
	--version 1.27 \
	--region us-west-2 \
	--nodegroup-name lottoaudit-linux-nodes
	--node-type t2.micro \
	--nodes 2
```
## Delete cluster
```bash
		eksctl delete cluster \
	--name lotto-audit-eks-Cluster \
```


## K9s Install
```bash
	choco install k9s
```