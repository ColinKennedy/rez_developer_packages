#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make sure :mod:`python_compatibility.iterbot` works."""

import unittest

from python_compatibility import iterbot


class IterIsLast(unittest.TestCase):
    """Make sure :func:`python_compatibility.iterbot.iter_is_last` works."""

    def test_empty(self):
        """Loop over nothing."""
        items = []
        generator = (item for item in [])

        self.assertEqual([], list(iterbot.iter_is_last(items)))
        self.assertEqual([], list(iterbot.iter_is_last(generator)))

    def test_iterate(self):
        """Loop over some iterable objects."""
        items = ["foo", "bar"]
        generator = (item for item in ["foo", "bar"])
        iter_tuple = iter(("foo", "bar"))

        self.assertEqual([(False, "foo"), (True, "bar")], list(iterbot.iter_is_last(items)))
        self.assertEqual([(False, "foo"), (True, "bar")], list(iterbot.iter_is_last(generator)))
        self.assertEqual([(False, "foo"), (True, "bar")], list(iterbot.iter_is_last(iter_tuple)))

    def test_invalid(self):
        """Make sure bad inputs raise `ValueError`."""
        with self.assertRaises(ValueError):
            list(iterbot.iter_is_last(None))
