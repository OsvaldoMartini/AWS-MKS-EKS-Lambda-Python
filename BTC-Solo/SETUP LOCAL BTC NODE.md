
# One important thing I left out of the video is you need to go onto your Internet router and port forward tcp/8333 to your node to allow inbound Bitcoin node connections.

** Since I recorded the video I've made some tweaks to the log rotation so the below doesn't exactly match the video. **

The basic steps are:
[BITCOIN ON DEBIAN](https://snapcraft.io/install/bitcoin-core/debian)
[SETUP BITCOIN DAEMON](https://www.youtube.com/watch?v=vst25Q9i9mc)

# Size of usage DISK
```bash
sudo  du -sh /home/btc
```


= Prep OS and install bitcoin core software
```bash
sudo su
apt update
apt upgrade
snap install bitcoin-core
```

= Create an account to run Bitcoin core in even more isolation from the rest of the system
```bash
groupadd btc
useradd -g btc -m -s /bin/bash btc
su - btc
```

= Do a test run:
```bash
bitcoin-core.daemon
```
== If no errors then after 30s:
```bash
ctrl-c
tail ~/snap/bitcoin-core/common/.bitcoin/debug.log 
```
= Create the configuration file:
```bash
cd ~/snap/bitcoin-core/common
mkdir .bitcoin  OR cd .bitcoin/

nano .bitcoin/bitcoin.conf
externalip=121.x.x.x           # OLD 121.98.x.x
externalip=2404:xx             # OLD 2404:4408:x:x::x
listenonion=0
disablewallet=1
dbcache=2048
```

= If you created a config file then do another test run:
```bash
bitcoin-core.daemon
```
== If no errors then after 30s:
```bash
ctrl-c
tail ~/snap/bitcoin-core/common/.bitcoin/debug.log 
```

= Now setup to run as a daemon:
== Become root again:
```bash
exit

nano /etc/systemd/system/bitcoind.service

[Unit]
Description=Bitcoin daemon
After=network.target
Wants=network-online.target

[Service]
User=btc
Group=btc
Type=forking
PIDFile=/home/btc/snap/bitcoin-core/common/.bitcoin/bitcoin.pid
ExecStart=/snap/bin/bitcoin-core.daemon -daemon -pid=bitcoin.pid
KillMode=process
Restart=always
TimeoutSec=120
RestartSec=30

[Install]
WantedBy=multi-user.target
```

== Enable and start service
```bash
systemctl daemon-reload
systemctl enable bitcoind.service
systemctl start bitcoind.service
systemctl status bitcoind.service
journalctl -xeu bitcoind.service
```

## READIUNG THE LOG on the bitcoin-daemon service
```bash
ls -lh /home/btc/snap/bitcoin-core//common/.bitcoin/debug.log
```

# Reducing DISK USAGE the logs storage "rotation"

= Setup log rotation of debug log
```bash
nano /etc/logrotate.d/bitcoind

### VERSION WITHOUT ERROR
/home/btc/snap/bitcoin-core/common/.bitcoin/debug.log
{
        su btc btc
        missingok
        notifempty
        compress
        delaycompress
        sharedscripts
        copytruncate
}

### VERSION FROM THE VIDEO WITH ERROR
/home/btc/snap/bitcoin-core/common/.bitcoin/debug.log
{
        su btc btc
        missingok
        notifempty
        compress
        delaycompress
        sharedscripts
        postrotate
                /usr/bin/systemctl stop bitcoind
                /usr/bin/systemctl start bitcoind
        copytruncate
}

```

== Check logrotation service is correctly configured
```bash
sudo systemctl restart logrotate.service
sudo systemctl status logrotate.service
```


= Check Bitcoin Daemon
```bash
su - btc

bitcoin-core.cli -netinfo | head -n 8 
bitcoin-core.cli getnetworkinfo | head -n 20


bitcoin-core.cli -netinfo 
bitcoin-core.cli getnetworkinfo
bitcoin-core.cli getblockchaininfo
bitcoin-core.cli getpeerinfo

tail ~/snap/bitcoin-core/common/.bitcoin/debug.log 
```

= This shows disk space used - should grow to begin with, currently 450GB "all up" for me
```bash
du -h ~/snap/bitcoin-core/common/.bitcoin/
```