# -*- coding: utf-8 -*-
"""
ProgIter lets you measure and print the progress of an iterative process. This
can be done either via an iterable interface or using the manual api. Using the
iterable inferface is most common.

ProgIter was originally developed independantly of ``tqdm``, but the newer
versions of this library have been designed to be compatible with tqdm-API.
``ProgIter`` is now a (mostly) drop-in alternative to tqdm_. The ``tqdm``
library may be more appropriate in some cases. *The main advantage of ``ProgIter``
is that it does not use any python threading*, and therefore can be safer with
code that makes heavy use of multiprocessing. `The reason`_ for this is that
threading before forking may cause locks to be duplicated across processes,
which may lead to deadlocks.

ProgIter is simpler than tqdm, which may be desirable for some applications.
However, this also means ProgIter is not as extensible as tqdm. If you want a
pretty bar, use tqdm; if you want useful information (rate, fraction-complete,
estimated time remaining, time taken so far, current wall time) about your
iteration by default, use progiter.

Example
-------

The basic usage of ProgIter is simple and intuitive. Just wrap a python
iterable.  The following example wraps a ``range`` iterable and prints reported
progress to stdout as the iterable is consumed. The ``ProgIter`` object accepts
various keyword arguments to modify the details of how progress is measured and
reported. See API documentation of the ``ProgIter`` classs here:
https://progiter.readthedocs.io/en/latest/progiter.progiter.html#progiter.progiter.ProgIter

Note that by default ProgIter reports information about iteration-rate,
fraction-complete, estimated time remaining, time taken so far, and the current
wall time.

.. code:: python

   >>> from progiter import ProgIter
   >>> def is_prime(n):
   ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
   >>> for n in ProgIter(range(1000), verbose=2):
   >>>     # do some work
   >>>     is_prime(n)
       0/1000... rate=0.00 Hz, eta=?, total=0:00:00, wall=14:05 EST
       1/1000... rate=82241.25 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST
     257/1000... rate=177204.69 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST
     642/1000... rate=94099.22 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST
    1000/1000... rate=71886.74 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST

"""
from __future__ import unicode_literals
from .progiter import (ProgIter,)

__version__ = '0.1.3'
__all__ = [
    'ProgIter',
]
