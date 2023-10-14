# Static IP Address Debiam
[How to Assign Static IP Address on Debian 12](https://www.linuxtechi.com/configure-static-ip-address-debian/)

## Cmd Line
```bash
  ip add show
```
![Ip Add Show](images/IP-Command-Output-Debian12-Command-Line-1024x657.webp)

* Next, run nmcli command to get connection name
```bash
$ nmcli connection
```
![Ip Add Show](images/nmcli-connection-command-debian12.webp)

* Once we get the connection name, run below nmcli command to assign static ipv4 address
> $ nmcli con mod  ‘connection-name’ ipv4.address  <IP-Address>
```bash
$ sudo nmcli connection modify 'Wired connection 1' ipv4.address 192.168.1.50/24
```
* Set the gateway by running below
```bash
$ sudo nmcli connection modify 'Wired connection 1' ipv4.gateway 192.168.1.1 
``` 