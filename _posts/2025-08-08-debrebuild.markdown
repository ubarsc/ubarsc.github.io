---
layout: post
title:  "Rebuilding Debian/Ubuntu's GDAL package"
date:   2025-08-07 10:00:00 +1000
categories: tutorial
---

# Introduction

Debian and Ubuntu are a great base for creating containers for raster processing
as they have GDAL already packaged and can be easily installed. The alternative
to using these packages is to have to build the GDAL from source which 
is painful. The Debian package is reasonably complete with useful drivers and
reproducing this would be a lot of work.

However, sometimes you might need to make a small tweak to GDAL to fix a bug
or to test some feature. It would be nice if you could just rebuild the GDAL
package, but with your changes. Turns out you can, although some of the steps
required are not obvious.

# Preparing the patch

The first step is to create a patch which can then be applied to the GDAL sources
before compilation. Turns out that Debian (and Ubuntu) use a special tool called `quilt`
instead of the more standard `diff` tool. Debian keeps the source code for all their
packages for each release so instead of having to work out where the source code is
for your release, it can be found quite easily. Obtain the source for GDAL like this:

```bash
# Install prereqs
sudo apt-get install -y devscripts equivs quilt
# backup
sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources~
# Enable source packages
sudo sed -Ei 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/ubuntu.sources
# refresh cache
sudo apt-get update
# install the source for gdal
apt-get source gdal
# cd into the source
gdal-3.10.2+dfsg 
```

Next, create a quilt patch based on the commands (see [the Debian wiki on quilt](https://wiki.debian.org/UsingQuilt)):

```bash
# Create a new patch
quilt new mypatch.patch
# add any source files you wish to patch
quilt add port/cpl_http.cpp
# now edit and make changes to the source files
# get quilt to create a patch with these changes
quilt refresh
# get quilt to create a basic header for your patch
# - just author and description are needed.
quilt header -e --dep3
# tell quilt you have finished the patch
quilt pop -a 
# now save patches/mypatch.patch somewhere
```

# Create your own GDAL packages

To actually rebuild GDAL with this patch run something like the following 
(based on [these instructions](https://www.linuxjournal.com/content/rebuilding-and-modifying-debian-packages)):

```bash
# (assume the same prereqs are installed)
# copy the new patch into the source tree
cp mypatch.patch debian/patches
# Add your patch to the list of patches to be applied
echo mypatch.patch >> debian/patches/series
# apply all the patches with quilt
QUILT_PATCHES="debian/patches" quilt push -a
# Start a rebuild with a log comment
dch --rebuild "rebuild with mypatch"
# Create the metadata packages for the build prereqs
mk-build-deps
# install the build prereqs
sudo apt-get install -y ./gdal-build-deps*.deb
# rebuild
debuild -us -uc -b
# install the new packages
sudo apt-get install -y ./libgdal36_*.deb ./gdal-data_*.deb ./gdal-plugins_*.deb ./libgdal-dev_*.deb
# remove the build dependencies
sudo apt-get purge -y --auto-remove gdal-build-deps
```

Obviously, the above is more than suitable for building a container but for other uses
you may need to copy the created *.deb files somewhere that others can access.

# Conclusion

The above recipe makes it possible to rebuild the Debina/Ubuntu GDAL package with custom patches for your
own use. Please submit any useful features or fixes upstream to the [GDAL repository](github.com/OSGeo/gdal/).
