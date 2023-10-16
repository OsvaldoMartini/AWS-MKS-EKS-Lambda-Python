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


