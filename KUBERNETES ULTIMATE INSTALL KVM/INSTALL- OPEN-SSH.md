# How to Install and Enable SSH on Debian 12/11/10

[Install OpenSSH](https://www.linuxcapable.com/how-to-install-and-enable-ssh-on-debian-linux/)

[Config Server Details](https://linuxhint.com/debian-12-enable-ssh-server/)

[Firewall UFW](https://www.zenarmor.com/docs/network-security-tutorials/how-to-set-up-a-firewall-with-ufw-on-debian)

## Step 1: Install SSH

```bash 
  sudo apt update && sudo apt upgrade

  sudo apt install openssh-server

  systemctl status ssh

```
# OpenSSH Configuration

## Step 2: Configure SSH
After installing the SSH server on your Debian system, you must configure it to meet your needs. The configuration file for SSH is located at <span style="color: yellow;">/etc/ssh/sshd_config</span>.

There are a couple of SSH configuration files:

* Configuration file for the SSH client
<span style="color: yellow;">/etc/ssh/ssh_config</span> 

* Configuration file for the SSH server
<span style="color: yellow;">/etc/ssh/sshd_config</span> 

```bash
 sudo nano /etc/ssh/sshd_config
```

# Secutiry Changes
* Here are some important configuration options that you may want to consider:

* Change the default SSH port: SSH uses port 22 for communication. However, this port is often targeted by attackers. You may want to change the default port to a different number to increase security. To do this, locate the following line in the configuration file:
```bash
  #Port 22
```
* Uncomment the line and replace 22 with your desired port number.

* Disable root login: By default, the root user can log in via SSH. However, it is generally recommended to disable this to increase security. To do this, locate the following line in the configuration file:

* Change “yes” to “no” to disable root login.
```bash
#PermitRootLogin yes
```

* Allow or deny specific users: You can also allow or deny specific users from accessing your system via SSH. To do this, add the following lines to the configuration file:
```bash
AllowUsers user1 user2
DenyUsers user3 user4
```

* Replace “user1”, “user2”, “user3”, and “user4” with the actual usernames. After making changes to the configuration file, save and close it by pressing Ctrl+X, Y, and Enter.

* Finally, to apply the changes, restart the SSH service using the following command
```bash
sudo systemctl restart ssh
```

## Step 3: Connect with SSH
```bash
 ip add show

 ssh username@ipaddress
```

# Firewall UFW
* Check out the list of UFW rules for verification:
```bash
  sudo apt update && sudo apt upgrade -y
  
  sudo apt install ufw -y


  sudo ufw allow proto tcp from any to any port 22

  ufw allow ssh
  ufw status

  sudo ufw status numbered
```

# Uninstall UFW
```bash
sudo apt autoremove ufw --purge -y
```

## Profile: WWW Full
```bash
  sudo ufw app info 'WWW Full'

  sudo ufw app info all
  
  sudo ufw allow 53 comment 'DNS server'
```
## Allowing Port Ranges
```bash
  sudo ufw allow 55100:55200/tcp

 # multiple Ports
  sudo ufw allow 22,80,443/tcp
```
## Allow Connections From an Only Trusted IP Address
* You may need to allow the administrator to access the server without any restrictions. To allow access to all ports from an IP address, such as 10.10.10.100, specify from followed by the IP address you need to whitelist:
```bash
sudo ufw allow from 10.10.10.100
```
 ## Allow Connections From a Trusted IP Address on Specific port
 * You may need to restrict connections from a specific IP address to a single port. For example, on your server, the MySQL service(3306) can only be accessed by the Application Server with the IP address 10.10.10.10. To accomplish this, run the following command:
 ```bash
  sudo ufw allow from 10.10.10.10 to any port 3306
```