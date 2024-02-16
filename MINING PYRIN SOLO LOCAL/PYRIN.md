# Videos 

[Node Pyrin Wallet](https://www.youtube.com/watch?v=s3tEQAtu-so&list=PLxV5dldYJZlvncBmeG5sK4MTVTTmkAXD5)




[Bridge Pyrin Solo](https://www.youtube.com/watch?v=DNuBU2ee-co)
[Brige Files](https://github.com/Lolliedieb/lolMiner-releases/wiki/Bridge-for-Pyrin-to-mine-to-the-Node)

[Bridge Guide](https://sonofatech.locals.com/post/4998704/solo-mine-pyrin-bridge-guide)


# Create Pyrin Service
## Some bash cmds
```bash
sudo nano /etc/systemd/system/pyipad.service

[Unit]
Description=Pyipad Service
After=network.service

[Service]
User=omartini
WorkingDirectory=/home/omartini
ExecStart=/usr/local/bin/pyipad --utxoindex
# optional items below
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
# Activating the Service
```bash
sudo systemctl daemon-reload
sudo systemctl status pyipad.service
sudo systemctl status pyipad.service   
sudo systemctl enable pyipad.service  # It creates a symbiotic link

sudo systemctl start pyipad.service
sudo systemctl status pyipad.service
sudo journalctl -u pyipad -n 1000 -f
```

# Run Pyrin Wallet DAEMON
```bash
 pyrinwallet start-daemon
```