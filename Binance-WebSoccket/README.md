## Binance Python
```bash

 pip3 install -r requirements.txt

 pip3 install python-binance
```


## FLASK install and Throubleshooting
[FLASK Minimal](https://flask.palletsprojects.com/en/1.1.x/quickstart/)

## CC.EXE
error: command 'C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.31.31103\\bin\\HostX86\\x64\\cl.exe' failed with exit code 2
```bash
  python -m pip install -U pip setuptools

  pip install --upgrade pip
  pip install discord

```

```bash
export FLASH_APP=app.py
## Windows 
set FLASK_APP=app.py //(for windows)
flask run
```

## PIP Lilast Packages Pyhton
Difference Between pip list and pip freeze
The main difference between pip list and pip freeze is that pip freeze does not include packages used for package management, such as pip and setuptools.

For example, here are the outputs of pip list and pip freeze for the same
```bash
pip list
pip freeze
```


## FLASK Debug Mode
```bash

brew list | grep python

ls /usr/bin/python*


sudo apt purge -y python2.7-minimal
sudo apt purge -y python*


flask run --debug

OR
$ export FLASK_ENV=development
set FLASK_ENV=development //(for windows)
$ flask run
```

## Trhoubleshooting TA-LIB


# INSIDE OF THE VS2015 (OR LATER ) NATIVE TOOLS
[HOW TO INSTALL TA-LIB ON WINDOWS](https://pypi.org/project/TA-Lib/)

```bash
Download ta-lib-0.4.0-msvc.zip and unzip to C:\ta-lib.

This is a 32-bit binary release. If you want to use 64-bit Python, you will need to build a 64-bit version of the library. Some unofficial (and unsupported) instructions for building on 64-bit Windows 10, here for reference:

Download and Unzip ta-lib-0.4.0-msvc.zip
Move the Unzipped Folder ta-lib to C:\
Download and Install Visual Studio Community (2015 or later)
Remember to Select [Visual C++] Feature
Build TA-Lib Library
From Windows Start Menu, Start [VS2015 x64 Native Tools Command Prompt]
Move to C:\ta-lib\c\make\cdr\win32\msvc
Build the Library nmake
```

# AFTER TRY TO RUN ON WINDOWS AGAIN
```bash
pip install -r requirements.txt
```



## TA-LIB
[TA-LIB](https://ta-lib.github.io/ta-lib-python/install.html)
```bash
pip3 install TA-Lib
```

## Troubleshootihg TA-LIB
```bash
Linux
Download ta-lib-0.4.0-src.tar.gz and:

$ untar and cd
$ ./configure --prefix=/usr
$ make
$ sudo make install
If you build TA-Lib using make -jX it will fail but that's OK! Simply rerun make -jX followed by [sudo] make install.

```