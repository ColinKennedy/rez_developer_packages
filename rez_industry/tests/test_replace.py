#!/usr/bin/env python
# -*- coding: utf-8 -*-


import textwrap
import unittest
import tempfile
import os

from python_compatibility.testing import common

from rez_industry import api

# class TestAddToAttributeHelp(unittest.TestCase):
#     pass
#     str to list of list of strs


class TestAddToAttributeTests(common.Common):
    def _test(self, expected, text, overrides):
        # TODO : Remove this code + delete_item_later once parso is fully supported
        directory = tempfile.mkdtemp(suffix="_temporary_location")
        self.delete_item_later(directory)

        package_file = os.path.join(directory, "package.py")

        with open(package_file, "w") as handler:
            handler.write(text)

        results = api.add_to_attribute("tests", overrides, package_file)

        self.assertEqual(expected, results)

    # def test_complex(self):
    #     """Partially override one key and completely replace another."""
    #     original = textwrap.dedent(
    #         """\
    #         tests = {
    #             "another": {
    #                 "command": "more",
    #                 "requires": ["information"],
    #             },
    #             "bar": {
    #                 "command": "thing",
    #                 "requires": ["whatever-1"],
    #             },
    #             "foo": "thing",
    #             "second_thing": {
    #                 "command": "and more",
    #                 "requires": ["information"],
    #             },
    #         }
    #         """
    #     )
    #     original = textwrap.dedent(
    #         """\
    #         foo = {
    #             "thing": {
    #                 "requires": [],
    #             },
    #         }
    #         """
    #     )
    #
    #     overrides = {
    #         "bar": {"requires": ["whatever-2+<3"],},
    #         "foo": {"command": "another thing", "requires": ["blah-1"],},
    #     }
    #
    #     expected = textwrap.dedent(
    #         """\
    #         tests = {
    #             "another": {
    #                 "command": "more",
    #                 "requires": ["information"],
    #             },
    #             "bar": {
    #                 "command": "thing",
    #                 "requires": ["whatever-2+<3"],
    #             },
    #             "foo": {
    #                 "command": "another thing",
    #                 "requires": ["blah-1"],
    #             },
    #             "second_thing": {
    #                 "command": "and more",
    #                 "requires": ["information"],
    #             },
    #         }
    #         """
    #     )
    #
    #     self._test(expected, original, overrides)

    def test_empty_001(self):
        original = textwrap.dedent(
            """\
            name = "whatever"

            tests = {}
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            tests = {
                "another": {
                    "command": "more",
                    "requires": ["information"],
                },
                "bar": {
                    "command": "thing",
                    "requires": ["whatever-1"],
                },
                "foo": "thing",
                "second_thing": {
                    "command": "and more",
                    "requires": ["information"],
                },
            }
            """
        )
        overrides = {
            "another": {"command": "more", "requires": ["information"],},
            "bar": {"command": "thing", "requires": ["whatever-1"],},
            "foo": "thing",
            "second_thing": {"command": "and more", "requires": ["information"],},
        }

        self._test(expected, original, overrides)

    def test_empty_002(self):
        original = textwrap.dedent(
            """\
            tests = {
                "another": {
                    "command": "more",
                    "requires": ["information"],
                },
                "bar": {
                    "command": "thing",
                    "requires": ["whatever-1"],
                },
                "foo": "thing",
                "second_thing": {
                    "command": "and more",
                    "requires": ["information"],
                },
            }
            """
        )

        overrides = {}

        with self.assertRaises(ValueError):
            api.add_to_attribute("tests", overrides, "foo = 'bar'")

    # def test_undefined(self):
    #     original = ""
    #     overrides = {
    #         "another": {"command": "more", "requires": ["information"],},
    #         "bar": {"command": "thing", "requires": ["whatever-1"],},
    #         "foo": "thing",
    #         "second_thing": {"command": "and more", "requires": ["information"],},
    #     }
    #
    #     textwrap.dedent(
    #         """\
    #         tests = {
    #             "another": {
    #                 "command": "more",
    #                 "requires": ["information"],
    #             },
    #             "bar": {
    #                 "command": "thing",
    #                 "requires": ["whatever-1"],
    #             },
    #             "foo": "thing",
    #             "second_thing": {
    #                 "command": "and more",
    #                 "requires": ["information"],
    #             },
    #         }
    #         """)
    #
    #     self._test(expected, original, overrides)
    #
    # def test_invalid(self):
    #     """If `overrides` is not a dict, raise an exception."""
    #     original = ""
    #     overrides = "something that is not a dict"
    #
    #     with self.assertRaises(ValueError):
    #         api.add_to_attribute("tests", overrides, original)
    #
    # def test_single_expand(self):
    #     pass
    #
    # def test_multiple_line_overwrite(self):
    #     pass


# TODO : Shamelessly copied. Might be worth an extra Rez package?
def _iter_nested_children(node, seen=None):
    """Find every child node of the given `node`, recursively.

    Args:
        node (:class:`parso.python.tree.PythonBaseNode`):
            The node to get children of.
        seen (set[:class:`parso.python.tree.PythonBaseNode`]):
            The nodes that have already been checked.

    Yields:
        :class:`parso.python.tree.PythonBaseNode`: The found children.

    """
    if not seen:
        seen = set()

    if not hasattr(node, "children"):
        yield
        return

    for child in node.children:
        if child not in seen:
            seen.add(child)

            yield child

            for subchild in _iter_nested_children(child):
                yield subchild
