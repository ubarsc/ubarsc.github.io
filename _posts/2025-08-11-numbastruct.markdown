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

Numba's [typed list](https://numba.readthedocs.io/en/stable/reference/pysupported.html#typed-list)
and [typed dictionary](
https://numba.readthedocs.io/en/stable/reference/pysupported.html#typed-dict)
allows you to access this functionality from inside @jit'ed code. Note that
these are much much quicker than using normal Python lists and dictionaries. These
are implemented in compiled code and @jit'ed code accesses them directly rather
than going via the interpreter.

The main thing to note is that these containers are typed. This means that the types
stored in them are set and they cannot contain a mix of types (unlike Python containers).

From inside @jit-ed code you can create these containers much like you can in 
Python and the types will be inferred by Numba:

```python
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

```python
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

```python
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

## More advanced use

It is also possible to create lists of dictionaries or dictionaries of lists:

```python
list_of_dict = List.empty_list(types.DictType(types.uint32, types.float64))
d1 = Dict.empty(key_type=types.uint32, value_type=types.float64)
d1[19] = 6.7
list_of_dict.append(d1)
testfn(list_of_dict)

dict_of_list =  Dict.empty(key_type=types.uint32, 
    value_type=types.ListType(types.float64))
l1 = List.empty_list(types.float64)
l1.append(8.9)
l1.append(10.3)
dict_of_list[4] = l1
```

If you don't know the types ahead of time you can use `typeof` to determine this at runtime.
For example, if you had an input array `myarray` that you don't know what the type is until 
it is read from file, you can do something like this to create a dictionary of this type of array:

```python
from numba import typeof
dict_of_array = Dict.empty(key_type=types.uint32, value_type=typeof(myarray))
```

You can also get the Numba type of a single element of an array if you want to store one value
rather than the whole thing:
```python
dict_of_scalar = Dict.empty(key_type=types.uint32, value_type=typeof(myarray[0]))
```

# @jitclass

The above containers are very handy, but what if you need to create more complex data structures?
This is where [@jitclass](https://numba.readthedocs.io/en/stable/user/jitclass.html) comes in. 
Basically it allows you to compile a class to called from @jit-ed code. To help Numba you need
to specify the types of each of the attributes and these are now fixed (like the typed containers):

```python
from numba.experimental import jitclass

spec = [('count', types.uint32), 
    ('sum', types.uint64), 
    ('best_array', types.uint8[:])]
@jitclass(spec)
class MyTestObject:
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.best_array = numpy.zeros((100,), dtype=numpy.uint8)
        
    def accumulate(self, arr):
        self.count += 1
        self.sum += arr.sum()
        self.best_array = arr

@njit
def testcreateobj():
    obj = MyTestObject()
    arr = numpy.ones((90,), dtype=numpy.uint8)
    obj.accumulate(arr)
```

The whole `MyTestObject` object is now compiled code. Note that you can use `types.optional` to
flag that a field can be None:

```python
spec = [('count', types.uint32), 
    ('sum', types.uint64), 
    ('best_array', types.optional(types.uint8[:]))]
@jitclass(spec)
class MyTestObject:
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.best_array = None
```

You can also have lists or dictionaries as attributes of your class:
```python
spec = [('count', types.uint32), 
    ('sum', types.uint64), 
    ('mylist', types.ListType(types.uint8[:]))]
@jitclass(spec)
class MyTestObject:
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.mylist = List.empty_list(types.uint8[:])
        
    def accumulate(self, arr):
        self.count += 1
        self.sum += arr.sum()
        self.mylist.append(arr)
```

Also, you can embed one object within another (note slightly clunky syntax for getting the type of a @jitclass):

```python
spec1 = [('count', types.uint32)]
@jitclass(spec1)
class MyTestObject1:
    def __init__(self):
        self.count = 0

spec2 = [('count', types.uint32), 
    ('sum', types.uint64), 
    ('first', types.optional(MyTestObject1.class_type.instance_type))]
@jitclass(spec2)
class MyTestObject2:
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.first = None
        
    def accumulate(self, o1):
        self.count += 1
        self.first = o1

```

Of course you can embed an object of the same type within an object using `deferred_type`:
```python
from numba import deferred_type

spec = [('count', types.uint32), 
    ('sum', types.uint64), 
    ('first', types.optional(node_type))]
@jitclass(spec)
class MyTestObject:
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.first = None
        
    def accumulate(self, o1):
        self.count += 1
        self.first = o1

# Note: this must happen before you use the class        
node_type.define(MyTestObject.class_type.instance_type)
```

This is probably quite familiar to anyone who has used structures in C. See [pyshepseg](https://github.com/ubarsc/pyshepseg/) or
[RATTree](https://github.com/gillins/rattree) for more examples of doing this.

## Customising attributes 

But - what about when you don't know one or more field types ahead of time? Well, `jitclass`
can be called as a function with the types at runtime. Note that this returns a type
which can then passed into a Numba function and instantiated.

```python
myarray = ...

class MyTestObjectDynamic:
    def __init__(self):
        self.last_array = None
        
cls = jitclass([('last_array', typeof(myarray))])

@njit
def testcreateobjdyn(clsdefn):
    obj = clsdefn()
```

# Conclusion

Complex data structures are indeed possible in Numba. This again shrinks the potential areas that require
compiled languages. There is definitely a steep learning curve involved, but the potential upsides 
are not insignificant:

1. No messing with compilers and managing libraries
2. No memory management (everything is reference counted)
3. Being able to specialise code at runtime which is not only simpler, it does allow the code to be more
optimised.
