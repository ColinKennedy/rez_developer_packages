#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import sys


@contextlib.contextmanager
def keep_sys_path():
    original = list(sys.path)

    try:
        yield
    finally:
        sys.path[:] = original
