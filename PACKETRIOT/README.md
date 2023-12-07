# Packetriot

# Ubuntu Firewall
```bash
  sudo ufw allow 22

  sudo ufw allow 9001 # Lotto-Audit Sockets

  sudo ufw status verbose
```


## PkTriot Install
[Packetriot Install](https://packetriot.com/downloads)
```bash
  sudo apt-get install apt-transport-https gnupg -y

  wget -qO - https://download.packetriot.com/linux/debian/pubkey.gpg | sudo apt-key add -  

  echo "
  deb [arch=amd64] https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-amd64 / 
  deb [arch=i386]  https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-i386  / 
  deb [arch=armhf] https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-armhf / 
  deb [arch=arm64] https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-arm64 / 
  " | sudo tee /etc/apt/sources.list.d/packetriot.list

  sudo apt-get update 
  
  sudo apt-get install pktriot

```


## Docker Packetriot Folder Tunnels
```bash

  [user@host] cd $HOME
  [user@host] mkdir Tunnels
  [user@host] cd Tunnels

  # let's make a sub-directory for our tunnel
  [user@host:~/Tunnels] mkdir shifthunter-tunnel

  sudo docker pull packetriot/pktriot:latest

  sudo docker run -d --restart always -v $PWD/shifthunter-tunnel:/data --name shifthunter-tunnel packetriot/pktriot:latest

  sudo docker logs -n 100 shifthunter-tunnel

  sudo docker logs --tail 100 <container ID>

  sudo docker logs --follow --until=3s

  sudo docker exec -it shifthunter-tunnel pktriot configure

  sudo docker exec shifthunter-tunnel pktriot edit --name Shift-Hunter-Tunnel

  sudo docker exec shifthunter-tunnel pktriot info

  sudo docker exec -it shifthunter-tunnel pktriot tunnel http add --domain green-smoke-17402.pktriot.net --destination localhost --http 15050 --letsencrypt

sudo docker exec -it shifthunter-tunnel pktriot tunnel http add --domain still-cherry-47731.pktriot.net --destination /var/www/shifthunter --http 15050 --letsencrypt
http://192.168.1.50:15050/

# Web Root
sudo pktriot tunnel http add --domain shifthunter.com --destination /var/www/html/source --http 15050 --webroot $PWD/var/www/html/source --letsencrypt

sudo docker  exec -it shifthunter-tunnel pktriot tunnel tcp allocate

sudo docker  exec -it shifthunter-tunnel pktriot route http add --domain green-smoke-17402.pktriot.net --webroot $PWD/var/www/html/source

# Remove Rule
sudo pktriot tunnel http rm --domain still-cherry-47731.pktriot.net
lotoauditoria.com  
# Docker
sudo docker exec -it shifthunter-tunnel pktriot tunnel http rm --domain green-smoke-17402.pktriot.net


sudo docker exec shifthunter-tunnel pktriot start

# ae2sites
find /etc/apache2/sites-available/ -type f -and -not -name "*default*" -exec a2ensite {} \;

sudo a2ensite *

sudo service apache2 reload

sudo a2ensite "*.conf"

sudo a2ensite /var/www/html/*/

sudo systemctl restart apache2.service
```

## Docker Patriot
(Docker Patriot)[https://packetriot.com/tutorials/posts/using-packetriot-with-docker/]

```bash
  sudo docker exec -it shifthunter-tunnel pktriot configure

  sudo docker restart -it young-waterfall-61248.pktriot.net

  sudo docker exec -it young-waterfall-61248.pktriot.net pktriot info

  sudo docker exec -it shifthunter-tunnel pktriot tunnel http add --domain shifthunter.com --destination /var/www/html/source --http 15050 --letsencrypt

  sudo docker exec -it shifthunter-tunnel pktriot tunnel http add --domain green-smoke-17402.pktriot.net --destination /var/www/html/source --http 15050 --letsencrypt

  # Remove Rule
  sudo docker exec -it shifthunter-tunnel pktriot tunnel http rm --domain shifthunter.com


  ss -anl | grep ":53"

  # Get All Listening Ports
  netstat -antp

```


## Video 1
[Real World DNS Google](https://www.youtube.com/watch?v=euXdC0NDgac)

## Video 2
[Introduction to packetriot](https://www.youtube.com/watch?v=ogi5ea2HyTs)

# Docker Container
> Using Docker? 
> Pull down our image packetriot/pktriot:latest. 

* Tip: docker exec > -it container-name before executing any commands with the client and restart between configuring and updating rules.



# Basic Commands
```bash

  sudo yum install pktriot

  sudo pktriot configure
  
  sudo pktriot info
  
 
  # With https
  # Fom Video 1
 sudo pktriot tunnel http add --domain summer-wildflower-77076.pktriot.net --destination /var/www/html/source --http 15050 --letsencrypt


  sudo pktriot tunnel http add --domain throbbing-sea-82929.pktriot.net --destination /var/www/shifthunter --http 15050 --webroot /var/www/shifthunter --letsencrypt

  sudo pktriot tunnel http add --domain shifthunter.com --webroot /var/www/shifthunter --http 15050 --letsencrypt

  sudo pktriot tunnel http add --domain jackpot.lottoaudit.co.uk --destination /var/www/html/source --http 15050 --letsencrypt

  sudo pktriot tunnel http add --domain restless-morning-58173.pktriot.net --webroot /var/www/shifthunter --http 15050 --letsencrypt
  
  sudo pktriot tunnel http add --domain shifhunter.com --webroot /var/www/shifthunter --http 15050 --letsencrypt


 sudo pktriot tunnel http add --domain restless-morning-58173.pktriot.net --destination /var/www/shifthunter --http 15050 --letsencrypt


  sudo pktriot tunnel http add --domain shifthunter.com --destination /var/www/html/source --http 15050 --webroot $PWD/var/www/html/source --letsencrypt

  sudo pktriot tunnel http add --domain jackpot.lottoaudit.co.uk --destination /var/www/html/source --http 15050 --letsencrypt

  # Fom Video 2
  sudo pktriot route http add --domain stoic-smoke-42450.pktriot.net --webroot $PWD/var/www/html/source
```

## Mount Unmount Drives Linux
```bash
 # Create a  dir for the driver
  ...
  mkdir -p /media/G
  ...
  mkdir -p /media/disk2
 
  # List all drives connected to get the name
  lsblk

  # Get the ID of the drive
  sudo blkid /dev/sda1
  
  /dev/sda1: LABEL="My Passport" BLOCK_SIZE="512" UUID="0ADAF673DAF65B01" TYPE="ntfs" PARTLABEL="My Passport" PARTUUID="6b5e005e-fefc-4b7b-be6e-8a86eeb7de4c"

  # ID
  UUID="0ADAF673DAF65B01"
  
  # Update the file
  sudo nano /etc/fstab 
  # <file system>     <mount point>       <type>     <options>     <dump>  <pass>
  UUID=1234-ABCE      /media/G      vfat       defaults      0       0
 
# Direct Mount
$ mkdir -p /home/user/usb
$ sudo mount /dev/sdc1 /home/user/usb
$ cd /home/user/usb
$ ls -l

$ mkdir -p /home/omartini/usb
$ sudo mount /dev/sda1 /home/omartini/usb
$ cd /home/omartini/usb

$ ls -l


# Unmount
sudo umount <device|directory>
sudo umount /dev/sda1
sudo umount /dev/sdb1

# Check if is mounted -> It shoul be empty
findmnt /dev/sda1

findmnt /dev/sdb1
<empty>

# Unmounting drives lazily
sudo umount -l <device|directory>
sudo umount -l /dev/sda1

# Force drive unmounting
sudo umount --force <device|directory>
sudo umount --force /dev/sda1

```

## Replace Text in Files
```bash
  sudo sed -i 's/firefox-esr.desktop/google-chrome-stable/g' ~/.config/mimeapps.list


  sudo sed -i 's/old_text/new_text/g' text.txt
```
## TAR Commands
```bash
  # Unzip Create folder
  tar -xvf bash.html_node.tar.gz --one-top-level
```

## CGMiner
```bash

sudo apt install build-essential autoconf automake libtool pkg-config libudev-dev libcurl4-openssl-dev git

# ThroubleShooting for  "libcurl4-openssl-dev"
# curl : Depends: libcurl4 (= 7.88.1-10+deb12u4) but 8.4.0-2~bpo12+1 is to be installed
sudo apt-get install libcurl4=7.88.1-10+deb12u4
sudo apt-get install libcurl4-openssl-dev

# sudo apt-get build-dep libcurl4-openssl-dev
sudo apt-get install libcurl4-openssl-dev


git clone https://github.com/dmaxl/cgminer
 
 or 

git clone https://github.com/ckolivas/cgminer

./autogen.sh


./configure --enable-scrypt --enable-gridseed

```

## Find Programs
```bash
  # In this example, search $HOME for all hidden files and dirs:
  find $HOME -name ".*" -ls

  # Find Grep
  systemctl list-unit-files | grep enabled | grep ssh

 # Find Files IN CURRENT FOLDER  AND DELETE
 
  find . -maxdepth 1 -name "*.sh" -type f

  find . -maxdepth 1 -name "*.sh" -type f -delete

  # Find Files
  sudo find / -name "VBoxManage" -print

  find /dir/to/search/ -name ".*" -print

  find /dir/to/search/ -name ".bash_profile" -print
  sudo find . -name ".bash_profile"

  find / -name ".kube" -print

 # Search only hidden files:
  find /dir/to/search/ -type f -iname ".*" -ls
  
  # Search only hidden directories:
  find /dir/to/search/ -type d -iname ".*" -ls

  find /etc/ -iname nginx.conf

  # Find packages
  sudo dpkg-query -L firefox

  sudo dpkg-query -l | grep package_name_to_search

  sudo dpkg-query -l | grep openresolv

  sudo dpkg-query -l | grep resolvconf
  
  sudo apt list --installed | grep openresolv

  sudo apt list --installed | grep resolvconf 
 

```

## Proccesses By Cmd Name
```bash
  ps -C pktriot
```
## Java Ubuntu Install
[Java Install](https://www.linuxcapable.com/how-to-install-openjdk-17-on-ubuntu-linux/)
[Java Alternatives](https://www.fosslinux.com/126168/how-to-switch-between-java-versions-in-ubuntu.htm)
```bash
 # Folder
 # mkdir /usr/lib/jvm 
 /usr/lib/jvm

wget https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz

sudo tar -xvf openjdk-17.*

sudo chmod 777 /usr/lib/jvm/jdk-17.0.2/

sudo nano ~/.bash_profile
# Add the Variables
export JAVA_HOME=/usr/lib/jvm/jdk-17.0.2
export PATH=$JAVA_HOME/bin:$PATH

# Reload the system variables
source ~/.bash_profile
source ~/.bashrc

# Actual PATH
printenv
PATH=/usr/lib/jvm/jdk-17.0.2/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:

  sudo apt install openjdk-17-jdk

  sudo apt remove openjdk-17-jre openjdk-17-jdk --purge

  apt-cache search openjdk | grep openjdk-17

# Step 3: Switching Alternative Java Versions on Ubuntu (Additional Commands)
 sudo update-alternatives --config java

```

## Get Path Link for Specific Package
```bash
  readlink -f $(which java) 

  readlink -f $(which pktriot) 
```

# Kuberbetes


## LCO Probe Docker File Kubernetes POD
[Java POD Kubernetes](https://briantward.github.io/running-java-on-kubernetes/)

[Desktop Says Desktop Stopped](https://stackoverflow.com/questions/72281976/docker-is-running-docker-desktop-says-docker-desktop-stopped)

* 1) Create the components of your container image
## Create Dockerfile 
```bash
  echo 'FROM openjdk:11
  COPY target/LCOProbe-RealTime.jar /LCOProbe-RealTime.jar
  CMD java -jar LCOProbe-RealTime.jar' > Dockerfile
```
* 2) Build the container image
## Build Docke  Image
```bash
  sudo docker build . --tag lco_probe
```
* 3) Tag the image to a registry you have access to pull from
## Tag Image
```bash
  sudo docker images | grep lco_probe

  sudo docker tag lco_probe shifthunter.com/omartini/lco_probe:latest

  # Remove tag
  sudo docker rmi shifthunter.com/hunter/lco_probe 

```
* 4) Push the image to the remote repository from which your image will pull.
##
```bash
  docker login osvaldo.martini
```

 ## Install Kubernetes
 [Install Kubernetes GOOD](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
 ```bash
1) Step
sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
2) Step
 sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
3) Step
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
# Expected
kubectl: OK
4) Install kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
5) Step
sudo chmod +x kubectl
mkdir -p ~/.local/bin
sudo mv ./kubectl ~/.local/bin/kubectl
6) Step
kubectl version --client
```

## K9s Install
```bash

  # Homebrew install
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  # Add Homebrew to your PATH
  (echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> /home/$USER/.bashrc

  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

  # k9s install
  brew install derailed/k9s/k9s

  # Windows
	choco install k9s

	# Linux
	sudo snap install k9s

  snap install k9s --channel=latest/stable

  snap refresh k9s --channel=latest/stable
```

mountPath