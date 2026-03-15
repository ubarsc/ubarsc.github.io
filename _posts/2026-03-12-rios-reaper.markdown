---
layout: post
title:  "Introducing the RIOS Reaper for terminating unused AWS resources"
date:   2026-03-12 10:00:00 +1000
categories: tutorial
---

# Introduction

[RIOS](https://www.rioshome.org) and [PyShepSeg](https://www.pyshepseg.org)
have support for Concurrency using AWS. RIOS [supports ECS and Fargate clusters](https://www.rioshome.org/en/latest/concurrency.html) and PyShepSeg currently
only [supports Fargate clusters](https://www.pyshepseg.org/en/latest/#concurrency).
These packages attempt to clean up any resources they create. However 
there may be situations, such as termination of the main script or software
error, where these resources are not terminated.
[RIOS Reaper](https://github.com/gillins/rios_reaper) is a tool that monitors resources created by RIOS and PyShepSeg
and notifies a user via email about anything that looks like it should
be terminated. It does this by looking for resource tags that RIOS and PyShepSeg
add as they are creating resources. It then checks EC2 instances for idle CPU 
and ECS and Fargate clusters that are stopped.
Currently, RIOS Reaper does not terminate any EC2 instances
or Fargate clusters. We feel it is safer for a user to delete these in case
they are still in use. 

# Installation

[RIOS Reaper](https://github.com/gillins/rios_reaper) is a Lambda that runs once a day. 
It is based on [AWS SAM](https://aws.amazon.com/serverless/sam/) and this needs to be installed
first. Any machine that is connected to the internet and logged into AWS should be
suitable for running the deployment, however we have only tested on Linux.
Further instructions are in the [README](https://github.com/gillins/rios_reaper/blob/main/README.md). Note 
will need to be logged onto your AWS account on the command line with sufficient parameters to install
a Lambda.

Since this job runs on a Lambda at a nominated time there is no extra machine to
be provisioned and you'll only be paying for when the Lambda is running. AWS takes
care of running Lambda code, you just need to provide the function.

Information about your account and VPC is required. This is passed in via environment variables:
- AWS_PROFILE - the name of the profile you are running under, or `default`
- VPC_ID - the id of the VPC you want the Lambda to run under
- SUBNET_IDS - a comma separated list of subnet ids the Lambda is to run within
- EMAIL - the email address you want notifications to be sent to 

You may also want to make changes to `template.yaml` which is the CloudFormation
template used by AWS SAM. Check that the `Architecture` parameter is correct
for your configuration (also in `samconfig.toml`) and that the `Schedule` setting is correct for when you
want the check to be run. The region can be set in `samconfig.toml`.

Once this information is set, you can test running the Lambda locally:

```bash
./test-deploy.py
```

Once you are happy, deploy the Lambda like this:

```bash
./test-deploy -m deployed
```

To remove the Lambda:

```bash
sam delete
```

# Conclusion

RIOS Reaper is a relatively easy way to check that there are no "zombie" jobs
running that are costing you money. You will get an email once a day containing
details of instances and clusters that may need to be checked and terminated.

