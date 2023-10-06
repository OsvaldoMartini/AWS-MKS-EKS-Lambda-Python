# Amazon Linux 2 Local

[AWS Local](https://www.youtube.com/watch?v=oYo1LHbEKyI)

## User and Passowrd
```bash
  USER:   ec2-user
  PWD: amazon
```


## Updates and installs and Start httpd
```bash
  sudo yum update

 # Instal httpd server
  sudo install httpd mc -y

  sudo service httpd start

  sudo systemctl start httpd

  sudo system enable httpd

  sudo service httpd stop

  # mc  app to help to edit files easilly
  sudo mc

  shift + F4  to create new file
  /var/www/index.html  > "Hellow Amazon Linux2"

  ifconfig
  ipaddress = 192.168.1.63 (VM Machine Address)
```

# Change IP Address Amazon Linux 2
```bash
  sudo mc /etc/sysconfig/network-scripts/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-eth0:0


  DEVICE=eth0
  BOOTPROTO=static
  ONBOOT=yes
  IPADDR=10.8.0.2
  NETMASK=255.255.255.0
  GATEWAY=10.8.0.1

```

## Permission SSH
```bash
    ssh ec2-user@192.168.1.63
    
    The authenticity of host '192.168.1.63 (192.168.1.63)' can't be established.
    ED25519 key fingerprint is SHA256:gMjeerl5HAnKfluVs1v3JOQyWhPgNQsPP4/npezm9aY.
    This key is not known by any other names
    Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
    
    Warning: Permanently added '192.168.1.63' (ED25519) to the list of known hosts.
    ec2-user@192.168.1.63: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).

```

## Enables Permission
```bash
  sudo mc

# File "sshd_config"
/etc/ssh/sshd_config

PasswordAuthentication yes
ChallengerResponseAuthentication yes

sudo systemctl restart sshd.service

& Login it again:

C:\Users\osval>ssh ec2-user@192.168.1.63
(ec2-user@192.168.1.63) Password:
Last login: Sat Sep 30 11:31:15 2023
   ,     #_
   ~\_  ####_        Amazon Linux 2
  ~~  \_#####\
  ~~     \###|       AL2 End of Life is 2025-06-30.
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /    A newer version of Amazon Linux is available!
      ~~._.   _/
         _/ _/       Amazon Linux 2023, GA and supported until 2028-03-15.
       _/m/'           https://aws.amazon.com/linux/amazon-linux-2023/

```
## List Ports in Use
```bash
  # Run any one of the following command on Linux to see open ports:
  sudo lsof -i -P -n | grep LISTEN
  sudo netstat -tulpn | grep LISTEN
  sudo ss -tulpn | grep LISTEN
  sudo lsof -i:22 ## see a specific port such as 22 ##
  sudo nmap -sTU -O IP-address-Here
```
## Create the Httpd/ Apache2 config file
```bash
 # HTTP Installation Oracle Linux
 [Httpd](http://192.168.1.63/)

  <virtualHost *:80>
        ServerName shifthunter.com
        DocumentRoot /var/www/html/
  </virtualHost>

 # Apache2 Installation Ubuntu
 [Apache 2](http://192.168.1.47:18080/)

<VirtualHost shifthunter.com:15444>
        ServerName shifthunter.com
        ServerAdmin omartini@shifthunter.com
        ServerAlias www.shifthunter.com
        DocumentRoot /var/www/shifthunter/public_html
        DirectoryIndex index.html
        ErrorLog ${APACHE_LOG_DIR}/shifthunter_error.log
        CustomLog ${APACHE_LOG_DIR}/shifthunter_access.log combined
  </VirtualHost>
```

# Ubuntu Static Ip Addres
```bash
  apt intall net-tools

  ifconfig -a

  cd /etc/netplan
```


## Linux Version
```bash
  cat /etc/os-release
  lsb_release -a
  hostnamectl
```

