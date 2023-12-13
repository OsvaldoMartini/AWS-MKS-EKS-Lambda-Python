# 2 Ways to Install GitHub Desktop on Debian 12 and 11
[GitHub Desktop](https://linux.how2shout.com/2-ways-to-install-github-desktop-on-debian-12-11-10/)


### Create Private Access Token on Github Developers
To use the “store” option, create a credentials file at <span style="color: yellow;">~/.git-credentials</span>. Enter a single line:
```bash
sudo nano ~/.git-credentials
```
Include the token  login here
```bash
https://{username}:{personal_access_token}@github.com


https://osvaldo.martini:{personal_access_token}@github.com
```

Then run to set up the git config global
```bash
git config --global credential.helper store
```

If you would like to store the credentials file elsewhere, run
```bash
git config --global credential.helper 'store --file /path/to/credentials/file'
```


### 1. Update your Debian Linux

```bash
sudo apt update && sudo apt upgrade
```

### 2. Add GitHub Desktop Repository

Well, the first method we are going to use is the “Apt Repository” method, using the given commands add the Shift key repository that offers the packages to install and later update GitHub Desktop using the terminal.

* Import GPG Key:
```bash
wget -qO - https://apt.packages.shiftkey.dev/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/shiftkey-packages.gpg > /dev/null
```
* After that add the repository that’s packages are signed by the above-added GPG key.

```bash
sudo sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/shiftkey-packages.gpg] https://apt.packages.shiftkey.dev/ubuntu/ any main" > /etc/apt/sources.list.d/shiftkey-packages.list'
```

* After adding the repository, run the system update command:

```bash
sudo apt update -y
```

### 3. Installing GitHub Desktop on Debian 12, 11, or 10
* Once the repository is added, we can use the default APT package manager of Debian to install the GitHub desktop app using the command terminal. Here is the one to follow:

```bash
sudo apt install github-desktop
```


### 4. Download GitHub Desktop Deb binary
Those who don’t want to use the APT method for the installation of this GUI Git app can directly download its binary from GitHub’s official website. Here is the Github Shiftkey repo link to follow.

![Debian Github Desktop](Download-GitHub-Desktop-Deb-binary.png)


### 5. Install the Binary

After downloading the binary of the GitHub Desktop app, open your command terminal and switch to the Downloads directory, first. It is because whatever we download from the browser, goes into that.

```bash
cd Downloads
```
* Use the DPKG tool to install it:

```bash
sudo dpkg -i GitHubDesktop-linux-*-linux1.deb
```

### 6. Run the Git GUI on Debian

Having the GitHub Application on your Debian Linux after following any of the above-given methods, we can run it. So, to launch the app, either press the Win key on your keyboard or click go to the Application menu and there search for it. As its icon appears, click to open the app.

![GUI Github Desktop](Git-GUI-on-Debian-12.png)

* Cmd Line

```bash
github-desktop
```