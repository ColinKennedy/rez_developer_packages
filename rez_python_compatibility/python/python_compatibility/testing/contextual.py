#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Context managers which can be used for unittesting or other purposes."""

import contextlib
import sys


@contextlib.contextmanager
def keep_sys_path():
    """Save :attr:`sys.path` and restore it later."""
    original = list(sys.path)

    try:
        yield
    finally:
        sys.path[:] = original
