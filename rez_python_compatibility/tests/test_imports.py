#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Basic import/module related unittests."""

from __future__ import unicode_literals

import atexit
import functools
import io
import logging
import os
import shutil
import sys
import tempfile
import textwrap
import unittest

from python_compatibility import import_parser, imports, wrapping
from python_compatibility.testing import common


class GetNamespace(unittest.TestCase):
    """Make sure :func:`python_compatibility.imports.get_namespace` works."""

    def test_class(self):
        """Get the dot namespace of a Python class."""
        self.assertEqual(
            "python_compatibility.import_parser.Module",
            imports.get_namespace(import_parser.Module),
        )

    def test_class_call(self):
        """Get the dot namespace of a Python ``__call__`` method."""
        self.assertEqual(
            "python_compatibility.import_parser.Module.__call__",
            imports.get_namespace(import_parser.Module.__call__),
        )

    def test_class_init(self):
        """Get the dot namespace of a Python ``__init__`` method."""
        self.assertEqual(
            "python_compatibility.import_parser.Module.__init__",
            imports.get_namespace(import_parser.Module.__init__),
        )

    def test_class_method(self):
        """Get the dot namespace of a Python classmethod."""
        self.assertEqual(
            "python_compatibility.import_parser.Module.from_context",
            imports.get_namespace(import_parser.Module.from_context),
        )

    def test_function(self):
        """Get the dot namespace of a Python function."""
        self.assertEqual(
            "python_compatibility.imports.get_parent_module",
            imports.get_namespace(imports.get_parent_module),
        )

    def test_instance_method(self):
        """Get the dot namespace of a Python method of an instantiated class."""
        module = import_parser.Module("blah", "thing", 0)
        self.assertEqual(
            "python_compatibility.import_parser.Module.get_alias",
            imports.get_namespace(module.get_alias),
        )

    def test_instance_method_un_instantiated(self):
        """Get the dot namespace of a Python method of an un-instantiated class."""
        self.assertEqual(
            "python_compatibility.import_parser.Module.get_alias",
            imports.get_namespace(import_parser.Module.get_alias),
        )


class ImportDetection(common.Common):
    """Test that :func:`python_compatibility.imports.has_importable_module` works."""

    @classmethod
    def _build_file_tree(cls, tree, root):
        """Make file(s) / folder(s) recursively.

        Args:
            tree (dict[str, Nonetype or dict[str]]):
                A tree of file / folder names to create. If the value is
                None, a file is created. Otherwise, a folder is created
                and the folder is visited.
            root (str):
                The folder that will be used to create an absolute path
                of any key that is found in `tree`

        Returns:
            str: The top-level directory that was created.

        """
        if not root:
            root = tempfile.mkdtemp()

        for key, value in tree.items():
            path = os.path.join(root, key)

            if value is None:
                with io.open(path, "a", encoding="ascii"):
                    pass
            else:
                os.makedirs(path)
                cls._build_file_tree(value, root=path)

        return root

    def test_empty(self):
        """Test False if the Python path is empty."""
        directory = tempfile.mkdtemp()
        self.delete_item_later(directory)

        self.assertEqual([], os.listdir(directory))
        self.assertFalse(imports.has_importable_module(directory))

    def test_direct_import(self):
        """Test True if there's a Python file directly under a folder."""

    def test_invalid(self):
        """Test False if the Python path does not exist."""
        directory = tempfile.mkdtemp()
        shutil.rmtree(directory)

        with self.assertRaises(OSError):
            self.assertFalse(os.listdir(directory))

        self.assertFalse(imports.has_importable_module(directory))

    def test_sub_package_import(self):
        """Test True if there's a Python file within a folder that is importable."""
        tree = {
            "root": {
                "__init__.py": None,
                "sub_folder": {"__init__.py": None, "some_file": None},
            }
        }

        root = tempfile.mkdtemp()
        directory = self._build_file_tree(tree, root)

        self.assertEqual(["root"], os.listdir(directory))
        self.assertTrue(imports.has_importable_module(directory))

    def test_sub_package_inaccessible(self):
        """Test True if there's a Python file in a package but it cannot be imported."""
        tree = {"root": {"__init__.py": None, "sub_folder": {"some_file": None}}}

        root = tempfile.mkdtemp()
        directory = self._build_file_tree(tree, root)

        self.assertEqual(["root"], os.listdir(directory))
        self.assertTrue(imports.has_importable_module(directory))


