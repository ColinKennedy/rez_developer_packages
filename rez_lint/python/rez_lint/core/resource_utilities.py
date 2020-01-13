#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic file-path operations."""

try:
    from functools import lru_cache  # python 3
except ImportError:
    from backports.functools_lru_cache import lru_cache  # python 2


@lru_cache()
def get_line_count(path):
    """int: Count the number of lines of a given file path and cache the result."""
    with open(path, "r") as handler:
        return len(handler.readlines())
