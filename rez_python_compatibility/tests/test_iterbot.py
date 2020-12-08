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

        self.assertEqual(
            [(False, "foo"), (True, "bar")], list(iterbot.iter_is_last(items))
        )
        self.assertEqual(
            [(False, "foo"), (True, "bar")], list(iterbot.iter_is_last(generator))
        )
        self.assertEqual(
            [(False, "foo"), (True, "bar")], list(iterbot.iter_is_last(iter_tuple))
        )

    def test_invalid(self):
        """Make sure bad inputs raise `ValueError`."""
        with self.assertRaises(ValueError):
            list(iterbot.iter_is_last(None))

    def test_multiple(self):
        """Process big lists."""
        items = range(100)
        generator = (item for item in range(100))

        expected = [
            (False, index) if index < 99 else (True, index) for index in range(100)
        ]

        self.assertEqual(expected, list(iterbot.iter_is_last(items)))
        self.assertEqual(expected, list(iterbot.iter_is_last(generator)))

    def test_simple_bug(self):
        """Make sure a simple list works as expected."""
        self.assertEqual(
            [(False, "another"), (False, "jpeg"), (True, "many")],
            list(iterbot.iter_is_last(["another", "jpeg", "many"])),
        )


class IterSubFinder(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(
            [],
            list(iterbot.iter_sub_finder([4, 5], []))
        )

        with self.assertRaises(ValueError):
            list(iterbot.iter_sub_finder([], [range(10)]))

    def test_find(self):
        self.assertEqual(
            [4],
            list(iterbot.iter_sub_finder([4, 5], list(range(10))))
        )

    def test_multiple_find_001(self):
        self.assertEqual(
            [4, 14],
            list(iterbot.iter_sub_finder(
                [4, 5],
                list(range(10)) + list(range(10)),
            ))
        )

class MakeChains(unittest.TestCase):
    def test_custom(self):
        self.assertEqual(
            [range(0, 4), range(1, 5)],
            list(iterbot.make_chains(range(5), size=4)),
        )

    def test_default(self):
        self.assertEqual(
            [range(0, 2), range(1, 3), range(2, 4), range(3, 5)],
            list(iterbot.make_chains(range(5))),
        )

    def test_empty(self):
        self.assertEqual(
            [],
            list(iterbot.make_chains([], size=4)),
        )

    def test_invalid(self):
        """Make sure invalid values fail execution."""
        with self.assertRaises(ValueError):
            list(iterbot.make_chains(None, size=1))

        with self.assertRaises(ValueError):
            list(iterbot.make_chains([], size=-1))

    def test_one(self):
        self.assertEqual(
            [range(0, 1)],
            list(iterbot.make_chains(range(1), size=1)),
        )

    def test_string(self):
        self.assertEqual(
            ["abc", "bcd", "cde", "def", "efg"],
            list(iterbot.make_chains("abcdefg", size=3)),
        )

    def test_too_high(self):
        length = 5
        self.assertEqual(
            [],
            list(iterbot.make_chains(range(length), size=length + 1)),
        )


class MakePairs(unittest.TestCase):
    def test_empty(self):
        self.assertEqual([], list(iterbot.make_pairs([])))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            list(iterbot.make_pairs(None))

    def test_many(self):
        self.assertEqual(
            [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)],
            list(iterbot.make_pairs(range(10))),
        )

    def test_odd(self):
        self.assertEqual(
            [(0, 1), (2, 3), (4, 5), (6, 7)],
            list(iterbot.make_pairs(range(9))),
        )
