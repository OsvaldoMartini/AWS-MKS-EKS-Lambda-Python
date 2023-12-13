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