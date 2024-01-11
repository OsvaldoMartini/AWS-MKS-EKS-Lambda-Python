# THROUBLESHOOTING Tulind 

[msvs_version](https://stackoverflow.com/questions/57879150/how-can-i-solve-error-gypgyp-errerr-find-vsfind-vs-msvs-version-not-set-from-c)

## Chech the values on **".npmrc"**

```bash
npm install --global --production windows-build-tools

npm config get msvs_version

npm config set msvs_version "C:\Program Files\Microsoft Visual Studio\2022\Community"


npm config get msbuild_path

npm config set msbuild_path="C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"


VCTargetsPath=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\
VS140COMNTOOLS=C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools

msvs-version=2022
msbuild-path=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe

msvs_version=2022
msbuild_path=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe


```
