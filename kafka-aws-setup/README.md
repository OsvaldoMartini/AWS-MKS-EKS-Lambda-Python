# Kafka AWS Setup  15K Per Seconds
[Kafka AWS Setup](https://itnext.io/how-to-setup-kafka-cluster-for-15k-events-per-second-on-aws-using-docker-d34539873589)

## Docker How To Tail Logs
 
## You can tail the logs of a docker container like this:
```bash
  docker logs zookeeper
```

## If you want to continously follow the logs and watch any updates as they happen, use “-f” like this:
```bash
  docker logs -f zookeeper
```
## You can also specify the number of lines ( ex: last 100 ) like this:
```bash
  docker logs -n 100 zookeeper
```
## You can follow and specify the number of lines like this:
```bash
  docker logs -f -n 100 zookeeper
```
## You could follow but only for 30 seconds like this:
```bash
  docker logs -f --until=30s
```  
# Zookeeper LINK and Misc
[Zookeper Basics](https://low-orbit.net/docker-zookeeper)