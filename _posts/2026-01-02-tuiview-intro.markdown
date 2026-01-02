---
layout: post
title:  "Tiling with TuiView"
date:   2025-01-02 10:00:00 +1000
categories: tutorial
---

# Introduction

[TuiView](https://tuiview.org/) is a simple raster viewer written in Python. Although,
it is simpler than other GIS packages, it does have some features not commonly found 
elsewhere. These include: geolinking viewers, default stretch for files base on their
attributes and powerful raster attribute table (RAT) manipulation.

This article covers some of these basic features. TuiView can be installed via
conda-forge.

# Tiling

Start tuiview at the command line by typing `tuiview`. A single window then appears
which has buttons to open files and start other windows:

![TuiView Window]({{site.url}}/images/tuiview_window.png)

Alternatively you can start `tuiview` with images already loaded from the command line 
like this:

```bash
tuiview --separate a.tif b.tif c.tif
```

This will create 3 windows, each with 1 file loaded. Without the `--separate` flag, 
all 3 files will be loaded into the one viewer.
Normally this windows will open on top of one another. Arranging each viewer so all
can be seen is tedious so TuiView has built in functionality to do this, accessed
via the "File" menu by selecting "Tile Windows..." or pressing Ctrl+I:

![TuiView Tile Window Dialog]({{site.url}}/images/tuiview_tilew.png)

By default, TuiView will determine the numbers of viewers across and down that is
best for the number of viewers you have started - this can be overridden as desired.
Also, the windows on the current monitor are tiles by this method. If you have more
than one monitor, move all the windows you want to that monitor and select 
"Tile Windows..." on a viewer on that monitor.

TuiView choses the window to be tiled at each location by finding the window that
is closest already. If you have a particular order you want the viewers to be tiled
in then move them into a rough location and TuiView will snap them to a tiled 
location.

![TuiView Tiled Windows]({{site.url}}/images/tuiview_tiled.png)
