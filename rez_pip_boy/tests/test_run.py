#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check to make sure ``rez_pip_boy`` makes "source" Rez pip packages as we expect."""

import unittest


class Integration(unittest.TestCase):
    """Build source Rez packages, using Rez-generated pip packages."""

    def test_simple(self):
        """Install a really simple pip package (a package with no dependencies)."""
        pass

    def test_complex_001(self):
        """Install a package with many dependencies and make sure each one is installed."""
        pass

    def test_complex_002(self):
        """Install another package."""
        pass

    def test_recurring(self):
        """Install a package and then install the same package again."""
        pass

    def test_partial_install(self):
        """Install a package, delete one of its depedencies, and then install it again."""
        pass

    def test_hashed_variants(self):
        """Make sure hashed variants work."""
        pass

    def test_regular_variants(self):
        """Make sure non-hashed variants work."""
        pass
