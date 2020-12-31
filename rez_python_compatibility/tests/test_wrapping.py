#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check everything in wrapping.py for issues."""

from __future__ import print_function

import functools
import os
import sys
import tempfile
import unittest

from python_compatibility import dependency_analyzer, imports, wrapping
from python_compatibility.testing import common


class WatchCallable(unittest.TestCase):
    """Make sure :func:python_compatibility.wrapping.watch_callable` works."""

    def test_class_call(self):
        """Watch a instance's ``__call__`` method."""
        caller = _Callable()

        with wrapping.watch_namespace(_Callable.__call__) as container:
            caller("thing")

        self.assertEqual(
            [(("thing",), dict(), 8)], [record.get_all() for record in container]
        )

    def test_class_init(self):
        """Watch a class's ``__init__`` method."""
        with wrapping.watch_namespace(
            dependency_analyzer._FakeModule.__init__,  # pylint: disable=protected-access
        ) as container:
            dependency_analyzer._FakeModule("text")  # pylint: disable=protected-access

        self.assertEqual(
            [(("text",), dict(), None)], [record.get_all() for record in container]
        )

    def test_instance_dunder(self):
        """Watch an instance's ``__repr__`` dunder (double-underscore) method."""

        with wrapping.watch_namespace(
            dependency_analyzer._FakeModule.__repr__  # pylint: disable=protected-access
        ) as container:
            item = dependency_analyzer._FakeModule(  # pylint: disable=protected-access
                "text"
            )
            repr(item)

        self.assertEqual(
            [(tuple(), dict(), "_FakeModule('text')")],
            [record.get_all() for record in container],
        )

    def test_instance_method_001(self):
        """Watch an instance's method."""
        item = dependency_analyzer._FakeModule(  # pylint: disable=protected-access
            "text"
        )

        with wrapping.watch_namespace(
            dependency_analyzer._FakeModule.get_path,  # pylint: disable=protected-access
        ) as container:
            item.get_path()

        self.assertEqual(
            [(tuple(), dict(), "text")], [record.get_all() for record in container]
        )

    def test_instance_method_002(self):
        """Watch an instance's method."""
        item = dependency_analyzer._FakeModule(  # pylint: disable=protected-access
            "text"
        )

        with wrapping.watch_namespace(
            dependency_analyzer._FakeModule.get_path,  # pylint: disable=protected-access
            implicits=True,
        ) as container:
            item.get_path()

        self.assertEqual(
            [((item,), dict(), "text")], [record.get_all() for record in container]
        )

    def test_function(self):
        """Watch a function from a module."""
        with wrapping.watch_namespace(imports.import_nearest_module) as container:
            imports.import_nearest_module("sys")

        self.assertEqual(
            [(("sys",), dict(), sys)], [record.get_all() for record in container]
        )

    def test_static_function(self):
        """Watch a function from a class."""
        with wrapping.watch_namespace(
            _Callable.do_static, namespace="tests.test_wrapping._Callable.do_static"
        ) as container:
            _Callable.do_static("thing")

        self.assertEqual(
            [(("thing",), dict(), 9)], [record.get_all() for record in container]
        )


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
            self.delete_item_later(root)

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
            self.delete_item_later(root)

            os.chdir(root)

        self.assertEqual(current_directory, os.getcwd())

    def test_os_environment(self):
        """Make sure :func:`python_compatibility.wrapping.keep_os_environment` works."""
        original = os.environ.copy()

        with wrapping.keep_os_environment():
            before = os.environ.copy()
            os.environ["FOO"] = "blah"
            after = os.environ.copy()

        self.assertEqual(original, before)
        self.assertNotEqual(before, after)
        self.assertEqual(original, os.environ)

    def test_sys_path(self):
        """Make sure :func:`python_compatibility.wrapping.keep_sys_path` works."""
        original = list(sys.path)

        with wrapping.keep_sys_path():
            before = list(sys.path)
            sys.path.append("/something")
            after = list(sys.path)

        self.assertEqual(original, before)
        self.assertNotEqual(before, after)
        self.assertEqual(original, sys.path)

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


class _Callable(object):
    """Some class for testing."""

    @staticmethod
    def do_static(_):
        """Do something."""
        return 9

    def __call__(self, item, blah=None):
        """Do something."""
        return 8
