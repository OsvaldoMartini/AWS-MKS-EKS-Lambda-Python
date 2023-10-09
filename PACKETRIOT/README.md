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