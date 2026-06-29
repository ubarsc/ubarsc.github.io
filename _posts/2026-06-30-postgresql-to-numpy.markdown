---
layout: post
title:  "Reading results from PostGreSQL directly into numpy arrays"
date:   2026-06-30 08:00:00 +1000
categories: tutorial
---

# Introduction

Traditionally, Python programs talk to [PostGreSQL](https://www.postgresql.org/) using
a tool like [psycopg](https://www.psycopg.org/) and loop over the results of a query
doing whatever processing is required for each row returned.
However, this can be slow when many results are returned. It is also painful when 
you want to be able to process the result with numpy or Numba and just need it
read in as quick as possible.
This is possible using the [COPY TO BINARY](https://www.postgresql.org/docs/current/sql-copy.html#SQL-COPY-BINARY-FORMAT)
command and some data manipulation.
Note that what follows is a complex dive into binary formats and is not for the faint hearted.
You will be expected to know the data types that are returned from a query.

# Using COPY TO BINARY

[psycopg's documentation](https://www.psycopg.org/psycopg3/docs/basic/copy.html#binary-copy) is a bit
vague about how to copy a query to a binary object. The trick is to use [io.BytesIO](https://docs.python.org/3/library/io.html#io.BytesIO) and write each binary chunk as it is returned
from the [cursor.copy](https://www.psycopg.org/psycopg3/docs/api/cursors.html#psycopg.Cursor.copy) function:

```python
result = io.BytesIO()
with curs.copy("COPY (SELECT * FROM my_table) TO STDOUT BINARY") as copy:
    for raw in copy:
        result.write(raw)
```

```
Note: you still have to loop over each result row. 
There doesn't appear to be a way of getting all results in one go.
However - this is still faster than processing each row into a tuple etc
```

# Processing the result with numpy

In the above example, the binary data will be read in to the `result` variable. The format
of the resulted binary data is explained in [the PostGreSQL documentation](https://www.postgresql.org/docs/current/sql-copy.html#SQL-COPY-BINARY-FORMAT). 
The first thing to note is that there is a header before the start of the data and a trailer 
at the end of the data. numpy allows us to specify the size of any header, but not the size
of the trailer. To remove the trailer before further processing, run:

```python
notrailer = result.getvalue()[:-2]  # unread the trailer
```

Next, the data can be read into a numpy array using the `numpy.frombuffer` function
by specifying the `dtype` of the result of your query.

```
Note: You will need to be sure what types are returned from your query 
before determining the dtype.
```

In addition need to understand how PostGreSQL serialises types before you
can interpret the result as a dtype. The [documentation](https://www.postgresql.org/docs/current/sql-copy.html#SQL-COPY-BINARY-FORMAT)
points you to [this directory](https://github.com/postgres/postgres/tree/master/src/backend/utils/adt)
in the PostGreSQL sources to work out the types. To get you started, below is a table of
commonly used types and how to interpret them with numpy:

| PostGreSQL Type | numpy dtype |
|-----------------|-------------|
| int             | >u4         |
| float           | >f8         |
| array           | >u4 (ndims) |
|                 | >u4 (has null) |
|                 | >u4 (element type |
|                 | For each dimension: |
|                 |   >u4 size of dim |
|                 |   >u4 lower bound |
|                 | Then for each value |
|                 |   >u4 size of value |
|                 |   Then value itself |

Unfortunately, variable length string data cannot be interpreted by
`numpy.frombuffer`. If all your strings are of fixed length you may 
be able to use the `S` format specifier along with the length.

```
Note: the > character before the type tells numpy the data is in big
endian format. PostGreSQL transmits data as big endian.
We will cover converting back to little endian later, but 
just be sure to specify this character otherwise you may not
be able to understand the result...
```

Currently the file header is 19 bytes (as documented in the PostGreSQL documentation). 
This means that the `offset` parameter to `numpy.frombuffer` must be set to 19.

Also, each row starts with a 16 bit integer (type `>u2`) with a count of the
results for that row. Since we provided the query we should be able to ignore this.

To process a result that has 2 floats for each row ('x' and 'y'):

```python
data = numpy.frombuffer(notrailer, 
    dtype=[('fields', '>u2'), ('sizex', '>u4'), ('x', '>f8'), ('sizey', '>u4'), ('y', '>f8')],
    offset=19)
```

The `sizex` and `sizey` fields can be safely ignored (assuming you are actually
reading in 2 floats!).

To process a result that has one float (radius) and one int (count) for each row:

```python
data = numpy.frombuffer(notrailer, 
    dtype=[('fields', '>u2'), ('sizeradius', '>u4'), ('radius', '>f8'), ('sizecount', '>u4'), ('count', '>u4')],
    offset=19)
```

Again, `sizeradius` and `sizecount` can be safely ignored if you know the types.

To read an array of a known size (4 elements in this example):

```python
data = numpy.frombuffer(notrailer, 
    dtype=[('fields', '>u2'), ('info_about_array', '>u4', (5,)), 
        ('array', [('offset', '>u4'), ('value', '>f8')], 4)],
    offset=19)
```

In this case we can ignore the `ndims` etc for the array (see table above,
this is stored in the `info_about_array` field. The data for the array
will be stored in the `array` field.

# Converting to the correct endian

As discussed above, PostGreSQL transmits all data as big endian. Most machines
now are little endian. So the data contained in these structured arrays are
likely to wrong for your CPU. You can find which byte order your machine is using
by printing the value of `sys.byteorder`:

```python
import sys
print(sys.byteorder)
```

If this is `little` you will need to convert the arrays to little endian with 
code like this:

```python
data_native = data.byteswap()  # swap the data
data_native = data_native.view(data_native.dtype.newbyteorder())  # set the little endian data types
```

# Conclusion

Reading data into a numpy array from a PostGreSQL binary cursor is possible if
you need to get the data directly into numpy as quickly as possible. It is not
without its downsides, but if you are getting back large arrays and numpy is
the only way they can be processed then the method described above is feasible.

