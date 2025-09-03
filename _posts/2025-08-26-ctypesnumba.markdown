---
layout: post
title:  "Calling C from inside Numba"
date:   2025-08-27 8:00:00 +1000
categories: tutorial
---

# Introduction

Following on from our previous post about [Complex data structures with Numba](../07/numbastruct.html)
we cover another lesser known feature of Numba - the ability to call C directly.

# ctypes

Python has always had the ability to invoke C using the [`ctypes` module](https://docs.python.org/3/library/ctypes.html).
This is a very handy feature when you need to access functionality not normally available in Python.
However, the main limitation is speed when you need to invoke a function from within a loop.

# Numba and ctypes

Numba can actually call [`ctypes` defined functions directly](https://numba.readthedocs.io/en/stable/user/cfunc.html#calling-c-code-from-numba). Instead of using `ctypes`
to invoke a function it is able to insert the appropriate machine instructions directly into the code giving
us the same speed as invoking from C. 

# Simple example

Below is a simple example (for Linux) of loading the C runtime library and invoking the `sleep` function
from inside Numba.

```python
import ctypes
from numba import njit

LIBC = ctypes.CDLL('libc.so.6')
LIBC_SLEEP = LIBC.sleep
LIBC_SLEEP.argtypes = [ctypes.c_uint]
LIBC_SLEEP.restype = ctypes.c_uint

@njit
def testsleep():
    for x in range(0, 90):
        print(x)
        LIBC_SLEEP(1)

testsleep()
```

This perhaps is not the most useful example ever but does give you a flavour of how it works. Note
that you need to know the argument types and result type and this must match the C definition of the
function or undefined behaviour will result.

# Locking concurrency 

A more useful example is locking access to a shared array from multiple threads:

```python
import ctypes
import threading
import numpy
from numba import njit

PYLIB = ctypes.CDLL('libpython3.so')

LOCK_CREATE = PYLIB.PyThread_allocate_lock
LOCK_CREATE.restype = ctypes.c_void_p
LOCK_CREATE.argtypes = []

LOCK_DESTROY = PYLIB.PyThread_free_lock
LOCK_DESTROY.argtypes = [ctypes.c_void_p]

LOCK_ACQUIRE = PYLIB.PyThread_acquire_lock
LOCK_ACQUIRE.argtypes = [ctypes.c_void_p, ctypes.c_int]
LOCK_ACQUIRE.restype = ctypes.c_int

LOCK_RELEASE = PYLIB.PyThread_release_lock
LOCK_RELEASE.argtypes = [ctypes.c_void_p]

LIBC = ctypes.CDLL('libc.so.6')
LIBC_SLEEP = LIBC.sleep
LIBC_SLEEP.argtypes = [ctypes.c_uint]
LIBC_SLEEP.restype = ctypes.c_uint

@njit(nogil=True)
def do_calc(lock, result):
    idx = int(numpy.random.rand() * result.shape[0])
    
    LOCK_ACQUIRE(lock, 1)
    existing = result[idx]
    LIBC_SLEEP(1)
    result[idx] = existing + 1
    LOCK_RELEASE(lock)
    
    
result = numpy.zeros((100,), dtype=int)
mylock = LOCK_CREATE()

threads = []
for _ in range(100):
    t = threading.Thread(target=do_calc, args=(mylock, result))
    threads.append(t)
    
# Start each thread
for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()

LOCK_DESTROY(mylock)

print(result.sum())
```

Note that this code uses functions from [pythread.h](https://github.com/python/cpython/blob/main/Include/pythread.h)
that allow us to lock threads in a platform independent way. Note also the `nogil=True` parameter to the `@njit`
decorator that releases the Python GIL and allows your threads to run all at once.
If you remove the locking then you will see that `result` does not add up to 100 as values will get overridden by
other threads between reading and writing in a random manner.

# Using `ctypes.c_void_p` with @jitclass

Sometimes it is desirable to wrap a collection of C functions within a @jitclass. All `ctypes` types
should map obviously to Numba types, the exception is `ctypes.c_void_p` which can be mapped to 
`types.intp` as shown below:

```python
from numba.core import types
from numba.experimental import jitclass
...

spec = [('ptr', types.intp)]
@jitclass(spec)
class MyLock:
    def __init__(self):
        self.ptr = LOCK_CREATE()
    ...
```


# Calling out to libraries with more complex interfaces

Where this approach can fall down is when calling more complex interfaces: ones with structures that get passed around
or those written in C++.

`ctypes` does have [support for structures](https://docs.python.org/3/library/ctypes.html#structures-and-unions) but
[Numba does not support this](https://numba.readthedocs.io/en/stable/reference/pysupported.html#ctypes). 

Calling C++ is a more complex undertaking and it not possible in a platform independent manner from within Python.

There is some support for [structures with CFFI](https://numba.readthedocs.io/en/stable/user/cfunc.html#handling-c-structures)
but this requires copying and pasting C code. We would recommend making a small C library that hides the complexity
and returns what you are actually after. [ctypesqhull](https://github.com/gillins/ctypesqhull) is an example
of this approach. 

# Passing a numpy array into a C function

`qhull` requires a C array with the input data. Fortunately what is expected matches the default layout of a numpy array.
In this situation, we can pass data straight in as a `ctypes.c_void_p` from the  [`ctypes.data`](https://numpy.org/doc/2.1/reference/generated/numpy.ndarray.ctypes.html) property of a numpy array.
We do have to check that the types, dimensions and layout match what [is expected](https://github.com/gillins/ctypesqhull?tab=readme-ov-file#how-to-use) otherwise you will get incorrect 
results (or program crash).

# Conclusion

Being able to call C functions from inside Numba is another useful feature to be aware of. Take care - the lack
of memory safety in C can cause problems. The function definitions must match exactly otherwise you will 
likely face some really strange bugs.
