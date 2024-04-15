# BTC SOLO MINING CKPOOL

[BTC Solo CKPool](https://www.youtube.com/watch?v=dAa6PkVN-3o)

= Prep OS and install mandatory components
```bash
sudo su
apt update
apt upgrade
apt install build-essential yasm autoconf automake libtool libzmq3-dev pkgconf
bash

= Create an account to run ckpool in isolation from the rest of the system
```bash
# Debian first creta the group 
groupadd btc

useradd -g btc -m -s /bin/bash ckpool
```



= Build ckpool
```bash
su - ckpool
git clone https://bitbucket.org/ckolivas/ckpool...
cd solobtc
./autogen.sh  // Generate All dependencies and Build files
./configure   // Make file and do some other pieces of configuration
make          // Build actually the code
```

= Enable RPC in bitcoin core snap
```bash
exit
su - btc
cd
```

== Add these lines
```bash
nano ./snap/bitcoin-core/common/.bitcoin/bitcoin.conf
externalip=121.x.x.x           # OLD 121.98.x.x
externalip=2404:xx             # OLD 2404:4408:x:x::x
listenonion=0
disablewallet=1
dbcache=2048

server=1
rpcuser=rpc_admin
rpcpassword=random_password
zmqpubhashblock=tcp://127.0.0.1:28332
```

= Restart Bitcoin Core
```bash
exit
systemctl restart bitcoind
systemctl status bitcoind
```

= Configure ckpool 
```bash
su -- ckpool
cd ~/solobtc
mv ckpool.conf ckpool.original
nano ckpool.conf
{
"btcd" :  [
        {
        "url" : "127.0.0.1:8332",
        "auth" : "rpc_admin",
        "pass" : "random_password",
        "notify" : true
        }
],
"btcsig" : "/minde per martini-crypto-mind/",
"donation" : 0.5
}
```


Test
```bash
cd ..
src/ckpool -B   #  LETTER B
```

= Now setup to run as a daemon:
```bash
exit
```

== Create systemd unit as ROOT
```bash
nano /etc/systemd/system/ckpool.service
[Unit]
Description=ckpool solo Bitcoin pool
After=multi-user.target
Requires=bitcoind.service

[Service]
User=ckpool
Group=btc
Type=simple
Restart=always
WorkingDirectory=/home/ckpool/ckpool-solo
ExecStart=/home/ckpool/ckpool-solo/src/ckpool -B

[Install]
WantedBy=multi-user.target
```


== Enable and start service
```bash
systemctl daemon-reload
systemctl enable ckpool.service
systemctl start ckpool.service
systemctl status ckpool.service
journalctl -xeu ckpool.service
```



= Setup log rotation of debug log
```bash
nano /etc/logrotate.d/ckpool
/home/ckpool/solobtc/logs/ckpool.log
{
        su ckpool btc
        missingok
        notifempty
        compress
        delaycompress
        sharedscripts
        copytruncate
}
```

== Check logrotation service is correctly configured
```bash
sudo systemctl restart logrotate.service
sudo systemctl status logrotate.service
```


S19 Pro                                      Wallet           Password
Pool1:  192.168.1.50:3333                    adklejrkjandf      xxx1234
Pool2:  stratum+tcp://solo.ckpool.org:3333   jksdfjijwekjk      xxx1234


