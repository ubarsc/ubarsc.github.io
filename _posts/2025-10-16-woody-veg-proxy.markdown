# Using RIOS and Moamosaic to create a proxy woody-vegetation density layer for Australia

By [Tony Gill](https://www.linkedin.com/in/tony-gill-23115927a/)
and [Cibolabs](https://www.cibolabs.com.au)

3-5 minute read.

Australia's natural environment contains grasslands, woodlands and open
and closed forests. In most places, the grass-layer senesces during
dry periods. The remaining greeness is from the foliage of the evergreen
woody vegetation layers.
A proxy for woody vegetation density can be created by finding this
minimum-green baseline using a satellite-image time series of NDVI.

![minimum NDVI baseline]({{site.url}}/images/ndvi_time_series.png)

[NDVI is a measure of vegetation greeness](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index).
It is calculated from the red and near-infrared image bands.
Over a four-year period, we calculated the NDVI for every cloud-free pixel for
every Sentinel-2 satellite image over Australia.
For each pixel time series, we calculated the 5th percentile of NDVI as our
proxy for woody vegetation density.

The processing workflow is:
- calculate the 5th percentile of NDVI for each tile using RIOS
- stitch the tiles together using Moamosaic

![woody vegetation density proxy]({{site.url}}/images/ndvi_percentile_map_3.png)

We used over a million input layers.
Images from 973 Sentinel-2 tiles are required to cover Australia.
There's notionally an image every 5 days per tile for four years. And we read from
three layers with 10 m pixel sizes: red, near infrared, and a mask layer
(to remove cloud-affected pixels from the analysis).

The input images were Sentinel-2 surface reflectance L2A products.
These are stored as cloud-optimised geotiffs on
[AWS S3 in the us-west-2 region](https://registry.opendata.aws/sentinel-2-l2a-cogs/).
For each tile we read over 900 input layers from S3.

Processing averaged 1 hour and 15 minutes per tile.
We found [RIOS's concurrency feature](https://www.rioshome.org/en/latest/concurrency.html)
to be an effective optimiser. Without it, reading the data sequentially from
an S3 bucket was slow due to high latencies (compared to reading data from local disk).
Through [trial and error with timings](https://www.rioshome.org/en/latest/concurrency.html#timing),
we settled on eight RIOS read workers for parallel reading of blocks of image data,
passing them to two RIOS compute workers for processing.

Moamosaic stitched the 973 single-band tile images together in 5 hours and 30 minutes.
We used Moamosaic's multi-threaded read feature to read the processed
tiles from S3. We found Moamosaic's default of four read workers to
perform best, which is in line with Neil's
[performance analysis](https://ubarsc.github.io/moamosaic/performance.html).

We estimated our processing cost at 350USD.
We used AWS Batch with EC2 instance types (and their Spot pricing at the time) of:
- c6g.8xlarge ($0.4212 / hr)
- c7g.4xlarge ($0.2225 / hr)
- c7g.8xlarge ($0.4484 / hr)

Each job was allocated 14 GB of RAM. This seems quite high. However, we found
it necessary for those tiles that intersected at least three satellite paths,
resulting in large numbers of input files.
