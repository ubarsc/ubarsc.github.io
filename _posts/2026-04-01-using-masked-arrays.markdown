---
layout: post
title:  "Using numpy masked arrays"
date:   2026-04-01 10:00:00 +1000
categories: tutorial
---

# Introduction

Dealing with numpy arrays that have missing data is a challenge. When 
calculating statistics on them or otherwise processing data in them 
you need to skip elements that are missing - often they are some 
very high (or low) nodata value and will skew the result. 

# Using NaNs

In floating point data, there is a special number: NaN ("not a number")
that you can use to signify that this value can't be processed for whatever reason.
Numpy has a collection of functions (they all start with "nan") that ignore
any NaNs in your data. You an also test for individual elements being NaN
with `numpy.isnan`.
However, what happens if you are dealing with integer data? Well, setting
integer elements to NaN fails. The alternative is to convert the whole
integer array you are dealing with to float and back again. This adds
time and memory use. Also performing operations on floats is slower
than on integers. 

# Numpy Masked Arrays

There is an alternative - [numpy masked arrays](https://numpy.org/doc/stable/reference/maskedarray.html). These
are arrays that also store a mask of where data is not valid:

```python
>>> import numpy
>>> x = numpy.array([[1, 5, 9999], [-980, 7, 9], [11, 61, 9923]])
>>> mx = numpy.ma.masked_array(x, mask=[[False, False, True], [True, False, False], [False, False, True]])
>>> mx
masked_array(
  data=[[1, 5, --],
        [--, 7, 9],
        [11, 61, --]],
  mask=[[False, False,  True],
        [ True, False, False],
        [False, False,  True]],
  fill_value=999999)
```

It is important to note the `mask` parameter is `True` where the data *is masked*.
Masked arrays support [many of the numpy methods](https://numpy.org/doc/stable/reference/maskedarray.baseclass.html#maskedarray-methods):

```python
>>> mx.max()
np.int64(61)
```

Note how the masked out values aren't used in the calculations. You can also turn 
a masked array back into a normal array using the `filled` method:

```python
>>> mx.filled(-99)
array([[  1,   5, -99],
       [-99,   7,   9],
       [ 11,  61, -99]])
```

If your data has a single value that represents "no data" then you can pass this in
to the `masked_values` function to create a masked array where that value is masked:

```python
x = numpy.array([1, -99, 23, 78, -99])
>>> mx = numpy.ma.masked_values(x, -99)
>>> mx
masked_array(data=[1, --, 23, 78, --],
             mask=[False,  True, False, False,  True],
       fill_value=-99)
```

# Notes on using Numba with masked arrays

Numba doesn't know anything about masked arrays - you get an `Unsupported array type: numpy.ma.MaskedArray` error when you pass one in to a Numba function. However, 
a masked array is made up of two normal arrays: the data and the mask. You can 
pass these in separately to a Numba function:

```python
@njit
def docalc(data, mask):
    tot = 0
    for x in range(data.shape[0]):
        if not mask[x]:
            tot += data[x]
    return tot
    
x = numpy.array([1, -99, 23, 78, -99])
mx = numpy.ma.masked_values(x, -99)
result = docalc(mx.data, mx.mask)
``` 

However, if your data just has a single "no data" value it may
be easier just to pass this value in and compare each element to it
instead of using masked arrays.

# Conclusion

Numba masked arrays can be a useful tool when dealing with missing
data. They provide a lighter weight alternative to conversion to float
arrays and setting NaN.

