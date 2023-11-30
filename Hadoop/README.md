# Haddop



# Docker Compose  - docker-compose Debian 12 / Ubuntu
[Docker-compose](https://wiki.crowncloud.net/?How_to_Install_and_use_Docker_Compose_on_Debian_12)

```bash
curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose

docker-compose --version
```

# Good Hadoop
[Docker Hadoop](https://www.youtube.com/watch?v=dLTI2HN9Ejg)
[Git Docker Hadoop](https://github.com/big-data-europe/docker-hadoop/tree/master)
```bash

git clone https://github.com/big-data-europe/docker-hadoop/tree/master

cd docker-hadoop/

docker-compose up

docker exec -it namenode /bin/bash

# Listing the directories
hdfs dfs -ls /
  # We can ignore this one
  drwxr-xr-x   - root supergroup          0 2023-11-22 12:28 /rmstate

# Creating Directories
hdfs dfs -mkdir /user/root
 # mkdir: `hdfs://namenode:9000/user': No such file or directory

hdfs dfs -mkdir -p /user/root

#  Delete Directory
hdfs dfs -rm- r /user/root
```

## Instal ifconfig
```bash
sudo apt update
sudo apt install net-tools
ifconfig
```

## Open the Browser
```bash
google-chrome

http://192.168.1.50:9870/dfshealth.html#tab-overview
```

## Download Examples Jar file to test MapReduce Job
```bash
cd docker-hadoop/

https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-mapreduce-examples/2.7.1/


wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-mapreduce-examples/2.7.1/hadoop-mapreduce-examples-2.7.1-sources.jar
```

## Copy file into the Docker Container
```bash
docker cp hadoop-mapreduce-examples-2.7.1-sources.jar namenode:/tmp/
# Successfully copied 699kB to namenode:/tmp/
```

## Create same example input text file
``` vi input1.txt
hello test file
hello world
```
## Copy file into the Docker Container
```bash
docker cp input1.txt namenode:/tmp/
# Successfully copied 699kB to namenode:/tmp/
```

## Docker EXEC Container Bash
```bash
docker exec -it namenode /bin/bash
```

## Uploadin File "INPUT1.TXT" into DFHS
```bash
# Create the directory for Input File

hdfs dfs -mkdir /user/root/input

# Put the File into the directory
hdfs dfs -put input1.txt   /user/root/input
  2023-11-22 13:02:14,104 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false

hdfs dfs -cat /user/root/input/input1.txt
  2023-11-22 13:03:28,707 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
  hello test file
  this is sample input
  hello world
```

## Run Hadoop Jar Command with class Name
```bash

hadoop jar hadoop-mapreduce-examples-2.7.1-sources.jar org.apache.hadoop.examples.WordCount input output
```
## Check the Results created
```bash
hdfs dfs -ls /user/root/output

hduser@localhost:~$ hdfs dfs -cat output/*
1 dfsadmin
1 dfs.replication
1 dfs.permissions

```

## Docker Compoese Down
```bash
docker-compose down
```



































## Another Haddop That Not Worked  
[HADOOP Single Cluster](https://medium.com/analytics-vidhya/hadoop-single-node-cluster-on-docker-e88c3d09a256)

## Creating the Hadoop image
```bash
$ git clone https://github.com/rancavil/hadoop-single-node-cluster.git
$ cd hadoop-single-node-cluster
$ docker build -t hadoop .
```

```bash
$ docker run -it — name <container-name> -p 9864:9864 -p 9870:9870 -p 8088:8088 — hostname <your-hostname> hadoop

$ docker run -it — name hadoop -p 9864:9864 -p 8080:9870 -p 8088:8088 — hostname localhost hadoop

$ sudo docker run -it --name docker.io/library/hadoop -p 9864:9864 -p 9870:9870 -p 8088:8088 -hostname admin-node hadoop
```

