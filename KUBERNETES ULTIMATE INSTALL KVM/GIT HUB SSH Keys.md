
(Dbian Packages)(https://github.com/git-ecosystem/git-credential-manager/releases/tag/v2.3.2)
```bash

brew install --cask git-credential-manager

sudo dpkg -i git-credential-manager
git-credential-manager configure


ssh-keygen -t ed25519 -C "osvaldo.martini@gmail.com"


eval "$(ssh-agent -s)"

ssh-add ~/.ssh/id_ed25519


chmod 400 ~/.ssh/id_ed25519.pub

Include the id_ed25519.pub into to SSH keys Github Account

git config --global user.name "osvaldo.martini"

git config --global user.email "osvaldo.martini@gmail.com"

git config --global --list

nano ~/.gitconfig

git remote -v

git remote add origin https://github.com/OsvaldoMartini/AWS-MKS-EKS-Lambda-Python.git

// HTTPS
git remote set-url origin https://github.com/OsvaldoMartini/AWS-MKS-EKS-Lambda-Python.git

// SSH
git remote set-url origin git@github.com:OsvaldoMartini/AWS-MKS-EKS-Lambda-Python.git


user: osvaldo.martini
Accss Token: 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

sudo ufw allow from 140.82.121.3 to any port 22 proto tcp

```