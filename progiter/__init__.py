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

   >>> # xdoctest: +SKIP
   >>> from progiter import ProgIter
   >>> def is_prime(n):
   ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
   >>> for n in ProgIter(range(1000), verbose=2):
   >>>     # do some work
   >>>     is_prime(n)
        0/1000... rate=0 Hz, eta=?, total=0:00:00
        1/1000... rate=137004.92 Hz, eta=0:00:00, total=0:00:00
        4/1000... rate=117671.14 Hz, eta=0:00:00, total=0:00:00
       16/1000... rate=265151.10 Hz, eta=0:00:00, total=0:00:00
       64/1000... rate=511709.21 Hz, eta=0:00:00, total=0:00:00
      256/1000... rate=541513.70 Hz, eta=0:00:00, total=0:00:00
     1000/1000... rate=251898.43 Hz, eta=0:00:00, total=0:00:00


"""
from .progiter import (ProgIter,)

__version__ = '1.0.0'
__all__ = [
    'ProgIter',
]
