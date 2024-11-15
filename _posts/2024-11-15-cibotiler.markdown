---
layout: post
title:  "Cibo Tiler Released"
date:   2024-11-15 10:00:00 +1000
categories: new
---

A new open source project that serves raster files as web tiles has been
released at [https://github.com/cibolabs/cibo_tilerlayer](https://github.com/cibolabs/cibo_tilerlayer). The documentation
is at [https://cibotilerlayer.readthedocs.io/en/latest/](https://cibotilerlayer.readthedocs.io/en/latest/).

It is based on a subset of TuiView code and attempts to be a much
simpler alternative to titiler. It is intended that users will deploy
this project to serve their data to web mapping sites, such as those 
built with Leaflet or MapBox. The technology used for serving is not
restricted by cibo tiler (unlike titiler) - should work with anything that uses Python
(AWS Lambda, FastAPI, Flask etc). It can also be used from stand alone Python applications.
