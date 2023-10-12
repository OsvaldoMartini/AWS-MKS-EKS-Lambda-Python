# Install activate KVM and Virtual machines

### Remove SNAP from Ubuntu
### Uninstall SNAP from Ubuntu
```bash
  sudo snap remove chromium snap-store # Remove Packages is Optional
  
  sudo systemctl stop snapd

  sudo apt remove --purge --assume-yes snapd gnome-software-plugin-snap

  sudo rm -rf ~/snap/
  
  sudo rm -rf /var/cache/snapd/ 
  
  su - $USER
```

## Check Virtualization Support on Ubuntu 20.04
```bash
1. Before you begin with installing KVM, check if your CPU supports hardware virtualization via
egrep -c '(vmx|svm)' /proc/cpuinfo
# Expects Any Number
32
# If the command returns a value of 0, your processor is not capable of running KVM

2. Now, check if your system can use KVM acceleration by typing:
sudo kvm-ok
# Expects
INFO: /dev/kvm exists
KVM acceleration can be used

3. To install cpu-checker, run the following command:
# If kvm-ok returns an error stating KVM acceleration cannot be used, try solving the problem by installing cpu-checker
sudo apt install cpu-checker

4. When the installation completes, restart the terminal.
```
## Install KVM on Ubuntu 20.04
## Step 1: Install KVM Packages

```bash
1. First, update the repositories:
sudo apt update

2. Then, install essential KVM packages with the following command:
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
```
## Step 2: Authorize Users
```bash
1. Only members of the libvirt and kvm user groups can run virtual machines. Add a user to the libvirt group by typing:
sudo adduser $USER libvirt # Add user to the libvirt group
sudo adduser $USER kvm # Add user to the kvm group
 # sudo aduser 'omartini' libvirt
  # Checking Groups and user
  id omartini # shows groups for the user
  groups # All  groups the User belongs to 
  less /etc/group # list all groups

2. Now do the same for the kvm group:
sudo adduser $USER kvm
```
## Step 3: Verify the Installation
```bash
1. Confirm the installation was successful by using the virsh command:
virsh list --all

2. Or use the systemctl command to check the status of libvirtd:
sudo systemctl status libvirtd

3. Press Q to quit the status screen.

4. If the virtualization daemon is not active, activate it with the following command:
sudo systemctl enable --now libvirtd
```
## Creating a Virtual Machine on Ubuntu 20.04
```bash
1. Before you choose one of the two methods listed below, install virt-manager, a tool for creating and managing VMs:
sudo apt install virt-manager
```

## Install x11-common Using apt
[How to enable X11 forwarding from Red Hat Enterprise Linux (RHEL), Amazon Linux, SUSE Linux, Ubuntu server to support GUI-based installations from Amazon EC2](https://aws.amazon.com/blogs/compute/how-to-enable-x11-forwarding-from-red-hat-enterprise-linux-rhel-amazon-linux-suse-linux-ubuntu-server-to-support-gui-based-installations-from-amazon-ec2/)
```bash
sudo apt update

# Step 1: To install X11 related packages and tools:
sudo apt install x11-apps

# Step 2: configure X11 forwarding
sudo vi /etc/ssh/sshd_config
X11Forwarding yes

#  Step 3: To Verify X11Forwarding parameter:
sudo cat /etc/ssh/sshd_config |grep -i X11Forwarding

#  Step 4: To restart ssh service if you changed the value in /etc/ssh/sshd_config:
sudo service ssh restart

```

## Method 1: Virt Manager GUI
[Virt Manager GUI](https://phoenixnap.com/kb/ubuntu-install-kvm)
```bash
sudo virt-manager
```