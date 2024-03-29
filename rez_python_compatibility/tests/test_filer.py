#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test that file-system related functions work as expected."""

import os
import shutil
import tempfile
import unittest

from python_compatibility import filer
from python_compatibility.testing import common


def _allowed_to_symlink():
    """bool: Check if symlinking works on the current machine."""
    if not hasattr(os, "symlink"):
        return False

    source = os.path.realpath(tempfile.mkdtemp(suffix="_symlink_source"))
    destination = os.path.realpath(tempfile.mkdtemp(suffix="_symlink_destination"))
    shutil.rmtree(destination)

    try:
        os.symlink(source, destination)
    except OSError:
        # Occurs on Windows when not in a developer mode. Usually errors with
        # "A required privilege is not held by the client"
        #
        return False

    return True


class Invalids(unittest.TestCase):
    """Check that invalid input to the `in_directory` function behaves as expected."""

    def test_empty_001(self):
        """Check that `in_directory` is False if both paths are empty."""
        self.assertFalse(filer.in_directory("", "", follow=True))
        self.assertFalse(filer.in_directory("", "", follow=False))

    def test_empty_002(self):
        """Check that `in_directory` is False if one of the paths is empty."""
        self.assertFalse(filer.in_directory(tempfile.gettempdir(), "", follow=True))
        self.assertFalse(filer.in_directory(tempfile.gettempdir(), "", follow=False))

    def test_empty_003(self):
        """Check that `in_directory` is False if one of the paths is empty."""
        self.assertFalse(filer.in_directory("", tempfile.gettempdir(), follow=True))
        self.assertFalse(filer.in_directory("", tempfile.gettempdir(), follow=False))


class Permutations(unittest.TestCase):
    """A series of valid calls to `in_directory` that either return True or False."""

    def test_yes_001(self):
        """Check that `in_directory` returns True for normal paths."""
        self.assertTrue(
            filer.in_directory("/some/path/here", "/some/path", follow=True)
        )

    def test_yes_002(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertTrue(
            filer.in_directory("/some/path/here/", "/some/path", follow=True)
        )

    def test_yes_003(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertTrue(
            filer.in_directory("/some/path/here", "/some/path/", follow=True)
        )

    def test_yes_004(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertTrue(
            filer.in_directory("/some/path/here/", "/some/path/", follow=True)
        )

    def test_no_001(self):
        """Check that `in_directory` returns False for normal paths."""
        self.assertFalse(
            filer.in_directory("some/path/here", "/some/path", follow=True)
        )

    def test_no_002(self):
        """Check that `in_directory` returns False even with trailing slashes."""
        self.assertFalse(
            filer.in_directory("some/path/here/", "/some/path", follow=True)
        )

    def test_no_003(self):
        """Check that `in_directory` returns False even with trailing slashes."""
        self.assertFalse(
            filer.in_directory("some/path/here", "/some/path/", follow=True)
        )

    def test_no_004(self):
        """Check that `in_directory` returns False even with trailing slashes."""
        self.assertFalse(
            filer.in_directory("some/path/here/", "/some/path/", follow=True)
        )

    def test_no_005(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertFalse(
            filer.in_directory("/some/path/here/", "/some/path/here/", follow=True)
        )

    def test_no_006(self):
        """Check that `in_directory` returns True."""
        self.assertFalse(
            filer.in_directory("/some/path/here", "/some/path/here", follow=True)
        )


@unittest.skipIf(not _allowed_to_symlink(), "Symlink support is disabled.")
class Symlinks(common.Common):
    """Tests related to symlinks, which sometimes cause issues in UNIX systems."""

    def setUp(self):
        """Create a symlinked directory for the tests in this class."""
        super(Symlinks, self).setUp()

        directory = os.path.realpath(tempfile.mkdtemp(suffix="_Symlinks_setup_source"))

        self._source = os.path.join(directory, "inner_part")
        self._destination = os.path.join(
            os.path.realpath(tempfile.mkdtemp(suffix="_Symlinks_setup_destination")),
            "folder",
        )

        # We just want the directory name, not for it to exist
        shutil.rmtree(directory)
        os.symlink(directory, self._destination)

        self.delete_item_later(self._source)
        self.delete_item_later(self._destination)

    def test_yes_001(self):
        """Check that `in_directory` returns True for normal paths."""
        self.assertTrue(
            filer.in_directory(self._source, self._destination, follow=True)
        )

    def test_yes_002(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertTrue(
            filer.in_directory(self._source + os.sep, self._destination, follow=True)
        )

    def test_yes_003(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertTrue(
            filer.in_directory(self._source, self._destination + os.sep, follow=True)
        )

    def test_yes_004(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertTrue(
            filer.in_directory(
                self._source + os.sep, self._destination + os.sep, follow=True
            )
        )

    def test_no_001(self):
        """Check that `in_directory` returns False for normal paths."""
        self.assertFalse(
            filer.in_directory(self._source[1:], self._destination, follow=True)
        )

    def test_no_002(self):
        """Check that `in_directory` returns False even with trailing slashes."""
        self.assertFalse(
            filer.in_directory(
                self._source[1:] + os.sep, self._destination, follow=True
            )
        )

    def test_no_003(self):
        """Check that `in_directory` returns False even with trailing slashes."""
        self.assertFalse(
            filer.in_directory(
                self._source[1:], self._destination + os.sep, follow=True
            )
        )

    def test_no_004(self):
        """Check that `in_directory` returns False even with trailing slashes."""
        self.assertFalse(
            filer.in_directory(
                self._source[1:] + os.sep, self._destination + os.sep, follow=True
            )
        )

    def test_no_005(self):
        """Check that `in_directory` returns True even with trailing slashes."""
        self.assertFalse(
            filer.in_directory(self._source[1:], self._source[1:], follow=True)
        )

    def test_no_006(self):
        """Check that `in_directory` returns True."""
        self.assertFalse(
            filer.in_directory(
                self._source[1:] + os.sep, self._source[1:] + os.sep, follow=True
            )
        )
