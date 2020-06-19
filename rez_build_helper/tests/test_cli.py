#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`rez_build_helper` works as expected."""

import unittest


class Cli(unittest.TestCase):
    """Make sure the basic CLI functions work as-expected."""

    def test_empty(self):
        """Build even if the package just contains just a package.py file."""
        pass

    def test_copy(self):
        """Copy folder(s) for the build Rez package."""
        pass

    def test_symlink(self):
        """Create symlinks for each specified folder."""
        pass


class Egg(unittest.TestCase):
    """Make sure .egg generation and symlinking works as expected."""

    def test_single(self):
        """Create a collapsed .egg file for a Python folder."""
        pass

    def test_single_symlink(self):
        """Create a symlink for (what would have normally been) an .egg file."""
        pass

    def test_multiple(self):
        """Create more than one collapsed egg files for a Python folder."""
        pass

    def test_invalid(self):
        """Disallow non-root folders for .egg generation."""
        pass
