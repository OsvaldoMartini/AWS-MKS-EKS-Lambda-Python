```bash


ssh-keygen -t ed25519 -C "osvaldo.martini@gmail.com"


eval "$(ssh-agent -s)"

ssh-add ~/.ssh/id_ed25519


chmod 400 ~/.ssh/id_ed25519.pub

Include the id_ed25519.pub into to SSH keys Github Account

git config --global user.name "osvaldo.martini"

git config --global user.email "osvaldo.martini@gmail.com"

git config --global --list


git remote set-url origin https://github.com/OsvaldoMartini/AWS-MKS-EKS-Lambda-Python

```