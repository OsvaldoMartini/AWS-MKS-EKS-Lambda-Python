# How to Setup NGINX Ingress Controller in Kubernetes
* Ingress is one of the important concepts in Kubernetes, which allows external users to access containerized application using <span style="color: yellow;">FQDN (fully qualified domain name).</span> Though Ingress is not enabled and installed by default in Kubernetes cluster. We must enable to this core concept using third party ingress controllers like <span style="color:  #99ccff;">Nginx, Traefik, HAProxy</span> and <span style="color:  #99ccff;">Istio</span> etc.
----------------------------------------------------------------
* In this tutorial we will demonstrate how to setup and use NGINX Ingress controller in Kubernetes Cluster.

* As above picture, external users are accessing applications using NGINX Ingress Controller via FQDN and internal ingress controller routes the request to service and then service routes the request to backend end points or pods.
----------------------------------------------------------------

## Enable NGINX Ingress Controller in Minikube
* [Minikube](https://www.linuxtechi.com/install-minikube-on-rhel-rockylinux-almalinux/) is a single node Kubernetes cluster, we can easily enable nginx ingress controller in minikube by running <span style="color: #99ccff;">“minikube addons”</span> command.

Run below command to verify the status of ingress controller
```bash
  minikube addons list
```