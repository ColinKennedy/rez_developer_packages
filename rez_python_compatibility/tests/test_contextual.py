#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`python_compatibility.testing.contextual` works."""

import sys
import unittest

from python_compatibility.testing import contextual


class KeepSysPath(unittest.TestCase):
    """Make sure :func:`python_compatibility.testing.contextual.keep_sys_path` works."""

    def test_do_nothing(self):
        """Don't do anything."""
        original = list(sys.path)

        with contextual.keep_sys_path():
            pass

        self.assertEqual(original, sys.path)

    def test_restore(self):
        """Restore sys.path to its previous point."""
        original = list(sys.path)
        value = ["foo"]

        with contextual.keep_sys_path():
            sys.path[:] = value

        self.assertEqual(original, sys.path)
        self.assertNotEqual(value, sys.path)
