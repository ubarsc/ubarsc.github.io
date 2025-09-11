---
layout: post
title:  "Gathering timing information for sections of your code with timinghooks"
date:   2025-09-12 10:00:00 +1000
categories: tutorial
---

# Introduction

When developing large complex Python projects it can be useful to work out
the proportion of time that is being spent in the various parts 
of your script. Using the [Python Profiler](https://docs.python.org/3/library/profile.html)
is one option (and probably the subject of a future post here)
but often you want a little bit more control over what is reported.

[timinghooks](https://github.com/ubarsc/timinghooks) allows you to:

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
with timings.interval('firstpart'):
    ...
    
with timings.interval('secondpart'):
    ...

summary = timings.makeSummaryDict()
print(summary)
```

A summary of the timings with some statistics on duration is printed:
```
{'firstpart': {'total': 1.4000797271728516, 'min': 1.4000797271728516, 'max': 1.4000797271728516, 'lowerq': 1.4000797271728516, 'median': 1.4000797271728516, 'upperq': 1.4000797271728516, 'mean': 1.4000797271728516, 'count': 1}, 'secondpart': {'total': 2.900083541870117, 'min': 2.900083541870117, 'max': 2.900083541870117, 'lowerq': 2.900083541870117, 'median': 2.900083541870117, 'upperq': 2.900083541870117, 'mean': 2.900083541870117, 'count': 1}}
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
with timings.interval('firstpart'):
    ...
    
with timings.interval('firstpart'):
    ...
```

# Conclusion

[timinghooks](https://github.com/ubarsc/timinghooks) is a useful tool
for tracking time spent on various parts of your code at a granularity
of your choice.

