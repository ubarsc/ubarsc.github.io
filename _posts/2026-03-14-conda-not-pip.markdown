---
layout: post
title:  "Distributing our software - conda-forge, not pip/PyPI"
date:   2026-03-14 10:00:00 +1000
categories: tutorial
---

# Introduction

Several of the packages available from the UBARSC group are most easily installed using the `conda` command. Some users are more familiar with using the `pip` command to download & install Python packages, and have wondered why we do not make our packages available in this way. What follows is a discussion of the major issues and reasons for this choice. Note that this is not a tutorial on the usage of either system.

# What Are Pip, Conda, PyPI and Conda-forge

The `pip` command is a tool for installing Python packages. It understands the conventions used for distributing Python packages, and can be used to perform the installation directly from a source repository or `.tar.gz` distribution file. By default it will install things from the Python Package Index website (PyPI), handling all downloading directly. It understands when other Python packages are needed as dependencies for the target package, and will download and install those as well.

The `conda` command is a package manager with a much broader scope. It can install anything which has been packaged up for conda-based installation, and has no particular bias towards Python packages or anything else.

The PyPI website is a large repository for distributing Python packages, aimed at making it easy to download and install anywhere. It distributes both pure Python source, and pre-built "wheel" files (`.whl`) which might include compiled C-extension modules. It is the default source for packages to be installed by the `pip` command.

The conda ecosystem was developed by a private company, Anaconda (formerly Continuum Analytics), which sells (among other things) their services for software packaging and distribution. They have worked collaboratively with the open source community to maintain the conda tool and specifications, and host alternative community distribution channels. The major such alternative channel is `conda-forge`, and it is through this channel that we at UBARSC distribute our software. The `conda-forge` channel includes distributions for a wide range of data science related software, including binary distributions for many tools and libraries unrelated to Python.

# Pip/PyPI vs conda/conda-forge

The PyPI repository is fine for distributing packages which are pure Python. All that is required is the Python source code, and some small text configuration files. However, distributing packages
which are written in something other than Python is not really supported (although it can be kludged around, in some cases). A good example would be the KEA file format. The KEA library is written in
C++, and while there is also a Python binding, this is largely separate from the library code
itself. PyPI and the `pip` command don't really have any idea what to do with all that.

Another more important example is the GDAL library. This is also written in C++, with an optional
Python binding, and again, PyPI/pip has little to offer.

For example, RIOS depends very heavily on GDAL. So, if we were to distribute RIOS though PyPI, we ought to include this dependency in its `requirements.txt` file. However, if we did that, then `pip` would try to install GDAL from PyPI. The GDAL Python bindings are present in PyPI, but this is just the bindings, not the library itself, and so GDAL would still not be installed. If we do not specify the dependency, then the situation would be just as bad, and with little guidance for the novice user.

So, one would have to rely on something like `conda` to install GDAL itself.

The GDAL bindings also require numpy. However, numpy is also fully available from PyPI. This means that, depending on what else is installed, it is possible to have a numpy from PyPI and a GDAL from conda, and they may well be compiled in ways which are incompatible at the binary level, resulting in serious conflicts at run time.

Things can become even more complicated when one or more packages installed from PyPI include their own copies of binaries from other libraries. A good example of this is `rasterio`, which bundles its own copy of the GDAL binaries. These may be compiled with different options than any already installed version of GDAL, potentially causing all kinds of headaches.

To avoid much of this complexity, we have concluded that it is simpler just to rely on `conda` to distribute our packages, and everything on which they depend.

There is a great deal of discussion on some of these points spread all over the Internet. [This article](https://www.anaconda.com/blog/understanding-conda-and-pip) from Anaconda provides a brief overview (although slightly out of date).

As discussed in that article, `conda` and `pip` can work moderately well together, and this is useful for adding in small pure Python packages which are not available in conda. However, one does need to watch for pip's tendency to try to install its own dependencies, and upgrade things which conda has already installed, resulting in incompatible combinations of binaries. For this reason it is strongly recommended that any package (including dependencies) which contains compiled binary files should come from `conda-forge`, and only pure Python should be installed from PyPI. Please exercise strong caution when combining them, including

 1. being aware of the dependencies of the package you are about to install
 2. watching the install as it runs, to see whether it tells you what else it is installing

This applies even when the target package being installed is from local source rather than PyPI. The ideal output of a `pip` installation should say that it installed the package itself, but that all dependencies were already satisfied. If `pip` starts over-writing things, you will probably need to discard that conda environment and start again.

# Conclusion
In short, we recommend that you build working environments using the packages on `conda-forge`, including our own packages such as RIOS, PyShepSeg, TuiView, etc., and only use pip/PyPI to install small, pure Python packages, and only if they are not available via `conda-forge`. Of course, more sophisticated users have other options, such as building things directly from source, but we assume that such users are sophisticated enough to know what they are doing.
