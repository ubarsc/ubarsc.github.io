---
layout: post
title:  "Introducing a TuiView Plugin for linking RatZarr files"
date:   2026-09-17 10:00:00 +1000
categories: ubarsc tutorial TuiView RatZarr
---

# Introduction

In a [previous post](../../../../tuiview/2026/01/26/tuiview-plugins.html) we looked at the
existing TuiView plugins. There is now a new plugin that allows you
to link Raster Attribute Data in .zarr format created by the 
[RatZarr](https://github.com/ubarsc/ratzarr) package.

# Installation

See the [plugin installation instructions](../../../../tuiview/2026/01/26/tuiview-plugins.html)
for more detail. The recommended way of installing `tuiview-plugins` is from the [git repo](https://github.com/ubarsc/tuiview-plugins):

```bash
pip install git+https://github.com/ubarsc/tuiview-plugins.git
```

You will need to have TuiView installed in your current environment. You can 
then run `tuiviewpluginmgr` on the command line. By enabling "RatZarr Quiery Window plugin"
you will see what your `TUIVIEW_PLUGINS_PATH` environment variable needs to be
set to.

# Requirements

You must have an existing raster file with a Raster Attribute Table. Ideally
this file will have colour columns as TuiView only displays colours that
are part of a Raster Attribute Table within the file. This file needs to 
be loaded into TuiView.

Additionally you should have a .zarr file created by the [RatZarr](https://github.com/ubarsc/ratzarr) 
package. This .zarr file should have the same number of rows as the 
Raster Attribute Table in your raster file. 

# Workflow

Once the above requirements are met you should be ready to go. Once you
have the plugin loaded and a raster file with a Raster Attribute Table
in a viewer you can click on the Query Button (![Query Window](https://raw.githubusercontent.com/ubarsc/tuiview/refs/heads/master/resources/query.png)).
The Query Window is displayed as normal but there are 3 extra buttons:

* Link a RatZarr file (<img src="https://raw.githubusercontent.com/ubarsc/tuiview-plugins/refs/heads/master/tuiview_plugins/ratzarr_querywindow/zarr-pink-stacked.svg" alt="QML" width="32" height="32">)
* Unlink the RatZarr file (<img src="https://raw.githubusercontent.com/ubarsc/tuiview-plugins/refs/heads/master/tuiview_plugins/ratzarr_querywindow/zarr-pink-stacked-add.svg" alt="QML" width="32" height="32">)
* Add a Column to the currently linked RatZarr file (<img src="https://raw.githubusercontent.com/ubarsc/tuiview-plugins/refs/heads/master/tuiview_plugins/ratzarr_querywindow/zarr-pink-stacked-add.svg" alt="QML" width="32" height="32">)

Note that you may need to click the 2 arrows to see all the buttons on the toolbar
if your window is small.

When you attempt to link a RatZarr file you will be asked to provide the path:

![Link RatZarr]({{site.url}}/images/tuiview_ratzarrling.png)

Note this can be a `s3://` style path for a file on S3, although you will need
to have logged into AWS.

Once you have successfully linked, the extra RatZarr columns will appear
after the columns in the Raster Attribute Table.

![Query Window RatZarr]({{site.url}}/images/tuiview_ratzarrcols.png)

You can move the order of the columns

You can add a column to either the RAT or RatZarr

![Query Window RatZarr]({{site.url}}/images/tuiview_ratzarraddcol.png)

You can use the RatZarr columns in an expression

You can update a RatZarr column by going into edit mode and right clicking on the 
column header

You can set a RatZarr column to recieve keyboard edits

You can export a CSV 

You can use a RatZarr column as a column table lookup into a surrogate
colur table (link)

# Supported

