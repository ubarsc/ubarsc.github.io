---
layout: post
title:  "Using Pyshepseg with AWS Fargate"
date:   2025-12-03 10:00:00 +1000
categories: tutorial
---

# Introduction

As discussed in [a previous post](../../06/17/rios-ecs.html), RIOS has the ability to
spread processing across multiple VMS with AWS ECS. RIOS has the ability to use
ECS in either the Fargate or Private Cluster mode.
[pyshepseg](www.pyshepseg.org/en/latest/) also gained the ability to use AWS ECS in 
Fargate mode to spread the segmentation workload over multiple VMs in [version 2.0.4](../../../../update/2025/10/17/pyshepseg-2.0.4.html).

Fargate is now our recommended approach to parallelising segmentation. The old AWS Batch
support is now being removed.

# Pyshepseg with Fargate

Using pyshepseg with AWS Fargate is very similar to [RIOS](../../06/17/rios-ecs.html),
you will need a `taskRoleArn`, `executionRoleArn`, security group and subnet information
similar to that needed by RIOS.

```python
from pyshepseg import tiling

fargateCfg = tiling.FargateConfig(containerImage=MyECRImage,
    taskRoleArn=MyECSTaskRoleARN,
    executionRoleArn=MyECSTaskExecutionRoleARN,
    securityGroups=[MySecurityGroup],
    subnet=mysubnets[0],
    cpu='8 vCPU', memory='48GB', cpuArchitecture='ARM64')
concurrencyCfg = tiling.SegmentationConcurrencyConfig(
    concurrencyType=tiling.CONC_FARGATE,
    numWorkers=numworkers,
    maxConcurrentReads=maxreads,
    fargateCfg=fargateCfg)

tiledSegResult = tiling.doTiledShepherdSegmentation(in_file, out_file, 
    concurrencyCfg=concurrencyCfg)
```

See the docstring for [tiling.FargateConfig](https://www.pyshepseg.org/en/latest/pyshepseg_tiling.html#pyshepseg.tiling.FargateConfig)
for more information about these parameters. The `numWorkers` controls how many parallel jobs are running 
and `maxreads` controls how many concurrent reads are happening - can be limited if read errors are observed. See
the docstring for [tiling.SegmentationConcurrencyConfig](https://www.pyshepseg.org/en/latest/pyshepseg_tiling.html#pyshepseg.tiling.SegmentationConcurrencyConfig).

# Statistics

Pyshepseg does not yet allow statistics to be collected in parallel. However multiple read workers can be used 
by the underlying RIOS code for high latency filesystems like S3. See the docstring for [tilingstats.calcPerSegmentSpatialStatsRIOS](https://www.pyshepseg.org/en/latest/pyshepseg_tilingstats.html#pyshepseg.tilingstats.calcPerSegmentSpatialStatsRIOS).

# Conclusion

Performing a segmentation over a large area can be slow. However with the ability to parallelise the segmentation as
much as possible, pyshepseg can help you obtain results in a reasonable timeframe.
