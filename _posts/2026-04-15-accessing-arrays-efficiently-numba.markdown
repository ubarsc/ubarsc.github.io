---
layout: post
title:  "Accessing Arrays efficiently in Numba"
date:   2026-04-15 10:00:00 +1000
categories: tutorial
---

# Introduction

Most modern computers come with a memory cache. This holds a copy
of memory chunks most recently used and can be [up to 100 times](https://www.hp.com/us-en/shop/tech-takes/what-is-cache-memory)
faster than normal memory. There are in fact often multiple levels of cache
but in this discussion we just assume there is just one.

Each time you access memory that is not in cache (known as a cache miss),
the CPU must go to main memory to retrieve the requested item. As
it does this, it makes a prediction that the items immediately following
will be the next ones requested, and loads a block of those into the
on-chip cache at the same time (with very little extra overhead). If the
prediction turns out to be correct, this means that those subsequent
requests are met from the (much faster) on-chip cache, rather than requiring
more requests to main memory.

In order to gain the most benefit from this, we should generally try to ensure
that our processing matches the predictions the cache system is making,
and so we should try to process in the order in which data is being held in
main memory.

Directly monitoring this aspect of performance tends to be quite difficult.
Confounding the analysis is the fact that operating systems 
tend to show that the CPU is 'busy' while waiting for
data to come from main memory. The only way to determine whether
a particular implementation is fast or not is to run it and
time how long it takes. Using how 'busy' the CPU is might not
give you an accurate picture.

```
A note about multi threading: Run multiple threads at once 
generally makes it harder for the cache to run efficiently 
since the memory requests become less predicable. Software also 
tends to have to add more locking and checking when multiple
threads are enabled and this overhead can affect the speed
of your code.
```

The below assumes there is no other competing processing
running on your hardware, results will vary depending on
what other things are going on in your system.

# This simple 1D case

Assume you are looping over a 1 dimensional array from the start
to the end. The array is 64KB (of 8 byte floats) and we 
assume the cache is 16KB:

```
[1,2,3.....2047,2048,2049,......4095,4096,4097.......8191]
 ^     ^        ^                    ^      ^
Cache  Cache    Cache                Cache  Cache
miss   hit      miss                 miss   hit
```

We are assuming that the CPU is implementing a simple caching 
system without any heuristics. When your code accesses the first
element there will likely be a cache miss. However for the next 
2048 elements the data will likely be in the cache already
and calculations will progress faster. But for element 2048 we
run out of data that is in the cache so that element will be 
slower to acccess while the value is fetched from main memory 
and the cache updated. Element 2049 will be relatively quick 
again until we hit element 4096.
So there will be 4 cache misses as you process the array in
sequential order. What happens when you process the array out of
order? If you processed element 0, first then element 2048,
then back to element 1? Well that could end up having a cache 
miss for every access - 2048 times slower!

So it is best to access elements that are next to each other.

# The 2 dimensional case

Things get a bit more complex with the multidimensional case. By 
default [numpy arrays are laid out in the "C" order](https://numpy.org/devdocs/dev/internals.html).
C uses row-major order, for an array with shape=(4, 5) this means:

```
array[0, 0], array[0, 1], array[0, 2], array[0, 3], array[1, 0], array[1, 1], array[1, 2].....
```

As you can see the last axis is grouped together in the array. So 
it makes the most sense to loop through each row so you are always
accessing the next element:

```python
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        sum += data[i, j]
```

If you were to reverse the order of these loops you would be 'jumping'
about in memory by `data.shape[1]` - not a huge deal with small arrays
but with larger ones this slowdown could be significant.

# The multidimensional case and transposing

This only gets more important if you have arrays with many dimensions.
Always loop through your array so the tightest loop is through the 
last axis, the second tightest loop through the second to last axis etc 
(assuming C layout).

This is how [numpy does it internally](https://numpy.org/devdocs/reference/c-api/iterator.html).

But what happens when your algorithm requires visiting the axes in 
a different order? This is where `numpy.transpose` comes in. It is often 
worthwhile transposing the order of your axes first so that they are in
the most optimal order for your algorithm.
But won't this create extra overhead? It does, but it is not as bad as
you might think. Firstly the input array is read by numpy in a sequential
order. Secondly, writing back to memory appears to happen "in the background"
so usually by the time you are reading the values they have been written 
to memory and the CPU does not have to wait. Often there are fewer cache misses
in total doing this.
Will this help your particular use case? You'd have to benchmark the transpose
and not transposed case and see what is faster. For big arrays it usually 
is faster.

# Conclusion

Not all locations in memory take equal time to access. Because of the cache,
most times it is the very next element from the previous one that will be fastest.
You will need to think about this especially for multidimensional arrays.
Note that processing using threads reduces predictability and often takes
more CPU cycles for the same result. This is why Numba's `prange` usually does
not give expected speedups. 
Transposing your input array so it is in the correct order is often leads 
to a significant speedup, but the only way to be sure is to run timings
for the various approaches.



