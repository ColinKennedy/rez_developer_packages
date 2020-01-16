#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check everything in wrapping.py for issues."""

import functools
import unittest

from python_compatibility import wrapping


class Wraps(unittest.TestCase):
    """Check the wrapper functions for issues."""

    def test_run_once(self):
        """Make a function that only gets called once."""
        @wrapping.run_once
        def _add_to_list1(object_):
            object_.append(1)

        def _add_to_list2(object_):
            object_.append(1)

        trackers1 = []  # Some mutable type that we can use to track the number of calls
        tracked_function1 = functools.partial(_add_to_list1, trackers1)

        trackers2 = []  # Some mutable type that we can use to track the number of calls
        tracked_function2 = functools.partial(_add_to_list2, trackers2)

        number = 2

        for _ in range(number):
            tracked_function1()
            tracked_function2()

        self.assertEqual(number, len(trackers2))  # Make sure a normal function runs more than once
        self.assertEqual(1, len(trackers1))  # Make sure the wrapped function runs once
