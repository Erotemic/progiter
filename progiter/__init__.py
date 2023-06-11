"""
ProgIter lets you measure and print the progress of an iterative process. This
can be done either via an iterable interface or using the manual API. Using the
iterable interface is most common.

ProgIter is *unthreaded*. This differentiates it from
`tqdm <https://github.com/tqdm/tqdm>`_ and
`rich.progress <https://rich.readthedocs.io/en/stable/progress.html>`_
which use a *threaded* implementation.
The choice of implementation has different tradeoffs and neither is strictly
better than the other.
An unthreaded progress bar provides synchronous uncluttered logging, increased
stability, and --- unintuitively ---- speed (due to Python's GIL).
Meanwhile threaded progress bars are more responsive, able to update multiple
stdout lines at a time, and can look prettier (unless you try to log stdout to
disk).

ProgIter was originally developed independently of ``tqdm``, but the newer
versions of this library have been designed to be compatible with tqdm-API.
``ProgIter`` is now a (mostly) drop-in alternative to tqdm_. The ``tqdm``
library may be more appropriate in some cases. The main advantage of ``ProgIter``
is that it does not use any python threading, and therefore can be safer with
code that makes heavy use of multiprocessing.
`The reason <https://pybay.com/site_media/slides/raymond2017-keynote/combo.html>`_
for this is that threading before forking may cause locks to be duplicated
across processes, which may lead to deadlocks.

ProgIter is simpler than tqdm, which may be desirable for some applications.
However, this also means ProgIter is not as extensible as tqdm.
If you want a pretty bar or need something fancy, use tqdm (or rich);
if you want useful information  about your iteration by default, use progiter.

Package level documentation can be found at: https://progiter.readthedocs.io/en/latest/

Example
-------

The basic usage of ProgIter is simple and intuitive: wrap a python iterable.
The following example wraps a ``range`` iterable and reports progress to stdout
as the iterable is consumed. The ``ProgIter`` object accepts various keyword
arguments to modify the details of how progress is measured and reported. See
API documentation of the ``ProgIter`` class here:
https://progiter.readthedocs.io/en/latest/progiter.progiter.html#progiter.progiter.ProgIter


.. code:: python

    >>> from progiter import ProgIter
    >>> def is_prime(n):
    ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
    >>> for n in ProgIter(range(1000), verbose=2):
    >>>     # do some work
    >>>     is_prime(n)
    0.00%    0/1000... rate=0 Hz, eta=?, total=0:00:00
    0.60%    6/1000... rate=76995.12 Hz, eta=0:00:00, total=0:00:00
    100.00% 1000/1000... rate=266488.22 Hz, eta=0:00:00, total=0:00:00
"""

__autogen__ = """
mkinit ~/code/progiter/progiter/__init__.py -w
"""

__version__ = '2.0.0'
from progiter import manager
from progiter import progiter

from progiter.manager import (ProgressManager,)
from progiter.progiter import (ProgIter,)

__all__ = ['ProgIter', 'ProgressManager', 'manager', 'progiter']
