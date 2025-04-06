---
layout: post
title:  "EMU Format ready for testing"
date:   2025-04-07 08:00:00 +1000
categories: update
---

Announcing that [EMU format](https://github.com/ubarsc/emuformat) is
ready for Beta testing. Please report any issues to github. 
This is a streaming format that allows 
direct writing to AWS S3 Buckets. The intention is that when using
this format there will be no need to save data locally before
copying the file to S3 (as with GeoTiff and KEA).  
  
Note that this format is very limited and is no way a replacement
for KEA. It is only intended as an intermediate processing format for AWS.
More information can be found at the [EMU format repository](https://github.com/ubarsc/emuformat).
