# Webmin with Ubuntu

## build a home lab server with Virtualbox, Webmin and Portainer

[home lab server with Virtualbox, Webmin and Portainer](https://www.youtube.com/watch?v=cTufqsBbXOU)

## Install
```bash
  # webmin
  curl -o setup-repos.sh https://raw.githubusercontent.com/webmin/webmin/master/setup-repos.sh

  sudo sh setup-repos.sh

  sudo apt-get install --install-recommends webmin 
```

# Virtual Box Configuration

## Instal VirtualBox 7 on Ubuntu
```bash
1. Import VirtualBox’s Repo GPG Key
wget -O- https://www.virtualbox.org/download/oracle_vbox_2016.asc | sudo gpg --dearmor --yes --output /usr/share/keyrings/oracle-virtualbox-2016.gpg

2. Add VirtualBox Repo to Ubuntu 22.04
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/oracle-virtualbox-2016.gpg] http://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list

3. Run System Update
  sudo apt update

4. Install VirtualBox 7 on Ubuntu 22.04
sudo apt install virtualbox-7.0

```

## Webmin -> System -> Users and Groups
  > Create NEW user called virtual
  * primary Group: vboxusers (VERY IMPORTANT)
  * secodary groups: shadow (VERY IMPORTANT)

## Webmin -> System -> Bootup and Shutdown
> Select vboxweb.service
Create a New if Doesn't Exist
```bash
 # nano /lib/systemd/system/vboxweb.service 

[Unit]
Description=Virtual Box Web Service
After=network.target


[Service]
Type=forking
User=virtual
Group=vboxusers
ExecStart=/usr/bin/vboxwebsrv --pidfile /home/virtual/vboxweb.pid --host=0.0.0.0 --background
PIDFile=/home/virtual/vboxweb.pid


[Install]
WantedBy=multi-user.target

# Restart the Service

```

## From Virtual Box Installation
```bash
[Unit]
SourcePath=/usr/lib/virtualbox/vboxweb-service.sh
Description=
Before=runlevel2.target runlevel3.target runlevel4.target runlevel5.target shutdown.target 
After=network-online.target vboxdrv.service 
Conflicts=shutdown.target 

[Service]
Type=forking
Restart=no
TimeoutSec=5min
IgnoreSIGPIPE=no
KillMode=process
GuessMainPID=no
RemainAfterExit=yes
User=virtual
Group=vboxusers
# ExecStart=/usr/lib/virtualbox/vboxweb-service.sh start
ExecStart=/usr/lib/virtualbox/vboxweb-service.sh start --pidfile /home/virtual/vboxweb.pid --host=0.0.0.0 --background
PIDFile=/home/virtual/vboxweb.pid
ExecStop=/usr/lib/virtualbox/vboxweb-service.sh stop

[Install]
WantedBy=multi-user.target
```


## RemoteBox

[RemoteBox ubuntu](https://remotebox.knobgoblin.org.uk/?page=installubuntu)
```bash
  sudo apt-get install libgtk3-perl libsoap-lite-perl freerdp2-x11 tigervnc-viewer

  # Unpack
  tar -xjf RemoteBox-3.2.tar.bz2 

  # Go to the Dir
  cd RemoteBox-3.2

  # Execute RemoteBox
  ./remotebox
```

## Docker Portainer
[Portainer.io](http://shifthunter:9000/#!/2/docker/containers)
> User: admin
> pwd: Patterns Always Used

```bash
# The one-liner for the portainer installation:

# ORIGINAL FROM  THE VIDEO:
docker run -d -p 8000:8000 -p 9000:9000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce

# FROM THE YOUTUBE LINK DESCRIPTIONS:
sudo docker run -d -p 9000:9000 -p 8000:8000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock  portainer/portainer


The webmin download page is here : https://www.webmin.com/download.html




To install webmin:


wget https://prdownloads.sourceforge .net/webadmin/webmin_1.962_all.deb
# please remove the space before the dot net
sudo dpkg -i webmin_1.962_all.deb 
sudo apt -f install



The content for the vboxweb.service unit file needs to be as follows:


=================================================================


[Unit]
Description=Virtual Box Web Service
After=network.target


[Service]
Type=forking
User=virtual
Group=vboxusers
ExecStart=/usr/bin/vboxwebsrv --pidfile /home/virtual/vboxweb.pid --host=0.0.0.0 --background
PIDFile=/home/virtual/vboxweb.pid


[Install]
WantedBy=multi-user.target


=================================================================

I have also documented this here: https://serverfault.com/questions/105...

```