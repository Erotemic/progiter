|Travis| |Codecov| |Appveyor| |Pypi|

ProgIter
========

A standalone version of the utility currently in `ubelt`_.

Docs are being written at https://progiter.readthedocs.io/en/latest/

Installation
------------

From pypi:
^^^^^^^^^^

::

   pip install progiter

From github:
^^^^^^^^^^^^

::

   pip install git+https://github.com/Erotemic/progiter.git

Description
-----------

``ProgIter`` is a (mostly) drop-in alternative to tqdm_. The
``tqdm`` library may be more appropriate in some cases. *The advantage
of ``ProgIter`` is that it does not use any python threading*, and
therefore can be safer with code that makes heavy use of
multiprocessing. `The reason`_ for this is that threading before forking
may cause locks to be duplicated across processes, which may lead to
deadlocks.

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

.. _ubelt: https://github.com/Erotemic/ubelt
.. _tqdm: https://pypi.python.org/pypi/tqdm
.. _The reason: https://pybay.com/site_media/slides/raymond2017-keynote/combo.html

.. |Travis| image:: https://img.shields.io/travis/Erotemic/progiter/master.svg?label=Travis%20CI
   :target: https://travis-ci.org/Erotemic/progiter
.. |Codecov| image:: https://codecov.io/github/Erotemic/progiter/badge.svg?branch=master&service=github
   :target: https://codecov.io/github/Erotemic/progiter?branch=master
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Erotemic/progiter?svg=True
   :target: https://ci.appveyor.com/project/Erotemic/progiter/branch/master
.. |Pypi| image:: https://img.shields.io/pypi/v/progiter.svg
   :target: https://pypi.python.org/pypi/progiter
