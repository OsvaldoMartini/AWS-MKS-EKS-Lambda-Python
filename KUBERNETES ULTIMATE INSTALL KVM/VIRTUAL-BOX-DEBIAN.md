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


Procedure <span style="color: yellow;">**Wheel**</span> Group

* 1 ) To enable sudo for the username on RHEL, add the username to the wheel group. Run the command as root user
```bash
  grep 'wheel' /etc/group

  groupadd wheel  
  
  usermod -aG wheel <username>

  usermod -aG wheel $USER
```
* 2 ) As a superuser or administrator, run the visudo to edit the /etc/sudoers file. Make sure that the lines are not commented
```bash
  visudo
```
It opens the /etc/sudoers file in a text editor.
```bash
## Allow root to run any commands anywhere
root        ALL=(ALL)       ALL
root ALL=(ALL) NOPASSWD:EXEC:ALL

## Allows members of the 'sys' group to run networking, software,
## service management apps and more.
# %sys ALL = NETWORKING, SOFTWARE, SERVICES, STORAGE, DELEGATING, PROCESSES, LOCATE, DRIVERS

## Allows people in group wheel to run all commands
%wheel        ALL=(ALL)       ALL

## Allows people in group wheel to run all commands without password
%wheel ALL=(ALL:ALL) NOPASSWD:ALL
```

# 4) Start VirtualBox CMD Line
```bash
  # Start VirtualBox
  virtualbox startvm DNS2

  # Stop
  VBoxManage controlvm "vm_name" poweroff
  
  VBoxManage controlvm "DNS2" poweroff

  # Stop
  nohup VBoxHeadless -startvm "vm_name" &

  # To list virtual machines:
  VBoxManage list vms
 
  # To Start a virtual machine:
  VBoxManage startvm YOUR_VIRTUAL_MACHINE_NAME

  VBoxManage startvm DNS2

  #To stop a virtual machine:
  VBoxManage controlvm DNS2 poweroff
```

 # AutoStart VMS Step by step
 * How To Set Your VirtualBox VM to Automatically Startup
First you need to create the file <span style="color: yellow;">/etc/default/virtualbox</span> and add a few variables.
```bash
sudo nano /etc/default/virtualbox
```

* <span style="color: yellow;">VBOXAUTOSTART_DB</span> which contains an absolute path to the autostart database directory and <span style="color: yellow;">VBOXAUTOSTART_CONFIG</span> which contains the location of the autostart config settings. The file should look similar to this:
```bash
# virtualbox defaults file
VBOXAUTOSTART_DB=/etc/vbox
VBOXAUTOSTART_CONFIG=/etc/vbox/autostart.cfg  # or  vbox.cfg
```
<span style="color: yellow;">Update:</span> It has been commented that the file named <span style="color: yellow;">vbox.cfg</span> didn’t work for some. 
They have been successful using <span style="color: yellow;">autostart.cfg</span>, if <span style="color: yellow;">vbox.cfg</span> doesn’t work for you, then trying naming the file <span style="color: yellow;">autostart.cfg</span>.

Now we need to create <span style="color: yellow;">/etc/vbox/vbox.cfg</span> file
```bash
sudo nano /etc/vbox/autostart.cfg # or vbox.cfg 
```
* Add the values
```bash
# Default policy is to deny starting a VM, the other option is "allow".
default_policy = deny
# Create an entry for each user allowed to run autostart
omartini = {
 allow = true
}
```
* if you are the only user you can just add the line default_policy = allow to the vbox.cfg file.

* Set permissions on directory to the vboxuser group and make sure users can write to the directory as well as sticky bit.
```bash
 chgrp vboxusers /etc/vbox

 chmod 1775 /etc/vbox
```
* Add each of the users to the vboxusers group. Make sure to check their group memberships so they do not loose any groups they currently have assigned to their id.

```bash
groups myuserid

myuserid wheel

usermod -G wheel, vboxusers myuserid
```
* Every user who wants to enable autostart for individual machines has to set the path to the autostart database directory with
```bash
 VBoxManage setproperty autostartdbpath /etc/vbox
```
Now we are ready to set the VM’s we choose to start.

* <span style="color: yellow;">Note:</span> The autostart options are stored in the <span style="color: yellow;">/etc/vbox</span> file, and the VM itself. If moving the vm, the options may need to be set again.
```bash
$ VBoxManage modifyvm <uuid|vmname> --autostart-enabled <on|off>

$ VBoxManage modifyvm DNS2 --autostart-enabled on

$ VBoxManage modifyvm DNS2 --autostart-enabled off
```
You can also:
```bash
$ VBoxManage modifyvm <uuid|vmname> --autostop-type <disabled|savestate|poweroff|acpishutdown>
```
* This will create a <span style="color: yellow;">myuserid.start</span>  file in <span style="color: yellow;">/etc/vbox</span> directory


# Service AutoStart VistualBox

[vboxautostart-service](https://askubuntu.com/questions/404665/how-to-start-virtual-box-machines-automatically-when-booting)

* 6b) Need to get a vboxautostart-service script and make it executable.
```bash
 cd /etc/init.d/

sudo wget http://www.virtualbox.org/browser/vbox/trunk/src/VBox/Installer/linux/vboxautostart-service.sh?format=raw -O vboxautostart-service

sudo chmod +x vboxautostart-service
```

# ###  Maybe  ###
* 6c) Alert the rc.d controller, but I used 24 as the start time. Putting just 20 and it did not start up. Perhaps it ran even before virtualbox was working.
```bash
sudo update-rc.d vboxautostart-service defaults 24 24
```

* Contents of [vboxautostart-service](./vboxautostart-service.sh)

* Now restart the vboxautostart-service to read in the changes
```bash
 sudo systemctl daemon-reload

 service vboxautostart-service restart
```


* Reboot your system and your VM should start.
