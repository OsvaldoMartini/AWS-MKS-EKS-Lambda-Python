# CPFLAGS   and MISC
## How to compile cgminer on Ubuntu
```bash
git clone https://github.com/ckolivas/cgminer.git
cd cgminer
./autogen.sh --enable-opencl
CFLAGS="-O2 -Wall -march=native -I/opt/AMDAPP/include" LDFLAGS="-L/opt/AMDAPP/lib/x86_64" ./configure --enable-opencl
make
./cgminer --url  stratum+tcp://pool --user username --pass password

export CPFLAGS=
export CFLAGS="-g -O2"
export LDFLAGS="-lpthread"
export LDADD="-ldl -lcurl   -L/usr/local/lib -ljansson  -lz -lpthread    -lm -lusb-1.0  -lrt"
export LIBCURL_CFLAGS=-I/usr/local/opt/curl/include
export LIBCURL_LIBS=-L/usr/local/opt/curl/lib

export CFLAGS="-O2 -Wall -march=native -I/opt/AMDAPP/include"
export LDFLAGS="-L/opt/AMDAPP/lib/x86_64"



export LDFLAGS=-L/usr/local/opt/curl/lib
export CPPFLAGS=-I/usr/local/opt/curl/include
./configure


OR

export LIBCURL_CFLAGS=-I/usr/local/opt/curl/include
export LIBCURL_LIBS=-L/usr/local/opt/curl/lib
./configure

```

## Another Way
```bash

CFLAGS="-O2 -Wall -march=native -I/opt/AMDAPP/include" LDFLAGS="-L/opt/AMDAPP/lib/x86_64" ./configure --enable-opencl

CFLAGS="-O2 -Wall -march=native -I/opt/AMDAPP/include" LDFLAGS="-L/opt/AMDAPP/lib/x86_64 -Wall -v" ./configure --disable-cpumining --enable-opencl --enable-cointerra && make
```


## Cersion  4.11.1
```bash
./autogen.sh --enable-opencl


Compilation............: make (or gmake)
  CPPFLAGS.............:
  CFLAGS...............: -O2 -Wall -march=native -I/opt/AMDAPP/include
  LDFLAGS..............: -L/opt/AMDAPP/lib/x86_64 -lpthread
  LDADD................: -ldl -lcurl   compat/jansson-2.9/src/.libs/libjansson.a -lz -lpthread    -lm  -lrt

Installation...........: make install (as root if needed, with 'su' or 'sudo')
  prefix...............: /usr/local


CPPFLAGS="" CFLAGS="-O2 -Wall -march=native -I/opt/AMDAPP/include" LDFLAGS="-L/opt/AMDAPP/lib/x86_64 -lpthread" LDADD="-ldl -lcurl   compat/jansson-2.9/src/.libs/libjansson.a -lz -lpthread    -lm  -lrt" make

```

