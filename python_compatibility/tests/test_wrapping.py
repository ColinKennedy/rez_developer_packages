#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check everything in wrapping.py for issues."""

from __future__ import print_function

import functools
import os
import sys
import tempfile
import unittest

from python_compatibility import wrapping
from python_compatibility.testing import common


class Wraps(common.Common):
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

        self.assertEqual(
            number, len(trackers2)
        )  # Make sure a normal function runs more than once
        self.assertEqual(1, len(trackers1))  # Make sure the wrapped function runs once

    def test_keep_cwd_001(self):
        """Make sure the directory is kept after the `keep_cwd` Context returns.

        This test changes the user's directory to someplace else and
        then checks if the directory returned to its original position.

        """
        current_directory = os.getcwd()

        with wrapping.keep_cwd(current_directory):
            root = tempfile.mkdtemp()
            self.add_item(root)

            os.chdir(root)

        self.assertEqual(current_directory, os.getcwd())

    def test_keep_cwd_002(self):
        """Make sure the directory is kept after the `keep_cwd` Context returns.

        This test checks that the directory is saved even if the code
        within the Context does **not** actually change the directory to
        somewhere different.

        """
        current_directory = os.getcwd()

        with wrapping.keep_cwd(current_directory):
            root = tempfile.mkdtemp()
            self.add_item(root)

            os.chdir(root)

        self.assertEqual(current_directory, os.getcwd())

    def test_pipes_empty(self):
        """Check that pipes capture nothing in stdout and stderr if there is nothing."""
        with wrapping.capture_pipes() as output:
            pass

        stdout, stderr = output

        self.assertEqual("", stdout)
        self.assertEqual("", stderr)

    def test_pipes_multiple_lines(self):
        """Check that pipes capture stdout and stderr even with multiple statements."""
        with wrapping.capture_pipes() as output:
            print("Hello")
            print("there!")

            print("General", file=sys.stderr)
            print("Kanobi", file=sys.stderr)

        stdout, stderr = output

        self.assertEqual("Hello\nthere!\n", stdout)
        self.assertEqual("General\nKanobi\n", stderr)
