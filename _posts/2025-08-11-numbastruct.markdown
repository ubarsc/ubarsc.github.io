---
layout: post
title:  "Complex data structures with Numba"
date:   2025-08-07 10:00:00 +1000
categories: tutorial
---

# Introduction

Most Numba users are only familiar with the basic "speed up loops over
numpy arrays" functionality. While this is very useful, Numba does
have support for other data structures with their typed containers
and even allows you to create your own data structures with @jitclass.
This functionality gives Numba the flexibility and power of languages
like C but without the associated difficulty.

# Typed containers

Numba [typed list](https://numba.pydata.org/numba-doc/dev/reference/pysupported.html#typed-list)
and [typed dictionary](
https://numba.pydata.org/numba-doc/dev/reference/pysupported.html#typed-dict)
allows you to access this functionality from inside @jit'ed code. Note that
these are much much quicker than using normal Python lists and dictionaries. These
are implemented in compiled code and @jit'ed code accesses them directly rather
than going via the interpreter.

The main thing to note as these containers are typed. This means that the types
stored in them are set and they cannot contain a mix of types (un like Python containers).

From inside @jit-ed code you can create these containers much like you can in 
Python and the types will be inferred by Numba:

```
import numpy
from numba import njit
from numba.typed import List

@njit
def mylist_func():
    mylist = List()
    mylist.append(13)
    mylist.append(64)
    for el in mylist:
        print(el)

@njit
def my_dictionary_func():
    mydict = {10: numpy.random.randint(0, 100, (100,)),
        30: numpy.random.randint(0, 120, (90,))}
        
    for key, value in mydict.items():
        print(key, value.sum())
```

However you can also create these types ahead of time and pass them into Numba
(can also be inferred if you don't want to set the type explictly):

```
import numpy
from numba import njit
from numba.core import types
from numba.typed import List, Dict

@njit
def mylistfunc(l):
    tot = 0.0
    for el in l:
        tot += el
    print(tot)

l = List.empty_list(types.float64)
l.append(3.2)
l.append(9.4)
mylistfunc(l)

@njit
def mydictfunc(mydict):
    for key in mydict:
        print(key, mydict[key].sum())

d = Dict.empty(key_type=types.uint32, value_type=types.uint8[:])
d[types.uint32(3)] = numpy.random.randint(0, 100, (10,))
d[types.uint32(67)] = numpy.random.randint(0, 18, (78,))
mydictfunc(d)
```

You can explicitly create these containers in @jit-ed code also:

```
@njit
def mycreatedictfunc():
    d = Dict.empty(key_type=types.uint32, value_type=types.uint8[:])
    d[types.uint32(3)] = numpy.random.randint(0, 100, (100,)).astype(numpy.uint8)
    d[types.uint32(67)] = numpy.random.randint(0, 18, (78,)).astype(numpy.uint8)
    for key in d:
        print(key, d[key].sum())
    return d
```

For examples of using typed lists and typed dictionaries see the [shepseg](https://github.com/ubarsc/pyshepseg/blob/master/pyshepseg/shepseg.py) and 
[tilingstats](https://github.com/ubarsc/pyshepseg/blob/master/pyshepseg/tilingstats.py)
modules of [pyshepseg](https://github.com/ubarsc/pyshepseg).

# @jitclass

The above containers are very handy what if you need to create more complex data structures?
This is where @jitclass comes in. Basically it allows you to compile a class to called from 
@jit-ed code:

```

```
