# Basic Steps to Install JMeter on Linux

[Pepper-Box JMeter](https://github.com/GSLabDev/pepper-box/)
[JMeter Install](https://linux.how2shout.com/2-ways-to-install-apache-jmeter-on-ubuntu-22-04-lts-linux/)

[X11-Forwarding](https://aws.amazon.com/blogs/compute/how-to-enable-x11-forwarding-from-red-hat-enterprise-linux-rhel-amazon-linux-suse-linux-ubuntu-server-to-support-gui-based-installations-from-amazon-ec2/)

[kafka-aws-setup](https://github.com/abhinavdhasmana/kafka-aws-setup/tree/master)

```bash
  # Install JDK
  su -c "yum install java-1.8.0-openjdk-devel"

  or

  sudo apt install default-jdk
  
  # Install Maven
  sudo yum install maven -y

  # Download JMeter
  sudo wget https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.5.zip

  # Unzip
  sudo unzip apache-jmeter-5.5.zip

  # Rename folder
  sudo mv apache-jmeter-5.5 jmeter

  # Move to /opt directory
  sudo mv jmeter /opt

  # Add Jmeter do the system path
  sudo echo 'export PATH="$PATH:/opt/jmeter/bin"' >> ~/.bashrc

  # Start Jmeter
  jmeter

  # Throubleshooting
  # X11-forwarding 
  sudo yum install xorg-x11-xauth


  sudo chown -R ec2-user /opt/jmeter
  sudo chown -R root /opt/jm -R ec2-user /opt/jmeter

  # Reload printenv
  source ~/.bashrc
  or
  . ~/.bashrc

  # Removal of directories
  sudo rm -r /xyv/directory
```
# Creating Jmeter File
```bash
 # Make Dir ~/Desktop
  sudo mkdir ~/Desktop   # /usr/Desktop
```
```bash
  # Create This File
  sudo nano ~/Desktop/Jmeter.desktop
```  
  ***
  > ######  /usr/Desktop/Jmeter.desktop

    [Desktop Entry]
    Version=1.0
    Type=Application
    Name=Apache-Jmeter
    Comment=Testing
    Exec=/opt/jmeter/bin/./jmeter.sh
    Icon=/opt/jmeter/docs/images/jmeter_square.png
    Terminal=false
    StartupNotify=false
  *** 
```bash
  # File Permission
  sudo chmod 4775 ~/Desktop/Jmeter.desktop
```

# Pepper JMeter

## Clone Pepper-Box to **~/projects/pepper-box** folder 
```bash
sudo git clone https://github.com/GSLabDev/pepper-box.git ~/projects/pepper-box

cd ~/projects/pepper-box

## Package Pepper-Box
sudo mvn clean install -Djmeter.version=3.0 -Dkafka.version=0.9.0.1

cp -p /home/ec2-user/projects/pepper-box/target/pepper-box-1.0.jar  /opt/jmeter/lib/ext/pepper-box-1.0.jar
```
## Or Download direct from repository Git
```bash
cd /opt/jmeter/lib/ext

# Download from repository
wget https://github.com/raladev/load/raw/master/JARs/pepper-box-1.0.jar
```
# Message App
> Create Kafka payload jar file, Message.jar. 

> Copy this file to the **/jmeter/lib/ext** folder of JMeter

## Copy from Repository
```bash
wget -P /opt/jmeter/lib/ext https://github.com/abhinavdhasmana/kafka-aws-setup/blob/master/JMeter/Message.jar 

```

## Message Java Code

```java
package com.gslab.pepper;
import java.io.Serializable;
public class Message  implements Serializable{

    private long messageId;
    private String messageBody;
    private String messageBodyTwo;
    private String messageBodyThree;
    private String messageBodyFour;
    private String messageBodyFive;
    private String messageBodySix;
    private String messageBodySeven;
    private String messageStatus;
    private String messageCategory;
    private long messageTime;

    public long getMessageId() {
        return messageId;
    }

    public void setMessageId(long messageId) {
        this.messageId = messageId;
    }

    public String getMessageBody() {
        return messageBody;
    }
    public String getMessageBodyTwo() {
        return messageBodyTwo;
    }
    public String getMessageBodyThree() {
        return messageBodyThree;
    }
    public String getMessageBodyFour() {
        return messageBodyFour;
    }
    public String getMessageBodyFive() {
        return messageBodyFive;
    }
    public String getMessageBodySix() {
        return messageBodySix;
    }
    public String getMessageBodySeven() {
        return messageBodySeven;
    }

    public void setMessageBody(String messageBody) {
        this.messageBody = messageBody;
    }
    public void setMessageBodyTwo(String messageBodyTwo) {
        this.messageBodyTwo = messageBodyTwo;
    }
    public void setMessageBodyThree(String messageBodyThree) {
        this.messageBodyThree = messageBodyThree;
    }
    public void setMessageBodyFour(String messageBodyFour) {
        this.messageBodyFour = messageBodyFour; 
    }
    public void setMessageBodyFive(String messageBodyFive) {
        this.messageBodyFive = messageBodyFive;
    }
    public void setMessageBodySix(String messageBodySix) {
        this.messageBodySix = messageBodySix;
    }
    public void setMessageBodySeven(String messageBodySeven) {
        this.messageBodySeven = messageBodySeven;
    }


    public String getMessageStatus() {
        return messageStatus;
    }

    public void setMessageStatus(String messageStatus) {
        this.messageStatus = messageStatus;
    }

    public String getMessageCategory() {
        return messageCategory;
    }

    public void setMessageCategory(String messageCategory) {
        this.messageCategory = messageCategory;
    }

    public long getMessageTime() {
        return messageTime;
    }

    public void setMessageTime(long messageTime) {
        this.messageTime = messageTime;
    }
}
```

# JMX JMeter 15k per seconds Performance file
```bash
  sudo mkdir ~/projects/JMeter-Performance-Tests

  wget -P ~/projects/JMeter-Performance-Tests https://github.com/abhinavdhasmana/kafka-aws-setup/blob/master/JMeter/kafka_loadtest.jmx

  # Rename File
  mv kafka_loadtest.jmx Kafka-15K-Per-Seconds-Load-Test.jmx

  # Permissions

  sudo chmod 777 ~/projects/JMeter-Performance-Tests

  sudo chmod 777 Kafka-15K-Per-Seconds-Load-Test.jmx
```

# Docker Install
```bash
#./install.sh

#! /bin/sh
sudo apt-get update

sudo apt-get -y install \
apt-transport-https \
ca-certificates \
curl \
gnupg-agent \
software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) \
stable"

sudo apt-get update

sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-compose
```

# JMeter  Heap Increasing its heap size
## Run jmeter by giving by increasing its heap size
```bash
  jmeter HEAP=”-Xms512m -Xmx24g” -n -t Kafka-15K-Per-Seconds-Load-Test.jmx
```