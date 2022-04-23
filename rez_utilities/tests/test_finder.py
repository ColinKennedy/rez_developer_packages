#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`rez_utilities.finder` works as expected."""

import atexit
import functools
import os
import shutil
import tempfile
import unittest

from rez_utilities import finder

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class GetNearestRezPackage(unittest.TestCase):
    """Make sure :func:`rez_utilities.finder.get_nearest_rez_package` works."""

    def test_get_current_package(self):
        """Make sure we can get the current Rez package."""
        package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)

        self.assertEqual("rez_utilities", package.name)

    def test_missing(self):
        """Don't return a package if there is none."""
        directory = tempfile.mkdtemp("_test_missing")
        atexit.register(functools.partial(shutil.rmtree, directory))

        package = finder.get_nearest_rez_package(directory)

        self.assertIsNone(package)
