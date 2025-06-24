---
layout: post
title:  "Building Numba from source on Ubuntu"
date:   2025-06-20 08:00:00 +1000
categories: recipe
---

[Numba](https://numba.pydata.org/) is an essential part of the scientific software toolkit
and is used by a number of the UBARSC projects. The normally recommended approach is to 
install via Conda Forge. However, while this may be fine for desktop usage, you may want
to have more control over how it is built and the version that is used in a cloud or HPC 
setting. 

Ubuntu is a common choice for cloud computing. It provides many useful packages that remain
at fixed versions in a given Ubuntu release. However, the Numba package connot always
be relied on to exist for every Ubuntu release. It has also been broken on ARM64 in some
versions. Fortunately, building Numba from source isn't actually too hard. Some 
[instructions](https://numba.readthedocs.io/en/stable/user/installing.html#installing-from-source)
do exist which this recipe is based on. 

Firstly, consult [the Numba version information](https://numba.readthedocs.io/en/stable/user/installing.html#version-support-information)
table to determine a supported LLVM/llvmlite/Numba version combination and export these as 
environment variables. For example:

```
export LLVM_VERSION=15.0.7
export LLVMLITE_VERSION=0.44.0
export NUMBA_VERSION=0.61.2
```

Also set an environmental variable for where you wish to install Numba. Normally, this is `/usr` but you 
may which to install Numba in a separate location.
```
export MY_PREFIX=/usr
```

You will also need to ensure `g++`, `cmake`, `make`, `patch` and `python3` Ubuntu packages are installed.

Download llvm and llvmlite at the same time as we need the patches and build instructions from the latter. Extract
to `/tmp` and get ready for compliation:

```
cd /tmp
wget https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVM_VERSION}/llvm-project-${LLVM_VERSION}.src.tar.xz
wget https://github.com/numba/llvmlite/archive/refs/tags/v${LLVMLITE_VERSION}.tar.gz
tar xf v${LLVMLITE_VERSION}.tar.gz
tar xf llvm-project-${LLVM_VERSION}.src.tar.xz
cd llvm-project-${LLVM_VERSION}.src
```

Apply the provided patches and use the provided `build.sh` to compile LLVM statically. Static LLVM is the preferred method for building
Numba. This ensures no conflicts with other versions of LLVM that may be present on the system - since there are a 
number of custom patches required this is a sensible precaution. Install static LLVM to `tmp/llvmout`.

Ensure `set -e` is set on their build.sh so any sub command faiure stops the build - this is similar to how conda does it.

```
cd llvm-project-${LLVM_VERSION}.src
for p in ../llvmlite-${LLVMLITE_VERSION}/conda-recipes/*.patch; do patch -p1 -i $p; done
echo "set -e" > ./mybuild.sh
cat ../llvmlite-${LLVMLITE_VERSION}/conda-recipes/llvmdev/build.sh >> ./mybuild.sh
PREFIX=/tmp/llvmout CPU_COUNT=2 bash ./mybuild.sh 
cd ..
```

Now compile and install llvmlite, telling it where to find LLVM:
```
cd llvmlite-${LLVMLITE_VERSION}
LLVM_CONFIG=/tmp/llvmout/bin/llvm-config python3 setup.py install --prefix=${MY_PREFIX}
cd ..
```
LLVM is no longer needed at this point as the necessary parts have been linked into `llvmlite` statically. 
Nexit, clean up:
```
rm -rf llvm-project-${LLVM_VERSION}.src.tar.xz \
    llvm-project-${LLVM_VERSION}.src \
    v${LLVMLITE_VERSION}.tar.gz \
    llvmlite-${LLVMLITE_VERSION} \
    /tmp/llvmout
```

Last step is to install Numba itself:
```
wget https://github.com/numba/numba/archive/refs/tags/${NUMBA_VERSION}.tar.gz
tar xf ${NUMBA_VERSION}.tar.gz
cd numba-${NUMBA_VERSION}
python3 setup.py install --prefix=${MY_PREFIX} --single-version-externally-managed --record record.txt
cd ..
rm -rf ${NUMBA_VERSION}.tar.gz numba-${NUMBA_VERSION}
```

Probably a good idea to run some tests at this point. You will need to ensure that your `PYTHONPATH` includes
your install locatiotion if you have set `MY_PREFIX` to something non standard:
```
python3 -c "import numba"
python3 -m numba.runtests
```
Note `numba.runtests` takes a very long time and needs a lot of memory.

