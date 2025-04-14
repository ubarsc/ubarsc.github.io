---
layout: post
title:  "New Python package to store processing history on GDAL raster files"
date:   2025-04-14 14:15:00 +1000
categories: new
---

A new Python package, [processinghistory](https://github.com/ubarsc/processinghistory),
has been released.

This package attaches small text metadata to a GDAL raster file, using GDAL's
arbitrary metadata API. The metadata is in the form of a dictionary of entries
for things like the script which created it, a short description of what it is,
and so on. In addition to that dictionary, there is also a copy of the history
metadata for all the parent GDAL files that were inputs to creating the current
file, so that the entire lineage is saved with the current file. This means the
detail of its creation can be traced, even without access to the parent files.
