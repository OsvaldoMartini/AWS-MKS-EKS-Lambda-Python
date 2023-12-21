# CMDS
[HTOP](https://www.cyberciti.biz/faq/how-to-install-htop-on-rhel-8-using-yum/)

```bash
$ apt install htop  # Resource & Memory Checker

or

sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

htop -C

htop --no-color

htop -t

htop --tree

# Let us see only processes of a given user named vivek:
htop -u vivek

htop --user=vivek

htop --user=nginx

# Limit and show process for only the given PIDs:
htop -p PID

htop -p PID1,PID2

htop -p 1342

htop -p 7435,1367

# Help
htop --help
man htop


# wc is the world count program
$ apt list --installed 

$ apt list --installed | wc -l 
107 Packages Installed

$ uname -r

# Location of the pipe wire binary and manin page etc..
$ whereis pipewire  
```

## Create a Service
[Create a Service](https://linuxhandbook.com/create-systemd-services/)

List Services
```bash
  service --status-all
```

```bash
cd /etc/systemd/system/

nano vbox-dns2.service
```

```bash
[Unit]
Description=DNS2 VirtualBox  
After=multi-user.target

[Service]
ExecStart=/usr/bin/VBoxManage startvm DNS2
Type=simple

[Install]
WantedBy=multi-user.target
```
Enabling the service
```bash
sudo systemctl daemon-reload
```

Now, we can enable our systemd service. The syntax to do so is as following:
```bash
sudo systemctl enable vbox-dns2.service
```

Verify Status
```bash
sudo systemctl is-enabled vbox-dns2.service
```

```bash
sudo systemctl status vbox-dns2.service
```


# Install WiFi Debian 12
(WiFi Debian 12)[https://wiki.debian.org/WiFi]


1. Update: ```sudo apt-get update && apt-get upgrade && apt-get dist-upgrade ``` and reboot if you updated the kernel

2. Connect the device. ```lsusb``` should show 2357:0107

3. Install required packages: ```sudo apt-get install git linux-headers-generic build-essential dkms```

4. Get the latest driver from ?GitHub and install it:

```bash
git clone https://github.com/Mange/rtl8192eu-linux-driver
cd rtl8192eu-linux-driver
sudo dkms add .
sudo dkms install rtl8192eu/1.0
```
5. Blocklist rtl8xxxu: echo "blacklist rtl8xxxu" | sudo tee /etc/modprobe.d/rtl8xxxu.conf

6. Reboot and check that the kernel module is loaded by running: ```lsmod```

7. Use your network-interface to connect to the WLAN. You could use the pre-installed NetworkManager for that.

8. Edit NetworkManager.conf as root: ```sudo kate /etc/NetworkManager/NetworkManager.conf```

Append the following:
```bash
[device]
wifi.scan-rand-mac-address=no
```
Save and run: ```/etc/init.d/network-manager restart```

## Nmap
Next, we use a command that offers more options. Said command is nmap. You won’t find nmap installed on your Linux machine by default, so we must add it to the system. Open a terminal window (or log into your GUI-less server) and issue the command:
```bash
sudo apt-get install nmap -y
```

(How to scan for IP addresses on your network with Linux)[https://www.techrepublic.com/article/how-to-scan-for-ip-addresses-on-your-network-with-linux/]

* Once the installation completes, you are ready to scan your LAN with nmap. To find out what addresses are in use, issue the command:

```bash
nmap -sP 192.168.1.0/24
```
* Let’s make nmap more useful. Because it offers a bit more flexibility, we can also discover what operating system is associated with an IP address. To do this, we’ll use the options -sT (TCP connect scan) and -O (operating system discovery). The command for this is:

```bash
sudo nmap -sT -O 192.168.1.0/24
```

## WiFi Scanning
(WiFi Scan ways)[https://linuxhint.com/3-ways-to-connect-to-wifi-from-the-command-line-on-debian/]
```bash
  sudo iwconfig
```
<span style="color: yellow;">NOTE:</span> Replace wlp3s0 for your wireless card displayed when the command iwconfig was executed.

- Scan Networks
```bash
sudo iwlist wlp4s0 scan
```

As you can see the output shows several networks including the LinuxHint Access Point, yet the format isn’t user friendly. If you only want to print the ESSID or names of available networks omitting the rest, run:
```bash
sudo iwlist wlp3s0 scan | grep ESSID
```
## Connecting to wifi from the command line using nmcli:
```bash
sudo nmcli d wifi connect FibreBox_X6-154EC7 password 'Martini!383940'
```
## Connecting to wifi from the console using nmtui:
Nmtui is an interactive curses-based alternative to nmcli and Network Manager, on the console run:
```bash
nmtui
```
