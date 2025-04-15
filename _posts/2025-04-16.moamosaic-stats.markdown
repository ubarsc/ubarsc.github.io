---
layout: post
title:  "New release of Moamosaic (1.0.1)"
date:   2025-04-16 07:35:00 +1000
categories: update
---

[Version 1.0.1](https://github.com/ubarsc/moamosaic/releases/tag/moamosaic-1.0.1)
release of Moamosaic, a multi-threaded GDAL mosaicing tool.

This version handles the pyramid layers and basic stats of the output file
block-by-block, avoiding the need for extra passes through the data when
the file is closed.
