# Get Create Set Context on Kubernetes
## Viewing the Kubernetes Configuration
```bash
$ kubectl config view
```
* Finding the Current Context in Kubectl
```bash
$ kubectl config current-context
```
* Listing Kubernetes Contexts
```bash
$ kubectl config get-contexts
```
## Creating a new Context
* The kubectl config set-context command is used to create a new context in a kubeconfig file.
```bash
$ kubectl config set-context <context-name> --namespace=<namespace-name> --user=<user-name> --cluster=<cluster-name>

# IMPORTANT NOTE
# last context configured
kubectl config set-context kubernetes-admin@kubernetes 


```

## Switching Kubernetes Contexts
* If you want to switch to a different Kubernetes context, you can use the kubectl config use-context command below.
```bash
$ kubectl config use-context <context-name>
```
## Best Practices When Using <span style="color: yellow;">kubectl config set-context</span>
* Switching between contexts is common when working with Kubernetes. 
* You can set aliases for your most frequently used contexts to make it easier. 
* For example, you could define an alias in your <span style="color: yellow;">~/.bashrc</span> file or your shell configuration file as shown below.
```bash
alias k8s-prod='kubectl config use-context production'
```
## Deleting a Kubernetes Context
```bash
$ kubectl config delete-context <context-name>

```


