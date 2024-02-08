#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A basic class that makes writing unittests a little easier."""

import io
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
        self._argv = []

    def setUp(self):
        """Save any temporary file(s)/folder(s) and delete them once the test is over."""
        self._items.clear()
        self._sys_path = sys.path[:]
        self._environment = os.environ.copy()
        self._argv = sys.argv[:]

    def tearDown(self):
        """Delete any file(s)/folder(s) that were created."""
        for item in self._items:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)

        sys.argv = self._argv
        sys.path[:] = self._sys_path
        os.environ.clear()
        os.environ.update(self._environment)

    def delete_item_later(self, item):
        """Add the given file/folder to the unittest."""
        self._items.add(item)

    def delete_items_later(self, items):
        """Add every given file/folder to the unittest."""
        self._items.update(items)


def make_files(file_structure, root):
    """Create a file and folder structure, starting a `root` directory.

    Args:
        file_structure (dict[str, dict[str] or None]): Every key represents a file or folder.
            If the value of that key is None, it is created as a file.
            If the key's value is an empty dict, an empty folder is
            created instead.
        root (str): The starting directory that is used to recursively build
            files and folders.

    """
    for key, items in file_structure.items():
        if items:
            make_files(items, os.path.join(root, key))

            continue

        item_path = os.path.join(root, key)
        directory = os.path.dirname(item_path)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        if items is None:
            if not os.path.isfile(item_path):
                with io.open(item_path, "a", encoding="ascii"):
                    pass
        elif not os.path.isdir(item_path):
            os.makedirs(item_path)
