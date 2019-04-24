# -*- coding: utf-8 -*-
"""
ProgIter is a simple way to indicate progress of an iterative process.

Its basic usage is simple and intuitive. Just wrap a python iterable.

Example:
    >>> from progiter import ProgIter
    >>> for item in ProgIter(range(1000)):
    >>>     item  # Do Work
"""
from __future__ import unicode_literals
from .progiter import (ProgIter,)

__version__ = '0.1.1'
__all__ = [
    'ProgIter',
]
