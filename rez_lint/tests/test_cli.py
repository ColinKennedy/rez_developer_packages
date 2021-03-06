#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the plugin registry calls for :mod:`rez_lint.cli`."""

import os
import unittest

from rez_lint import cli
from rez_utilities import finder

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Generic(unittest.TestCase):
    """Test the plugin registry calls for :mod:`rez_lint.cli`."""

    def test_not_recursive(self):
        """Make sure that getting plugins from a given directory works."""
        package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)
        found, invalids = cli._find_rez_packages(  # pylint: disable=protected-access
            finder.get_package_root(package), recursive=False,
        )
        found_package = next(iter((found)))

        self.assertEqual(1, len(found))
        self.assertTrue(bool(found))
        self.assertEqual(found_package.name, package.name)
        self.assertEqual(found_package.filepath, package.filepath)
        self.assertEqual(found_package.version, package.version)
        self.assertEqual(set(), invalids)

    def test_recursive(self):
        """Make sure that getting plugins recursively works."""
        package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)
        found, invalids = cli._find_rez_packages(  # pylint: disable=protected-access
            finder.get_package_root(package), recursive=True,
        )
        found_package = next(iter((found)))

        self.assertEqual(1, len(found))
        self.assertTrue(bool(found))
        self.assertEqual(found_package.name, package.name)
        self.assertEqual(found_package.filepath, package.filepath)
        self.assertEqual(found_package.version, package.version)
        self.assertEqual(set(), invalids)
