## Install Python Latest
[Python Latest](https://www.linuxcapable.com/how-to-install-python-3-9-on-debian-linux/)

Install Python 3.9 on Debian 12, 11, or 10 via source
Step 1: Update Debian Before Python 3.9 Installation
Before installing Python 3.9, update your Debian system packages:

sudo apt update && sudo apt upgrade
Step 2: Install Development Packages for Python 3.9
In this step, we will install a group of packages necessary for compiling Python from the source code. These packages include development libraries and utilities that will facilitate the compilation process:

sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev -y
Step 3: Download Python 3.9 Source Code
Next, download the Python 3.9 source code from the official Python website. Make sure to download the latest version of Python 3.9, which at the time of this writing is Python 3.9.17.

It’s advisable to visit the official Python website to verify if there is a newer release version available. The link provided in this guide serves as an example; be sure to modify it accordingly to download the most recent version in the future.

wget https://www.python.org/ftp/python/3.9.17/Python-3.9.17.tar.xz
Step 4: Extract Python Archive and Move to Appropriate Directory on Debian
Once you download the source code, extract it:

tar -xf Python-3.9.17.tar.xz
Next, move the extracted files to a standard directory. Here, we use /usr/local/share:

mv Python-3.9.17 /usr/local/share/python3.9
Step 5: Configure, Compile, and Install Python 3.9 on Debian
Go to the directory with the Python source code. Run the ./configure script with optimization and shared library flags:

cd /usr/local/share/python3.9
./configure --enable-optimizations --enable-shared
The --enable-optimizations flag optimizes the Python binary, and --enable-shared builds shared libraries. If you want pip alongside Python, add --with-ensurepip=install.

Now, compile the source code:

make
For faster compilation on multi-core systems, use the -j flag. For instance, to use 5 CPU cores:

make -j 5
Once the compilation is completed, install Python. Use the make altinstall command to avoid overwriting the system’s default Python:

sudo make altinstall
Configure the dynamic linker run-time bindings:

sudo ldconfig /usr/local/share/python3.9
Lastly, check your Python 3.9 installation:

python3.9 --version
You should see output indicating the installed Python version, similar to:

Python 3.9.17

Create a Virtual Environment with Python 3.9 on Debian 12, 11 or 10
Step 1: Create a Test Project Directory on Debian
Start by making a directory for your Python project and setting up the virtual environment inside it. Use these commands to make a directory called test_app and go into it:

mkdir ~/test_app
cd ~/test_app
Step 2: Set Up a Virtual Environment
Now that you’re in the project directory, it’s time to create the virtual environment. We’ll use Python’s venv module, which has been part of Python since version 3.3.

Create a virtual environment called test_app_venv with this command:

python3.9 -m venv test_app_venv
Here, -m venv signifies the utilization of the venv module. test_app_venv is designated as the virtual environment’s name, though you can confer any name that aligns with your project.

Step 3: Activate the Virtual Environment
With the virtual environment created, you need to activate it. When activated, any Python commands and installations will only affect this environment.

Activate the virtual environment with this command:

source test_app_venv/bin/activate
When the virtual environment is active, you’ll see its name at the beginning of the terminal prompt:

(test_app_venv) root@debian:~/test_app# 
This shows you’re working inside the test_app_venv environment. Any Python packages you install will only be available in this environment.

Step 4: Deactivate the Virtual Environment
When you’re done working in the virtual environment, deactivate it to return to the system-wide Python environment. Do this by entering:

deactivate
After deactivation, the name of the virtual environment will disappear from the terminal prompt, showing you’ve left the virtual environment.

Install Pip with Python 3.9 on Debian 12, 11, or 10
In this section, you’ll learn how to install Pip, Python’s package manager, and Python 3.9. Pip makes it easier for Python developers to install and manage Python libraries and packages.

Step 1: Validating the Installation of Pip
Check if Python 3.9 already has Pip installed by using the command:

python3.9 -m pip --version
If the command displays the Pip version, you already have it installed. Otherwise, follow the next steps to install Pip.

You can just use python instead of python3.9 if you just have this version installed and depending on your setup.

Step 2: Download the Pip Installation Script on Debian
To install Pip with Python 3.9, you need the get-pip.py script. Use the following command to download this script:

wget https://bootstrap.pypa.io/get-pip.py
This command saves the get-pip.py script in your current directory.

Step 3: Integrating Pip with Python 3.9
Now, use the downloaded script to install Pip by running:

python3.9 get-pip.py
This command tells Python 3.9 to run the script and install Pip.

Step 4: Upgrading Pip to the Latest Version
It’s a good idea to ensure you’re using the latest version of Pip. To upgrade Pip, use the command:


AD
python3.9 -m pip install --upgrade pip
This command upgrades Pip to the latest available version.

Step 5: Confirming the Pip Installation on Debian
After installation and upgrade, ensure that Pip works as expected. Check the installed version with:

python3.9 -m pip --version
The command should display the latest Pip version.