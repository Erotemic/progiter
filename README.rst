|GithubActions| |ReadTheDocs| |Pypi| |Downloads| |Codecov| 


ProgIter
========

ProgIter lets you measure and print the progress of an iterative process. This
can be done either via an iterable interface or using the manual API. Using the
iterable interface is most common.

.. image:: https://i.imgur.com/HoJJYzd.gif
   :height: 300px
   :align: left

ProgIter was originally developed independently of ``tqdm``, but the newer
versions of this library have been designed to be compatible with tqdm-API.
``ProgIter`` is now a (mostly) drop-in alternative to tqdm_. The ``tqdm``
library may be more appropriate in some cases. *The main advantage of ``ProgIter``
is that it does not use any python threading*, and therefore can be safer with
code that makes heavy use of multiprocessing. `The reason`_ for this is that
threading before forking may cause locks to be duplicated across processes,
which may lead to deadlocks.

ProgIter is simpler than tqdm, which may be desirable for some applications.
However, this also means ProgIter is not as extensible as tqdm.
If you want a pretty bar or need something fancy, use tqdm;
if you want useful information  about your iteration by default, use progiter. 

Package level documentation can be found at: https://progiter.readthedocs.io/en/latest/

Example
-------

The basic usage of ProgIter is simple and intuitive. Just wrap a python
iterable.  The following example wraps a ``range`` iterable and prints reported
progress to stdout as the iterable is consumed. The ``ProgIter`` object accepts
various keyword arguments to modify the details of how progress is measured and
reported. See API documentation of the ``ProgIter`` class here:
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
       0/1000... rate=0 Hz, eta=?, total=0:00:00, wall=12:47 EST
       1/1000... rate=58551.44 Hz, eta=0:00:00, total=0:00:00, wall=12:47 EST
     257/1000... rate=317349.77 Hz, eta=0:00:00, total=0:00:00, wall=12:47 EST
     642/1000... rate=191396.29 Hz, eta=0:00:00, total=0:00:00, wall=12:47 EST
    1000/1000... rate=139756.95 Hz, eta=0:00:00, total=0:00:00, wall=12:47 EST



For more complex applications is may sometimes be desireable to manually use
the ProgIter API. This is done as follows:

.. code:: python 

    >>> from progiter import ProgIter
    >>> n = 3
    >>> prog = ProgIter(desc='manual', total=n, verbose=3)
    >>> prog.begin() # Manually begin progress iteration
    >>> for _ in range(n):
    ...     prog.step(inc=1)  # specify the number of steps to increment
    >>> prog.end()  # Manually end progress iteration
    manual 0/3... rate=0 Hz, eta=?, total=0:00:00, wall=12:46 EST
    manual 1/3... rate=12036.01 Hz, eta=0:00:00, total=0:00:00, wall=12:46 EST
    manual 2/3... rate=16510.10 Hz, eta=0:00:00, total=0:00:00, wall=12:46 EST
    manual 3/3... rate=20067.43 Hz, eta=0:00:00, total=0:00:00, wall=12:46 EST

When working with ProgIter in either iterable or manual mode you can use the
``prog.ensure_newline`` method to guarantee that the next call you make to stdout
will start on a new line. You can also use the ``prog.set_extra`` method to
update a dynamic "extra" message that is shown in the formatted output. The
following example demonstrates this.


.. code:: python 

    >>> from progiter import ProgIter
    >>> def is_prime(n):
    ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
    >>> _iter = range(1000)
    >>> prog = ProgIter(_iter, desc='check primes', verbose=2)
    >>> for n in prog:
    >>>     if n == 97:
    >>>         print('!!! Special print at n=97 !!!')
    >>>     if is_prime(n):
    >>>         prog.set_extra('Biggest prime so far: {}'.format(n))
    >>>         prog.ensure_newline()
    check primes    0/1000... rate=0 Hz, eta=?, total=0:00:00, wall=12:55 EST
    check primes    1/1000... rate=98376.78 Hz, eta=0:00:00, total=0:00:00, wall=12:55 EST
    !!! Special print at n=97 !!!
    check primes  257/1000...Biggest prime so far: 251 rate=308037.13 Hz, eta=0:00:00, total=0:00:00, wall=12:55 EST
    check primes  642/1000...Biggest prime so far: 641 rate=185166.01 Hz, eta=0:00:00, total=0:00:00, wall=12:55 EST
    check primes 1000/1000...Biggest prime so far: 997 rate=120063.72 Hz, eta=0:00:00, total=0:00:00, wall=12:55 EST


Installation
------------

ProgIter can be easily installed via `pip`. 

.. code:: bash

   pip install progiter

Alternatively, the `ubelt`_ library ships with its own version of ProgIter.
Note that the `ubelt` version of progiter is distinct (i.e. ubelt actually
contains a copy of this library), but the two libraries are generally kept in
sync. 


.. _ubelt: https://github.com/Erotemic/ubelt
.. _tqdm: https://pypi.python.org/pypi/tqdm
.. _The reason: https://pybay.com/site_media/slides/raymond2017-keynote/combo.html


.. |Travis| image:: https://img.shields.io/travis/Erotemic/progiter/master.svg?label=Travis%20CI
   :target: https://travis-ci.org/Erotemic/progiter?branch=master
.. |Codecov| image:: https://codecov.io/github/Erotemic/progiter/badge.svg?branch=master&service=github
   :target: https://codecov.io/github/Erotemic/progiter?branch=master
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Erotemic/progiter?branch=master&svg=True
   :target: https://ci.appveyor.com/project/Erotemic/progiter/branch/master
.. |Pypi| image:: https://img.shields.io/pypi/v/progiter.svg
   :target: https://pypi.python.org/pypi/progiter
.. |Downloads| image:: https://img.shields.io/pypi/dm/progiter.svg
   :target: https://pypistats.org/packages/progiter
.. |CircleCI| image:: https://circleci.com/gh/Erotemic/progiter.svg?style=svg
    :target: https://circleci.com/gh/Erotemic/progiter
.. |ReadTheDocs| image:: https://readthedocs.org/projects/progiter/badge/?version=latest
    :target: http://progiter.readthedocs.io/en/latest/
.. |GithubActions| image:: https://github.com/Erotemic/progiter/actions/workflows/tests.yml/badge.svg?branch=main
    :target: https://github.com/Erotemic/progiter/actions?query=branch%3Amain
