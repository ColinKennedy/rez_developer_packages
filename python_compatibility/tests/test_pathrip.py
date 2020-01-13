#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that everything in the "pathrip.py" module works as expected."""

import unittest

from python_compatibility import pathrip


class Split(unittest.TestCase):
    """Make sure that every directory-splitting operation works as expected."""

    def test_permutations(self):
        """Check every possible path-splitting scenario for every OS."""
        paths = [
            ("", []),
            ("foo", ["foo"]),
            ("foo/", ["foo"]),
            ("foo\\", ["foo\\"]),
            ("/foo", ["/", "foo"]),
            ("\\foo", ["\\foo"]),
            ("foo/bar", ["foo", "bar"]),
            ("/", ["/"]),
            ("c:", ["c:"]),
            ("c:/", ["c:"]),
            ("c:foo", ["c:foo"]),
            ("c:/foo", ["c:", "foo"]),
            ("c:/users/john/foo.txt", ["c:", "users", "john", "foo.txt"]),
            ("/users/john/foo.txt", ["/", "users", "john", "foo.txt"]),
            ("foo/bar/baz/loop", ["foo", "bar", "baz", "loop"]),
            ("foo/bar/baz/", ["foo", "bar", "baz"]),
            ("//hostname/foo/bar.txt", ["//", "hostname", "foo", "bar.txt"]),
        ]

        for text, expected in paths:
            self.assertEqual(expected, pathrip.split_os_path_asunder(text))


class CommonPrefix(unittest.TestCase):
    """Test that :func:`.get_common_prefix` works as-expected."""

    def test_permutations(self):
        """Test every possible type of input to :func:`.get_common_prefix`."""
        all_paths = [
            (["", "", ""], ""),
            (["/something", "", ""], ""),
            (
                [
                    "/something/parts/inner/folder_inside",
                    "/something/parts/inner_folder_with_more_text/folder_inside",
                ],
                "/something/parts",
            ),
            (["/usr/var1/log", "/usr/var2/log"], "/usr"),
            (["/usr/var1/log", "/usr/var2/log/"], "/usr"),
            (["/usr/var1/log/", "/usr/var2/log"], "/usr"),
            (["/usr/var1/log/", "/usr/var2/log/"], "/usr"),
            ([], ""),
        ]

        for paths, expected in all_paths:
            self.assertEqual(expected, pathrip.get_common_prefix(paths))
