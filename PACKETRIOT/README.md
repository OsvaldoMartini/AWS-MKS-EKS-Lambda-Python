# Packetriot
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

  pktriot configure
  
  pktriot info
  
  # With https
  # Fom Video 1
  pktriot tunnel http add --domain stoic-smoke-42450.pktriot.net --destination /var/www/html/source --http 15050 --letsencrypt

  pktriot tunnel http add --domain jackpot.lottoaudit.co.uk --destination /var/www/html/source --http 15050 --letsencrypt

  # Fom Video 2
  pktriot route http add --domain stoic-smoke-42450.pktriot.net --webroot $PWD/var/www/html/source



```