class Run(common.Common):
    """Import Python modules and make sure it works correctly."""

    def test_standard_library(self):
        """Import a module from Python's own libraries."""
        path = os.path.splitext(textwrap.__file__)[0] + ".py"
        self.assertIsNotNone(imports.import_file("some_package", path))

    def test_invalid(self):
        """If the module fails to import, make sure the function fails, too."""
        # This is a module with a SyntaxError
        code = textwrap.dedent(
            """\
            foo =
            """
        )

        with tempfile.NamedTemporaryFile(
            suffix=".py", delete=False, mode="w"
        ) as handler:
            handler.write(code)

        self.delete_item_later(code)

        with self.assertRaises(SyntaxError):
            imports.import_file("fake_package", handler.name)


class ImportNearest(unittest.TestCase):
    """Test permutations of :func:`python_compatibility.imports.import_nearest_module`."""

    def test_module(self):
        """Import a module from a Python module namespace."""
        self.assertEqual(unittest, imports.import_nearest_module("unittest"))

    def test_function(self):
        """Import a module from a Python function namespace."""
        self.assertEqual(textwrap, imports.import_nearest_module("textwrap.dedent"))

    def test_module_attribute(self):
        """Import a module from a Python module attribute namespace."""
        self.assertEqual(sys, imports.import_nearest_module("sys.maxsize"))

    def test_class_attribute(self):
        """Import a module from a Python class attribute namespace."""
        self.assertEqual(
            unittest, imports.import_nearest_module("unittest.TestCase.setUp")
        )

    def test_invalid(self):
        """Fail to import if the namespace does not point to a Python module."""
        self.assertEqual(
            None, imports.import_nearest_module("something_that_doesnt_exist")
        )

    def test_undefined_name(self):
        """Prevent a module with an undefined name from breaking our function."""
        code = textwrap.dedent(
            """\
            def __some_function():
                pass

            some_undefined_name

            def another():
                pass
            """
        )

        directory = tempfile.mkdtemp(suffix="_ImportNearest_test_undefined_name")
        atexit.register(functools.partial(shutil.rmtree, directory))

        with io.open(
            os.path.join(directory, "some_name_mangled_file.py"),
            "w",
            encoding="ascii",
        ) as handler:
            handler.write(code)

        with wrapping.keep_sys_path():
            sys.path.append(directory)

            self.assertIsNone(imports.import_nearest_module("some_name_mangled_file"))
            self.assertIsNone(
                imports.import_nearest_module("some_name_mangled_file.another")
            )
            self.assertIsNone(
                imports.import_nearest_module("some_name_mangled_file.__some_function")
            )


class Module(unittest.TestCase):
    """Test different situations for :func:`python_compatibility.imports.get_parent_module`."""

    def test_normal(self):
        """Check that functions, classes, attributes, and the like all return correctly."""
        options = [
            ("unittest.TestCase", unittest),  # class
            ("logging.logThreads", logging),  # attribute
            ("textwrap.dedent", textwrap),  # function
            ("tempfile", tempfile),  # module
        ]

        for namespace, expected in options:
            self.assertEqual(expected, imports.get_parent_module(namespace))

    def test_missing(self):
        """Check that a non-existing namespace return nothing."""
        self.assertIsNone(imports.get_parent_module("some.namespace.that.is.not.real"))

    def test_empty(self):
        """Check that an empty string returns nothing."""
        self.assertIsNone(imports.get_parent_module(""))

    def test_invalid(self):
        """Check that a non-string returns nothing."""
        self.assertIsNone(imports.get_parent_module(None))

    def test_from_nested_class(self):
        """Check that a "class-in-a-class" is still imporable."""
        code = textwrap.dedent(
            """\
            class Something(object):
                class Another(object):
                    pass
            """
        )
        path = os.path.join(tempfile.mkdtemp(), "fake_module.py")

        with io.open(path, "w", encoding="ascii") as handler:
            handler.write(code)

        with wrapping.keep_sys_path():
            sys.path.append(os.path.dirname(path))

            self.assertIsNotNone(
                imports.get_parent_module("fake_module.Something.Another")
            )
