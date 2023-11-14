# Ansible Automation Tooll install

[Ansible Install](https://www.linuxtechi.com/install-ansible-automation-tool-debian10/)

```bash


sudo apt update


echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main" | sudo tee -a /etc/apt/sources.list

sudo apt install ansible -y

sudo ansible --version

sudo ansible target1 -m ping --ask-pass inventory.txt
```


grep -l phoenix *



## Check the ssh_pass
```bash
sudo nano /etc/ansible/ansible.cfg
```

# Managing Linux Servers using Ansible
Refer the following steps to manage Linux like servers using Ansible controller node

Step:1) Exchange the SSH keys between Ansible Server and its hosts

Generate the ssh keys from ansible server and shared the keys among the ansible hosts

```bash
$ sudo -i
# ssh-keygen

# ssh-copy-id omartini@admin-node
# ssh-copy-id omartini@master-node

# ssh-copy-id omartini@192.168.1.15
# ssh-copy-id omartini@192.168.1.17
```

Step:2) Create Ansible Hosts inventory file

```bash
$ sudo nano $HOME/hosts
[Web]
192.168.1.15

[DB]
192.168.1.17
```

## Create the file Hosts inventory

```bash
cd /home/omartini/projects/AWS-MKS-EKS-Lambda-Python/Ansible

# Create the File
$ sudo nano hosts
[Admin]
admin-node

[Master]
master-node ansible_ssh_user=omartini ansible_ssh_pass=martini

# Create the Servers
[servers]
server1 ansible_host=203.0.113.111
server2 ansible_host=203.0.113.112
server3 ansible_host=203.0.113.113

[all:vars]
ansible_python_interpreter=/usr/bin/python3


```



```bash
ansible-inventory -i hosts --list -y
```

Step:3) Test and Use default ansible modules

Where:

-i ~/hosts: contains list of ansible hosts
-m: after -m specify the ansible module like ping  & shell
<host>: Ansible hosts where we want to run the ansible modules
Verify ping connectivity using ansible ping module

```bash
# ansible -i <host_file> -m <module> <host>
$ sudo ansible -i ~/hosts -m ping all

$ sudo ansible -i hosts -m ping Admin --ask-pass

$ sudo ansible -i ~/hosts -m ping Master

$ sudo ansible -i ~/hosts -m ping Web
$ sudo ansible -i ~/hosts -m ping DB

```

### Nginx All Servers

* Important
```bash
 sudo ufw allow 179/tcp
 sudo ufw allow 4789/udp
 sudo ufw allow 51820/udp
 sudo ufw allow 51821/udp
 sudo ufw reload
```

```bash
$ sudo nano nginx.yaml
---
- hosts: Web
  tasks:
    - name: Install latest version of nginx on CentOS 7 Server
      yum: name=nginx state=latest
    - name: start nginx
      service:
          name: nginx
          state: started

sudo ansible-playbook -i hosts  nginx.yaml


# SUDO PASSWORD
sudo ansible-playbook nginx.yaml -i hosts --ask-become-pass
```


## Testing Nginx
```bash

# Admin-node
curl http://127.0.0.1/

# Master-node
curl http://127.0.0.1/
```

# Throubleshooting
* "msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"
```bash
  sudo apt install sshpass
```

* "msg": "Using a SSH password instead of a key is not possible because Host Key checking is enabled and sshpass does not support this.  Please add this host's fingerprint to your known_hosts file to manage this host."

[Using a SSH password instead of a key is not possibl](https://ripon-banik.medium.com/ansible-how-do-i-connect-with-remote-to-run-my-script-for-automation-3a8b3cea18ca)
```bash
python3 -m pip install --user paramiko
```

##  Can I ignore it? Yes I can, let’s puts ansible.cfg file in my $HOME folder.
* host_key_checking = False 

```bash
[defaults]
host_key_checking = False
ansible_winrm_server_cert_validation = ignore
```