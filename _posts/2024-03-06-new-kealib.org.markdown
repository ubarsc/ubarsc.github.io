---
layout: post
title:  "New kealib.org website with improved documentation"
date:   2024-03-06 11:00:00 +1000
categories: update
---

New [kealib.org](https://kealib.org) website launched. This now includes
[Doxygen generated documentation of the C++ headers](https://kealib.org/cpp/html/index.html) and
the [Python documentation](https://kealib.org/python/kealib.html).

The Python bindings haven't been widely advertised until now, but they are ready 
for use. They allow access to KEA specific functionality that can't be accessed via GDAL
like the 'neighbours' for segments. This is mainly contained in the [extrat module](https://kealib.org/python/kealib/extrat.html). Note that these functions take
a GDAL 'dataset' object as the first parameter so you must open the file with GDAL first.

There is also a module for [building neighbours](https://kealib.org/python/kealib/build_neighbours.html)
and a command line program to do this (kea_build_neighbours).



