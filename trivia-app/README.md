## Installing and run Integration Tests  
### "pyyaml" package
```bash
  pip3 install -U -r .\back-end-python\gameactions\requirements.txt
```

### "Tests" Requeriments packages
```bash
  pip3 install -U -r .\back-end-python\tests\requirements.txt 
```

## Set ".Env" file for Environment Variables

```bash
  cd ./back-end-python/
  create file ".env"

  # Environment Variable

  AWS_SAN_STACK_NAME=trivia-app
```

## Setting the Test IDE Tests
### I need tyo Tell the IDE what tests we have

* Command Pallet <Ctlr + Shift + P>
* Search for "Python: Configure Tests
* Selecy "pytest" framework -> "tests" folder

## VsCode Pytest Configuration file
>settings.json
```bash

  # /.vscode/

  {
      "python.testing.pytestArgs": [
          "tests"
      ],
      "python.testing.unittestEnabled": false,
      "python.testing.nosetestsEnabled": false,
      "python.testing.pytestEnabled": true
  }
```

## Yaml Package
```bash
  pip install pyyaml
```






## WSL  Good fixes
```
 Good

 https://www.thewindowsclub.com/fix-0x80072eff-wsl-error-on-windows-computer

Copy and paste the following command lines one by one and press Enter on your computer keyboard.

net start LxssManager & net stop LxssManager & net start LxssManager
rd /s /q c:\Windows\SoftwareDistribution
Dism /online /Disable-Feature /FeatureName:Microsoft-Windows-subsystem-Linux
Dism /online /Enable-Feature /FeatureName:Microsoft-Windows-subsystem-Linux
Dism /online /Disable-Feature /FeatureName:Microsoft-Hyper-V-All
Dism /online /Enable-Feature /FeatureName:Microsoft-Hyper-V-All
wsreset.exe
Dism /Online /Cleanup-Image /RestoreHealth

https://github.com/microsoft/WSL/issues/8561

https://github.com/microsoft/WSL/issues/4618

```

## WSL  fixes
```

	Check the Microsoft Repairs Page
	Use the System File Checker tool to repair missing or corrupted system files
	
	https://support.microsoft.com/en-us/topic/use-the-system-file-checker-tool-to-repair-missing-or-corrupted-system-files-79aa86cb-ca52-166a-92a3-966e85d4094e

  Run the System File Checker tool (SFC.exe)
  
  DISM.exe /Online /Cleanup-image /Restorehealth
  
  or
  
  sfc /scannow




> wsl --list --verbose
  NAME                    STATE           VERSION
* rancher-desktop-data    Stopped         2
  rancher-desktop         Stopped         2
> wsl --unregister docker-desktop-data
Unregistering...
There is no distribution with the supplied name.
> wsl --unregister rancher-desktop-data
Unregistering...

> wsl --unregister rancher-desktop
Unregistering...

> wsl --list --verbose
	Windows Subsystem for Linux has no installed distributions.
	Distributions can be installed by visiting the Microsoft Store:
	https://aka.ms/wslstore

> wsl -l
Windows Subsystem for Linux has no installed distributions.
Distributions can be installed by visiting the Microsoft Store:
https://aka.ms/wslstore
>

Youtube Steps WSL
https://www.bing.com/videos/riverview/relatedvideo?&q=cmd%20line%20instal%20wsl&mid=A9D1BB0F4E861EE4FA11A9D1BB0F4E861EE4FA11&ajaxhist=0


Installing, this may take a few minutes...
WslRegisterDistribution failed with error: 0x80070002
Error: 0x80070002 The system cannot find the file specified.

``

