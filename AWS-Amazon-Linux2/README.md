# Amazon Linux 2 Local

[AWS Local](https://www.youtube.com/watch?v=oYo1LHbEKyI)

## User and Passowrd
```bash
  USER:   ec2-user
  PWD: amazon
```

## Network Setting
```bash
sudo nano /etc/sysconfig/network-scripts/ifcfg-eth0
```
Updating DNS1, DNS2, GATEWAY
```bash
$ sudo cat <<EOF | sudo tee /etc/sysconfig/network-scripts/ifcfg-eth0
GATEWAY=192.168.1.1
EOF
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


## Linux Version Version Installed Linux
```bash
  cat /etc/os-release
  lsb_release -a
  hostnamectl


NIPOGI Mini PC
Operating System: Debian GNU/Linux 12 (bookworm)  
Kernel: Linux 6.5.0-0.deb12.1-amd64
```

# Instal CMake Debian
Step 1: Download CMake
[CMake Debian 11](https://linuxhint.com/install-cmake-on-debian/)
```bash
wget https://github.com/Kitware/CMake/releases/download/v3.28.0/cmake-3.28.0.tar.gz

tar -zxvf cmake-3.28.0.tar.gz
```
Step 2: Extract CMake and Run the Bootstrap
```bash
cd cmake-3.28.0 
##Run de bootstrap
sudo ./bootstrap
```
Step 3.1: Install CMake
```bash
sudo make
```
Step 3.2: Install CMake
```bash
# And After
sudo make install
```


## Find file  or Locate GCC
```bash
whereis gcc

which gcc

gcc --version
```


## Search Packages
```bash

  sudo apt list --installed | grep openssl

  dpkg -l | grep ssl

# MANDATORY FO CMAKE AND G++ / GCC
sudo apt-get update -y

sudo apt-get install -y libcurl4-openssl-dev

sudo apt-get install -y libssl-dev

```

# curl-config is our friend
Applications (or actually whoever) that want to find out about the libcurl installation on a particular host, will find a friend in the curl-config tool. (Added in the curl 7.7.2 release.)

- What compiler flags do I need to compile libcurl using source code?
```bash
 curl-config --cflags
```
- What linker options do I need when I link with libcurl?
```bash
 curl-config --libs
```
- How do I know if libcurl was built with SSL support?
```bash
 curl-config --feature | grep SSL
```
- What's the installed libcurl version?
```bash
 curl-config --version
```


## Throubleshooting INSTALL CURL  libcurl4-openssl-dev
```bash
Step 1
sudo apt-get update -y
Step 2
sudo apt-get install -y libcurl4-openssl-dev
Step 3
sudo apt-get install -y libssl-dev


## DANGEROUS BECAUSE DELETES THE NETWORK
# sudo apt-get remove libcurl3-gnutls 
# sudo apt-get remove --auto-remove libcurl3-gnutls 
# sudo apt-get purge libcurl3-gnutls 
# sudo apt-get purge --auto-remove libcurl3-gnutls 
# sudo apt-get remove curl 
# sudo apt-get remove --auto-remove curl 
# sudo apt-get purge curl 
# sudo apt-get purge --auto-remove curl 

```

## Throubleshooting libcurl.so.4
## Find file  or locate libcurl.so.4 
```bash
apt --installed list | grep 'curl'

lsb_release -a

ls -hal

stat libcurl.so.4

# Instal apt-get install apt-file
sudo apt install apt-file
sudo apt-file update

apt-file search libcurl.so.4

ldd libcurl.so.4

sudo ln -fs /usr/lib/libcurl.so.4 /usr/local/lib/

sudo ldconfig -v 
sudo ldconfig -p 


whereis libcurl.so.4
## Or 
locate libcurl.so.4

## Result
libcurl.so.4: /usr/lib/x86_64-linux-gnu/libcurl.so.4

## Find out the Type
ls -l /usr/lib/x86_64-linux-gnu/libcurl.so.4
## Result
lrwxrwxrwx 1 root root 16 Oct  5 22:31 /usr/lib/x86_64-linux-gnu/libcurl.so.4 -> libcurl.so.4.8.0
```

Third, remove it and rebuild the link to libcurl.so.4.3.0:
```bash
sudo rm /usr/lib/x86_64-linux-gnu/libcurl.so.4
sudo ln -s /usr/lib/x86_64-linux-gnu/libcurl.so.4.8.0 /usr/lib/x86_64-linux-gnu/libcurl.so.4
```
Next, check it:
```bash
 ls -l /usr/lib/x86_64-linux-gnu/libcurl.so.4
```
Type CMake version
```bash
cmake -version
```
## Compile C Getting the return from  main()
```bash
$ cc -I. -I./subfolder main.cpp   -o main
$ ./main
$ echo $?
```
## Compile C++ Getting the return from  main()
```bash
$ g++ -I. -I./subfolder main.cpp   -o main
$ ./main
$ echo $?


g++ -g3 -Wall -I. -I./ccan cgminer.c -o cgminer
```


## Compile Build
How do I compile the program on Linux?
Use any one of the following syntax to compile the program called demo.c:
```bash
cc program-source-code.c -o executable-file-name
## OR ##
gcc program-source-code.c -o executable-file-name
## OR, assuming that executable-file-name.c exists ##
make executable-file-name
```

In this example, compile demo.c, enter:
```bash
cc demo.c -o demo
OR
## assuming 'demo.c' exists in the current directory ##
make demo
```

If there is no error in your code or C program then the compiler will successfully create an executable file called demo in the current directory, otherwise you need fix the code. To verify this, type:
```bash
ls -l demo*
```

# Install Linux Distro on Windows
```bash
  wsl --install


  GUI
sudo apt install gnome
```

## NVIDIA or Cideo Vard Versionadn Model and Name
```bash
ubuntu-drivers devices

# Linux Ubuntu 
$ sudo apt install inxi

$ inxi -Gx
  Graphics:  Device-1: NVIDIA GP104 [GeForce GTX 1080] vendor: ASUSTeK driver: nvidia v: 435.21 bus ID: 01:00.0 
            Display: server: X.Org 1.20.5 driver: nvidia resolution: 3440x1440~75Hz 
            OpenGL: renderer: GeForce GTX 1080/PCIe/SSE2 v: 4.6.0 NVIDIA 435.21 direct render: Yes




lspci | grep VGA


wmic path win32_VideoController get name
    Trigger 6 External Graphics
    Trigger 6 External Graphics
    Intel(R) Iris(R) Xe Graphics

wmic path win32_VideoController get DriverVersion
    DriverVersion
    1.5.2201.426
    1.5.2201.426
    30.0.101.1003

```


### GCC Version
## Install GCC and G++ and GDB
Just run
```bash
  sudo apt-get install build-essential gdb
```

```bash
gcc -version

g++ --version

- hread model: posix
- Supported LTO compression algorithms: zlib zstd
- gcc version 12.2.0 (Debian 12.2.0-14) 

# Next install the GNU compiler tools and the GDB debugger with this command:

sudo apt-get install build-essential gdb

- GNU gdb (Debian 13.1-3) 13.1

```

## Add Syubdirectories to be found by GCC
```bash
sudo echo 'export PATH="$PATH:/home/omartini/projects/cgminer/ccan"' >> ~/.bashrc

sudo source ~/.bashrc

```


## Binance WWW Socket
```bash

$ npm install -g wscat


$ wscat -c wss://stream.binance.com:9443

$ wscat -c wss://stream.binance.com:9443/ws/btcusdt@trade

{"e":"trade","E":1702304816463,"s":"BTCUSDT","t":3316196691,"p":"41881.11000000","q":"0.00161000","b":23681621827,"a":23681621462,"T":1702304816462,"m":false,"M":true}

[Unix TimeStamp](https://www.unixtimestamp.com/)
{
    "e": "trade",           //Event
    "E": 1702304816463,     //Time Stamp
    "s": "BTCUSDT",         //Symbol / Instrument 
    "t": 3316196691,        // Trace ID
    "p": "41881.11000000",  // Price
    "q": "0.00161000",      //Quantity
    "b": 23681621827,       // Buyer order ID
    "a": 23681621462,       // Seller order ID
    "T": 1702304816462,     // Trade Time
    "m": false,             // Is the buyer the market maker?
    "M": true               // Ignore
}
KLine/Candlestick Stream
$ wscat -c wss://stream.binance.com:9443/ws/btcusdt@kline_5m
{
    "e": "kline",
    "E": 1702305606684,
    "s": "BTCUSDT",
    "k": {
        "t": 1702305600000,
        "T": 1702305899999,
        "s": "BTCUSDT",
        "i": "5m",
        "f": 3316221692,
        "L": 3316221810,
        "o": "41988.88000000",  //open
        "c": "41977.01000000",  //close
        "h": "41990.00000000",  // high
        "l": "41977.00000000",  // low
        "v": "3.15230000",
        "n": 119,
        "x": false,
        "q": "132356.57522880",
        "V": "1.77565000",
        "Q": "74555.95547580",
        "B": "0"
    }
}

 Saving as file
$ wscat -c wss://stream.binance.com:9443/ws/btcusdt@kline_5m | tee btcusdt-binance.txt




{"e":"kline","E":1702305634480,"s":"BTCUSDT","k":{"t":1702305600000,"T":1702305899999,"s":"BTCUSDT","i":"5m","f":3316221692,"L":3316222441,"o":"41988.88000000","c":"41997.16000000","h":"42020.00000000","l":"41977.00000000","v":"33.94432000","n":750,"x":false,"q":"1425724.82791720","V":"20.99923000","Q":"881899.63820630","B":"0"}}


```


## Throubleshooting
## TimeStamp RecWindow``
```bash
wget -qO- http://ipecho.net/plain


# Windows
net stop w32time
w32tm /unregister

w32tm /register

net start w32time

w32tm /resync
```
## Synchronizing a Linux System Clock with NTP Server
[NTP Server](https://tecadmin.net/synchronizing-a-linux-system-clock-with-ntp-server/#:~:text=The%20Network%20Time%20Protocol%20(NTP,systemd%20system%20and%20service%20manager.)

- Step 1: Install Timesync Service
Timesync is the minimalistic service to synchronize local time with NTP servers. The package contains the systemd-timesyncd system service that may be used to synchronize the local system clock with a remote Network Time Protocol server.
```bash
sudo apt install systemd-timesyncd 

sudo systemctl status systemd-timesyncd 
```
- Step 2: Enable the Clock Synchronization
To synchronize the Linux system clock with an NTP server using timedatectl, you need to run the following command as root or use sudo:
```bash
sudo timedatectl set-ntp true 
```
- Step 3: Verify Changes
You can verify the status of the NTP synchronization by running the following command:
```bash
timedatectl 
```
- Step 4: Synchronize Hardware Clock
It’s important to note that the timedatectl command only affects the system clock, which is the main clock on the system used by the operating system and applications. The hardware clock, also known as the real-time clock (RTC), is a separate clock that runs independently of the system and is used to keep the time even when the system is powered off. To synchronize the hardware clock with the system clock, you need to run the following command:
```bash
sudo timedatectl set-local-rtc 1 
```
