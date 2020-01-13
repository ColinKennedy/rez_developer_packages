#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test all functions in the :mod:`rez_utilities.inspection` module."""

import os
import tempfile
import unittest

from python_compatibility.testing import common
from rez_utilities import inspection

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def _has_versioned_parent_package_folder():
    """bool: Check if this unittest suite is being run from a built Rez package."""
    package = inspection.get_nearest_rez_package(_CURRENT_DIRECTORY)
    root = inspection.get_package_root(package)
    folder = os.path.basename(root)

    return folder == os.environ["REZ_{name}_VERSION".format(name=package.name.upper())]


class Packaging(common.Common):
    """Check that Rez package files are found correctly."""

    @unittest.skipIf(
        _has_versioned_parent_package_folder(),
        "This unittest is being run from a built package",
    )
    def test_built_package_false(self):
        """Check that source Rez packages do not return True for :func:`.is_built_package`."""
        package = inspection.get_nearest_rez_package(
            os.path.dirname(_CURRENT_DIRECTORY)
        )
        self.assertFalse(inspection.is_built_package(package))

    def test_built_package_invalid(self):
        """Check that non-package input to :func:`.is_built_package` raises an exception."""
        with self.assertRaises(ValueError):
            inspection.is_built_package(None)

    def test_detect_found_001(self):
        """Check that valid directory input can find Rez packages correctly."""
        self.assertIsNotNone(
            inspection.get_nearest_rez_package(os.path.dirname(_CURRENT_DIRECTORY))
        )

    def test_detect_found_002(self):
        """Check that valid directory input can find Rez packages correctly."""
        self.assertIsNotNone(inspection.get_nearest_rez_package(_CURRENT_DIRECTORY))

    def test_detect_found_003(self):
        """Check that valid directory input can find Rez packages correctly."""
        self.assertIsNotNone(
            inspection.get_nearest_rez_package(os.path.join(_CURRENT_DIRECTORY, "foo"))
        )

    def test_detect_missing(self):
        """Check that a directory that has no Rez package returns None."""
        directory = tempfile.mkdtemp()
        self.add_item(directory)

        self.assertIsNone(inspection.get_nearest_rez_package(directory))

    # TODO : Need unittests for `has_python_package`
    #
    # - Source Rez package
    # - Source Rez package with variants
    # - Built Rez package
    #
    def test_python_package_true(self):
        """Make sure a source Rez package with no variant still works."""
        package = inspection.get_nearest_rez_package(
            os.path.dirname(_CURRENT_DIRECTORY)
        )
        self.assertTrue(inspection.has_python_package(package))

    def test_python_package_invalid(self):
        """Make sure a non-package input raises an exception."""
        with self.assertRaises(ValueError):
            inspection.has_python_package(None)
