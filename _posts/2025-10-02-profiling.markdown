---
layout: post
title:  "Profiling script with cProfile, SnakeVis and profila"
date:   2025-10-02 8:00:00 +1000
categories: tutorial
---

# Introduction

Understanding where your script spends the bulk of the time is essential
for any attempt to optimise it. Otherwise you may spend a lot of time
trying to speed up sections that take almost no time at all. The risk
is that the code can become more complex and harder to understand and
at the same time not giving you any improvement in speed.

It is much more sensible to identify the parts of your script that are 
really slow and spend effort optimising them.

This article discusses ways to temporarily gather profile information during
development. Refer to [our previous post on timinghooks](../../09/16/timinghooks.html)
for a permanent way to embed timing information into your script.

# cProfile

[cProfile](https://docs.python.org/3/library/profile.html) is a Python
module that comes with Python itself. It allows you to collect statistics
from a run of your script that you can study later. To run from the command
line using the `-m` switch to load `cProfile` before running your script and
specify an output file to put the profile information into:

```bash
python -m cProfile -o profile.dat myscript.py
```

Any command line parameters for your script can go at the end of the command line.

# Interpreting a profile with pstats

Python also has a built in module for interpreting the result of `cProfile`: [pstats](https://docs.python.org/3/library/profile.html#module-pstats).

This module can be used to load in the `profile.dat` file created above and
sort the results by various metrics (with the `sort_stats()` function) and
a summary printed (by the `print_stats()` function).

# Interactively exploring a profile with SnakeVis

[SnakeVis](https://jiffyclub.github.io/snakeviz/) is a graphical utility that
allows visualisation and sorting of the profile results interactively.

It can be installed from conda forge and opens a browser that shows the
results. For example:

```bash
snakeviz profile.dat
```

This will open a page that will let you select between two graphical views that
can help you understand where your script is spending most of its time. Of most
use is the table down the bottom. Here you can sort your functions by the number
of calls that are made, the total amount of time spent in each call and the 
average time of each call. Using this you can narrow down which functions are the
best candidates for optimisation. Start by looking at functions that are high in 
both total and per call time. Optmising a function with a high per call time is 
likely not useful if it isn't called many times. On the other hand if it is called
many times but the per call time is very low there might not be much time to be 
shaved off. Interpreting these results is a bit of an art but with a bit of 
practise and familiarity with your code large improvements can be made.

It may be worthwhile to split up some larger functions into smaller ones so 
problem areas can be narrowed down.

# Optimising Numba code

An obvious avenue of optmisation is to replace parts of your script that does a lot
of looping with Numba functions. This is often an easy win, but when you want to 
squeeze even more performance out, it turns out that optimising Numba code is harder. 
`cProfile` just shows your Numba function as
a single entry. It is hard to get visibility on which part of your Numba function 
(or which functions if you have multiple Numba functions that call each other) is slow. 

Fortunately, [profila](https://github.com/pythonspeed/profila) allows you to peer inside
your Numba code and identify bottlenecks. `profila` must be installed via `pip` with
a setup step used to download a patched version of `gdb`:

```bash
pip install profila
python -m profila setup
```

Then you can start profiling Numba code:

```bash
python -m profila annotate -- myscript.py
```

Note that because `profila` takes samples of what is being executed your script needs to
spend a reasonable proportion of its time running Numba code. You can fake this my running
your Numba code within a Python loop (say 1000 times) to exaggerate the runtime of Numba
code. `profila` prints a listing of your Numba code with a percentage spent on each line.
Note that some of your listing will show some internal Numba code if you are using Numba
optimised numpy functions or Numba containers so some care is needed in interpreting
the result.

# Conclusion

Profiling is an important step in developing complex scientific software. Python does
come with a very good tool for helping you understand how your script runs, however
patience and care is required to get a good speed up.
