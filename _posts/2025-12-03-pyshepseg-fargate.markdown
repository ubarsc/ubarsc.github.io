---
layout: post
title:  "Using Pyshepseg with AWS Fargate and threading"
date:   2025-12-03 10:00:00 +1000
categories: tutorial
---

# Introduction

As discussed in [a previous post](../../06/17/rios-ecs.html), RIOS has the ability to
spread processing across multiple VMS with AWS ECS. RIOS has the ability to use
ECS in either the Fargate or Private Cluster mode.
[pyshepseg](www.pyshepseg.org/en/latest/) also gained the ability to use AWS ECS in 
Fargate mode to spread the segmentation workload over multiple VMs in [version 2.0.4](../../../../update/2025/10/17/pyshepseg-2.0.4.html). 

Fargate is now the recommended approach to parallelising segmentation on AWS. The old AWS Batch
support is now being removed. When running on a single multi-core machine, the preferred approach is to use
`concurrencyType=CONC_THREADS`.

`pyshepseg` performs the stitching of the individual tiles in the background as they complete. This means
that it should be very efficient, but see "A note about performance" below.

# Pyshepseg with Fargate

Using `pyshepseg` with AWS Fargate is very similar to [RIOS](../../06/17/rios-ecs.html),
you will need a `taskRoleArn`, `executionRoleArn`, security group and subnet information
similar to that needed by RIOS.

```python
from pyshepseg import tiling

fargateCfg = tiling.FargateConfig(containerImage=MyECRImage,
    taskRoleArn=MyECSTaskRoleARN,
    executionRoleArn=MyECSTaskExecutionRoleARN,
    securityGroups=[MySecurityGroup],
    subnet=mysubnets[0],
    cpu='4 vCPU', memory='32GB', cpuArchitecture='ARM64')
concurrencyCfg = tiling.SegmentationConcurrencyConfig(
    concurrencyType=tiling.CONC_FARGATE,
    numWorkers=numworkers,
    maxConcurrentReads=maxreads,
    fargateCfg=fargateCfg)

tiledSegResult = tiling.doTiledShepherdSegmentation(in_file, out_file, 
    concurrencyCfg=concurrencyCfg)
```

See the docstring for [tiling.FargateConfig](https://www.pyshepseg.org/en/latest/pyshepseg_tiling.html#pyshepseg.tiling.FargateConfig)
for more information about these Fargate parameters. For the supported combinations of `cpu` and `memory`, refer to the
[AWS documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-cpu-memory-error.html).

For the `tiling.SegmentationConcurrencyConfig`, `numWorkers` controls how many parallel jobs are running 
and `maxreads` controls how many concurrent reads are happening - this can be limited if read errors are observed. See
the docstring for [tiling.SegmentationConcurrencyConfig](https://www.pyshepseg.org/en/latest/pyshepseg_tiling.html#pyshepseg.tiling.SegmentationConcurrencyConfig) for more detail.

# Pysghepseg with Threads

`pyshepseg` can also utilise the threading ability of a single computer with the CONC_THREADS concurrency type. In this
case, the `fargateCfg` is not passed and the `concurrencyType` is set to `tiling.CONC_THREADS` as shown below:

```python
from pyshepseg import tiling

concurrencyCfg = tiling.SegmentationConcurrencyConfig(
    concurrencyType=tiling.CONC_THREADS,
    numWorkers=numworkers)

tiledSegResult = tiling.doTiledShepherdSegmentation(in_file, out_file, 
    concurrencyCfg=concurrencyCfg)
```

Set the `numWorkers` to the number of threads you wish to use.

# A note about performance

It is important to note, when parallelising the segmentation, that it will not scale indefinitely with numWorkers. The
process of stitching together the segmented tiles is inherently sequential, and when the number of workers reaches the
level where they are running faster than the stitching, there is no further benefit to adding more workers. Doing so will
only increase the memory required to cache the completed tiles, with no decrease in total elapsed time. For this reason,
it is recommended to begin by testing (e.g. on a subset with a smaller number of tiles) with just a few workers
(something like 5), and increase until the stitchwaitfortile component no longer decreases significantly. The correct
number of workers will depend on the Fargate configuration chosen (notably the cpu/memory combination that controls the
hardware selection), or the specs of your machine (for threading) and also the tile size used, but numbers on the order
of 10 to 20 would be expected.

# Statistics

Pyshepseg does not yet allow statistics to be collected in parallel. However multiple read workers can be used 
by the underlying RIOS code for high latency filesystems like S3. See the docstring for [tilingstats.calcPerSegmentSpatialStatsRIOS](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.calcPerSegmentSpatialStatsRIOS).

# Conclusion

Performing a segmentation over a large area can be slow. However with the ability to parallelise the segmentation as
much as possible, pyshepseg can help you obtain results in a reasonable timeframe. However, there is a limit to
how much of a speedup can be acheived due to the limitations of the stitching process and gathering of statistics.


