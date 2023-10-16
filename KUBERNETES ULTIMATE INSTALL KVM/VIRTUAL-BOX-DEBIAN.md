# How to Install VirtualBox on Debian 12 Step-by-Step

```bash

$ sudo apt install curl wget gnupg2 lsb-release -y

$ curl -fsSL https://www.virtualbox.org/download/oracle_vbox_2016.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/vbox.gpg

$ curl -fsSL https://www.virtualbox.org/download/oracle_vbox.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/oracle_vbox.gpg


$ echo "deb [arch=amd64] http://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list


$ sudo apt update

$ sudo apt install linux-headers-$(uname -r) dkms -y

$ sudo apt install virtualbox-7.0 -y

```

## Extension Pack
```bash
wget https://download.virtualbox.org/virtualbox/7.0.10/Oracle_VM_VirtualBox_Extension_Pack-7.0.10.vbox-extpack
```
# Fixing VirtualBox Kernerl Errors
[Fixing Kernel](https://www.addictivetips.com/ubuntu-linux-tips/fix-virtualbox-vm-launch-error-on-linux/)


# 3) Add Your User to the vboxusers Group
* To use VirtualBox without superuser privileges, you need to add your user to the vboxusers group. Run below usermod command.

```bash
 $ sudo usermod -aG vboxusers $USER
 
 $ newgrp vboxusers
```

# 4) Start VirtualBox CMD Line
```bash
  # Start VirtualBox
  virtualbox startvm DNS2

  # Stop
  VBoxManage controlvm "vm_name" poweroff

  # Stop
  nohup VBoxHeadless -startvm "vm_name" &

  # To list virtual machines:
  VBoxManage list vms
 
  # To Start a virtual machine:
  VBoxManage startvm YOUR_VIRTUAL_MACHINE_NAME

  VBoxManage startvm DNS2

  #To stop a virtual machine:
  VBoxManage controlvm Android poweroff

```



