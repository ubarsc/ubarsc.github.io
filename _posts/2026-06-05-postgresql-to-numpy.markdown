---
layout: post
title:  "Reading results from PostGreSQL directly into numpy arrays"
date:   2026-06-05 10:00:00 +1000
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

# Processing the result with numpy

In the above example, the binary data will be read in to the `result` variable. The format
of the resulted binary data is explained in [the PostGreSQL documentation](https://www.postgresql.org/docs/current/sql-copy.html#SQL-COPY-BINARY-FORMAT). 
The first thing to note is that there is a header before the start of the data and a trailer 
at the end of the data. numpy allows us to specify the size of any header, but not the size
of the trailer.


# Conclusion
