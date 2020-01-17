#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A basic class that makes writing unittests a little easier."""

import os
import shutil
import sys
import unittest


class Common(unittest.TestCase):
    """A generic unittest class that deletes temporary files when needed."""

    def __init__(self, *args, **kwargs):
        """Create this class and add temporary variables for reverting the user's environment."""
        super(Common, self).__init__(*args, **kwargs)

        self._items = set()
        self._sys_path = []

    def setUp(self):
        """Save any temporary file(s)/folder(s) and delete them once the test is over."""
        self._items.clear()
        self._sys_path = sys.path[:]
        self._environment = os.environ.copy()

    def tearDown(self):
        """Delete any file(s)/folder(s) that were created."""
        for item in self._items:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)

        sys.path[:] = self._sys_path
        os.environ.clear()
        os.environ.update(self._environment)

    def add_item(self, item):
        """Add the given file/folder to the unittest."""
        self._items.add(item)

    def add_items(self, items):
        """Add every given file/folder to the unittest."""
        self._items.update(items)


def make_files(file_structure):
    pass
