---
layout: post
title:  "Gathering timing information for sections of your code with timinghooks"
date:   2025-09-12 8:00:00 +1000
categories: tutorial
---

# Introduction

When developing large complex Python projects it can be useful to work out
the proportion of time that is being spent in the various parts 
of your script. Using the [Python Profiler](https://docs.python.org/3/library/profile.html)
is one option for the developer to understand how time is spent in their 
software (and probably the subject of a future post here).

However, another important use case is to make logical timing information
available to the end user of the software. This arises where there are choices
the user could be making which affect the performance of the software, and
knowing how the software spends time can allow the user to make more informed
choices.

The [timinghooks](https://github.com/ubarsc/timinghooks) module is designed
to allow the developer to embed timing hooks into logical places in the code, 
so that the resulting timing information can then be reported to the user by
the software itself.

A very simple example would be timings on whether a piece of software is spending
more time reading its input data or performing calculations on that data. The
developer can put timing hooks around those two operations, and report the
totals to the user, allowing the user to make informed choices about whether or
not to move the data to a faster disk drive.

1. Just report time taken in part of a function 
2. Report time taken for a whole group of statements
3. Collate similar steps into one timing

# Installation

`timinghooks` can be installed from the github repo like this:

```bash
git clone https://github.com/ubarsc/timinghooks.git
cd timinghooks
pip install .
```

However, given that this is intended to ship with production software, the
developer may prefer to include the timinghooks module in with their code, 
eliminating an external dependency.

# Usage

The first step is to create a "timings" object. It is usual just to 
have one of these per script:

```python
from timinghooks import Timers
...
timings = Timers()
```

The next step is to use the `timings` as a context manager using a string
to record what you are timing. This string will be shown in the report made
by `timings.makeSummaryDict()`:

```python
with timings.interval('reading'):
    # Statements to read input data
    
with timings.interval('calculating'):
    # Statements to perform calculations

summary = timings.makeSummaryDict()
print(summary)
```

A summary of the timings with some statistics on duration is printed:
```
{'reading': {'total': 1.4000797271728516, 'min': 1.4000797271728516, 'max': 1.4000797271728516, 'lowerq': 1.4000797271728516, 'median': 1.4000797271728516, 'upperq': 1.4000797271728516, 'mean': 1.4000797271728516, 'count': 1}, 'calculating': {'total': 2.900083541870117, 'min': 2.900083541870117, 'max': 2.900083541870117, 'lowerq': 2.900083541870117, 'median': 2.900083541870117, 'upperq': 2.900083541870117, 'mean': 2.900083541870117, 'count': 1}}
```
All timing values are in seconds.

Each named timer is given a set of summary statistics. In general, the most
useful one is the `'total'`, which simply adds up all the time spent in the
block of code for that named timer. The other statistics can provide more
information about the distribution of those individual timings. The `'count'`
field is a count of how many times the code block was executed.

So, a simpler output might be something like:

```python
for t in summary:
    print(t, summary[t]['total'])
```
which would just look something like
```
reading 1.4000797271728516
calculating 2.900083541870117
```

Code can be nested:
```python
with timings.interval('all'):
    for i in range(count):
        with timings.interval('inner')
            ...
```

Also, the same string can be used more than once if separate parts of the 
code need to be timed together.

```python
with timings.interval('calculating'):
    ...
    
with timings.interval('calculating'):
    ...
```

The timers object, and the individual named timers, are also thread-safe, 
so can be accumulated across different threads within the same process.

# Conclusion

[timinghooks](https://github.com/ubarsc/timinghooks) is a useful tool
for tracking time spent on various parts of your code at a granularity
of your choice, making it easy to embed such timings into production code
and report results to end users.

