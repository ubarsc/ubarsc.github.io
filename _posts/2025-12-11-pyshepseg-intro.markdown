---
layout: post
title:  "An introduction to using Pyshepseg"
date:   2025-12-11 10:00:00 +1000
categories: tutorial
---

# Introduction

[Pyshepseg](https://www.pyshepseg.org/en/latest/) is a tool for performing
segmentation of imagery. This tool is useful when you want to segment an 
image into areas that are similar spectrally for the purpose of mapping areas.

`pyshepseg` is a tool that needs a bit of work to understand before you can
start using it. This article should help you get running with the basic
functionality.

# Installation

`pyshepseg` can be installed via conda-forge or from source in [github](https://github.com/ubarsc/pyshepseg).
The examples below assume you have the KEA GDAL driver installed (`libgdal-kea` on conda forge).

# Segment a smallish image

The most simple case is loading an image into memory, segmenting it with
`pyshepseg` and saving it again. Since this requires all of the image being
read into memory you may want to select a small one (or only segment part
of it). Here is an example of using [pyshepseg.shepseg.doShepherdSegmentation](https://www.pyshepseg.org/en/latest/pyshepseg_shepseg.html#pyshepseg.shepseg.doShepherdSegmentation) to achieve this:

```python
from pyshepseg import shepseg
from osgeo import gdal

inds = gdal.Open('56JMQ.kea')
img = inds.ReadAsArray()

segResult = shepseg.doShepherdSegmentation(img)
ysize, xsize = segResult.segimg.shape

driver = gdal.GetDriverByName('KEA')
outds = driver.Create('out.kea', xsize, ysize, 1, gdal.GDT_UInt32)
band = outds.GetRasterBand(1)
band.WriteArray(segResult.segimg)
```

This script reads in all bands of `56JMQ.kea` into memory and uses them to do a segmentation and
writes back the result to `out.kea`. This uses the default parameters for the segmentation, see
the docstring of [pyshepseg.shepseg.doShepherdSegmentation](https://www.pyshepseg.org/en/latest/pyshepseg_shepseg.html#pyshepseg.shepseg.doShepherdSegmentation) for information about how to tweak the segmentation for your
situation.

`segResult` is an instance of [pyshepseg.shepseg.SegmentationResult](https://www.pyshepseg.org/en/latest/pyshepseg_shepseg.html#pyshepseg.shepseg.SegmentationResult) that contains information about the segmentation. Note that
you can save the kmeans object calculated for this segmentation and pass it into another
segmentation run.

# Segment a large image

What happens if you have an image that is larger than can be fitted into memory? That's 
where the [pyshepseg.tiling.doTiledShepherdSegmentation](https://www.pyshepseg.org/en/latest/pyshepseg_tiling.html#pyshepseg.tiling.doTiledShepherdSegmentation) function comes in. It is similar to `pyshepseg.shepseg.doShepherdSegmentation`
but handles splitting the image into tiles, processing them and stictching the result together.
Here is an example of processing the same image:

```python
from pyshepseg import tiling

segresult = tiling.doTiledShepherdSegmentation('56JMQ.kea', 'out.kea')
```

Again, see the docstring for [pyshepseg.tiling.doTiledShepherdSegmentation](https://www.pyshepseg.org/en/latest/pyshepseg_tiling.html#pyshepseg.tiling.doTiledShepherdSegmentation) for tweaking the parameters for your situation. Note that the overlap
must be sufficently large so that the segments on tile boundaries can be merged. 

`segresult` is an instance of [pyshepseg.tiling.TiledSegmentationResult](https://www.pyshepseg.org/en/latest/pyshepseg_tiling.html#pyshepseg.tiling.TiledSegmentationResult) which contains information about the tiled segmentation. 

Note that because of the overlap, doing a tiles segmentation is less efficient than an whole image
segmentation. However, it does allow you to segment very large images. For information about
running the tiled segmentation in parallel, please see [our previous blog post](../03/pyshepseg-fargate.html).

# Calculating statistics

`pyshepseg` also has support for calculating statistics from another image for each segment with the `tilingstats` module. This module processes the image in a tiled manner meaning that very large images
can be processed. There are two functions, one for [non-spatial statistics](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.calcPerSegmentStatsTiled) and another one for [spatial statistics](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.calcPerSegmentSpatialStatsTiled). Here is an example calculating the mean of the first band that we used for the segmentation for each of the segments:

```python
from pyshepseg import tilingstats

tilingstats.calcPerSegmentStatsTiled('56JMQ.kea', 1, 'out.kea', [('Band1_mean', 'mean')])
```

When you open `out.kea` you will see that there is a new raster attribute column `Band1_mean`
containing the means of `56JMQ.kea` band 1 for each segment. See the docstring of
[pyshepseg.tilingstats.calcPerSegmentStatsTiled](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.calcPerSegmentStatsTiled) for more information on the types of statistics
that can be calculated. Needless to say you can calculate statistics on files that weren't
used for the segmentation (soil maps, landuse etc) but they all must match on extent and pixel size.

Spatial statistics can be calculated in a similar manner, however instead of a statistic name you
must supply a callback written in Numba. There are some functions for common spatial statistics 
already in the `tilingstats` module:

1. [userFuncVariogram](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.userFuncVariogram) for calculating the variogram at a given distance.
2. [userFuncNumEdgePixels](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.userFuncNumEdgePixels) for calculating the length of the boundary of a segment.
3. [userFuncMeanCoord](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.userFuncMeanCoord) for calculating the mean coordinate of a segment. 

Here is an example of calculating the variogram at distance = 1 of each segment against the input data:

```python
from pyshepseg import tilingstats
from osgeo import gdal

tilingstats.calcPerSegmentSpatialStatsTiled('56JMQ', 1, 'out.kea', 
    [('Band1_var', gdal.GFT_Real)], 
    tilingstats.userFuncVariogram, 1)
```

This creates a new raster attribute table column `Band1_var` with the variogram value. Note how you specify
the types of the the columns to be created, and the callback fills in the values for these. See the docstring
for [](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.calcPerSegmentSpatialStatsTiled) for more information about the parameters.

# Conclusion

`pyshepseg` is a very powerful tool once you understand how to call it. It has the ability to process images
much larger than memory available, and also calculate statistics on the segments in an efficient manner.


