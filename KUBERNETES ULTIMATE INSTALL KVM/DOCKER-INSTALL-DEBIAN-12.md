# Docker Install Dbian 12


1) Update Apt Package Index
Login to your Debian 12  system, open the terminal and run below command to update apt package index

```bash
$ sudo apt update

$ sudo apt install -y ca-certificates curl gnupg
```

2) Add Docker Repository
```bash
$ sudo install -m 0755 -d /etc/apt/keyrings

$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

$ sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Next, run echo command to add official docker repository.
```bash
$ echo \
"deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
3) Install Docker Engine
```bash
$ sudo apt update

$ sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

Once the docker is installed successfully then it’s service starts automatically. Verify its version and service status by running,
```bash

$ sudo docker version

$ sudo systemctl status docker
```

4) Verify Docker Installation
```bash
$  sudo docker run hello-world
```
5) Allow Local User to Run Docker Command
To allow local user to run docker commands without sudo, add the user to docker group (secondary group) using usermod command.

```bash

$ sudo usermod -aG docker $USER

$ newgrp docker
```

## Removal of Docker
```bash
$ sudo apt purge docker-ce docker-ce-cli containerd.io \
docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras -y

$ sudo rm -rf /var/lib/docker

$ sudo rm -rf /var/lib/containerd
```
