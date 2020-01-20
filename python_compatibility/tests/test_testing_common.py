#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test anything in testing/common.py."""

import os
import tempfile

from python_compatibility.testing import common


class FileMaker(common.Common):
    """Test the :func:`python_compatibility.testing.common.make_files` function."""

    def test_empty(self):
        """Don't create anything but still run."""
        root = tempfile.mkdtemp(suffix="_the_empty_root")
        self.add_item(root)
        common.make_files({}, root)

        self.assertEqual([], os.listdir(root))

    def test_make_files(self):
        """Create some files."""
        root = tempfile.mkdtemp(suffix="_the_single_files")
        self.add_item(root)
        files = {"foo.txt", "another.md", "no_extension"}
        common.make_files({name: None for name in files}, root)

        self.assertEqual(files, set(os.listdir(root)))
        self.assertTrue(
            all({os.path.isfile(os.path.join(root, name)) for name in files}),
        )

    def test_make_nested(self):
        """Create a nested set of files and folders."""
        root = tempfile.mkdtemp(suffix="_the_single_files")
        self.add_item(root)

        common.make_files(
            {"foo": {"another.py": None, "thing": {"blah.py": None}}}, root
        )

        self.assertEqual({"foo"}, set(os.listdir(root)))
        self.assertEqual(
            {"another.py", "thing"}, set(os.listdir(os.path.join(root, "foo")))
        )
        self.assertEqual(
            {"blah.py",}, set(os.listdir(os.path.join(root, "foo", "thing")))
        )

        self.assertTrue(all({os.path.isdir(os.path.join(root, "foo"))}))
        self.assertTrue(all({os.path.isfile(os.path.join(root, "foo", "another.py"))}))
        self.assertTrue(all({os.path.isdir(os.path.join(root, "foo", "thing"))}))
        self.assertTrue(
            all({os.path.isfile(os.path.join(root, "foo", "thing", "blah.py"))})
        )
