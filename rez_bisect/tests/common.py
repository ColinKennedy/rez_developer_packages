#!/usr/bin/env python

import atexit
import functools
import shutil
import tempfile


def make_directory():
    directory = tempfile.mkdtemp(suffix="_make_directory")
    atexit.register(functools.partial(shutil.rmtree, directory))

    return directory
