#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that everything in the "pathrip.py" module works as expected."""

import platform
import unittest

from python_compatibility import pathrip

_SYSTEM = platform.system()
_IS_NOT_WINDOWS = _SYSTEM != "Windows"
_IS_NOT_LINUX = _SYSTEM != "Linux"


class Split(unittest.TestCase):
    """Make sure that every directory-splitting operation works as expected."""

    @unittest.skipIf(_IS_NOT_LINUX, "This test requires Linux")
    def test_permutations_linux(self):
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

    @unittest.skipIf(_IS_NOT_LINUX, "This test requires Linux / UNIX systems")
    def test_permutations_linux(self):
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

    @unittest.skipIf(_IS_NOT_WINDOWS, "This test requires Windows")
    def test_permutations_windows(self):
        """Test every possible type of input to :func:`.get_common_prefix`."""
        all_paths = [
            (["", "", ""], ""),
            ([r"C:\something", "", ""], ""),
            (
                [
                    r"C:\something\parts\inner\folder_inside",
                    r"C:\something\parts\inner_folder_with_more_text\folder_inside",
                ],
                r"C:\something\parts",
            ),
            ([r"C:\usr\var1\log", r"C:\usr\var2\log"], r"C:\usr"),
            ([r"C:\usr\var1\log", r"C:\usr\var2\log\\"], r"C:\usr"),
            ([r"C:\usr\var1\log\\", r"C:\usr\var2\log"], r"C:\usr"),
            ([r"C:\usr\var1\log\\", r"C:\usr\var2\log\\"], r"C:\usr"),
            ([], ""),
        ]

        for paths, expected in all_paths:
            self.assertEqual(expected, pathrip.get_common_prefix(paths))
