---
layout: post
title:  "Numpy Structured Arrays"
date:   2025-11-11 10:00:00 +1000
categories: tutorial
---

# Introduction

[Numpy Structured arrays](https://numpy.org/doc/stable/user/basics.rec.html) are a more complex type
of array made up of smaller "structures". This is very similar to an array of `struct`s in the C language.

Previously, we had [introduced Numba's `@jitclass`](../../08/07/numbastruct.html) feature for grouping
together values of different types. However, for many uses (outside of building your own data structures)
structured arrays will suffice.

# Creation

You can create a numpy structured array by passing in a `dtype` containing a list of the names and 
types of the individual fields like this:

```python
import numpy
a = numpy.empty((10,), dtype=[('x', float), ('y', float), ('z', float), ('count', int)])
```

If you need to specify the exact precision, you can do this with the `numpy` types:

```python
a = numpy.empty((10,), dtype=[('x', numpy.float32), ('y', numpy.float32), 
    ('z', numpy.float64), ('count', numpy.uint8)])
```

You can also provide input data using `numpy.array`:
```python
a = numpy.array([(121.9, 97.1, 9.1, 5), (124.1, 98.0, 8.7, 4)], 
    dtype=[('x', float), ('y', float), ('z', float), ('count', int)])
```

# Access

You can access individual structures with the normal numpy indices, combined with the name
if individual fields. To set values, use this syntax:

```python
# set all the `x` values to 10 for all elements of the array
a['x'] = 10
# set all the fields of the first structure to 9
a[0] = 9
# set the 'x' field of the second structure to 100
a[1]['x'] = 100
```

The same rules apply for reading data out of the array:

```python
# all the 'x' fields in the array
a['x']
# the first structure in the array
a[0]
# the 'x' field of the second structure in the array
a[1]['x']
```

# Strings

Prior to numpy 2.0 you needed to define the length of strings in a structured array, and whether
they were unicode or not:

```python
a = numpy.empty((10,), dtype=[('asciistring', 'S8'), ('unicodestring', 'U5')])
```

Note that `asciistring` is limited to 8 characters and is accessed as a Python `bytes` object.
`unicodestring` is limited to 5 characters and is accessed as a normal string.

Since numpy 2.0, you can use the new `StringDType` which is more flexible - you don't have to
define length and can handle UTF-8 encoded strings:

```python
a = numpy.empty((10,), dtype=[('x', float), ('label', numpy.dtypes.StringDType)])
a['label'] = 'forest'
```

# Numba

Numba can also access structured arrays:

```python
from numba import njit

@njit
def iteratearray(a_struct):
    rows, = a_struct.shape
    totalcount = 0
    for i in range(rows):
        totalcount += a_struct[i]['count']
        
    return totalcount

a = numpy.array([(121.9, 97.1, 9.1, 5), (124.1, 98.0, 8.7, 4)], 
    dtype=[('x', float), ('y', float), ('z', float), ('count', int)])
    
print(iteratearray(a))
```

If you prefer, you can use the more C style "dot" notation from within numba:

```python
for i in range(rows):
   totalcount += a_struct[i].count
```

# Conclusion

Structured arrays are another handy numpy feature that can be combined with Numba to
create fast application specific code. Structured arrays are often using with 
LiDAR data - for example [Riegl Tools](https://gitlab.com/jrsrp/sys/lidar/riegl_tools)
returns structured numpy arrays of TLS data.
