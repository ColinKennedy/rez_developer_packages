#!/usr/bin/env python
# -*- coding: utf-8 -*-


import textwrap
import unittest

from rez_industry import api


# class TestAddToAttributeHelp(unittest.TestCase):
#     pass
#     str to list of list of strs


class TestAddToAttributeTests(unittest.TestCase):
    def _test(self, expected, text, overrides):
        results = api.add_to_attribute("tests", overrides, text)
        self.assertEqual(expected, results)

    def test_contents_overwrite(self):
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

        overrides = {
            "bar": {
                "requires": ["whatever-2+<3"],
            },
            "foo": {
                "command": "another thing",
                "requires": ["blah-1"],
            },
        }

        expected = textwrap.dedent(
            """\
            tests = {
                "another": {
                    "command": "more",
                    "requires": ["information"],
                },
                "bar": {
                    "command": "thing",
                    "requires": ["whatever-2+<3"],
                },
                "foo": {
                    "command": "another thing",
                    "requires": ["blah-1"],
                },
                "second_thing": {
                    "command": "and more",
                    "requires": ["information"],
                },
            }
            """
        )

        self._test(expected, original, overrides)

    # TODO : Finish these
    # def test_empty(self):
    #     pass
    #
    # def test_undefined(self):
    #     # Declare it (since it doesn't already exist)
    #     pass
    #
    # def test_existing_key(self):
    #     # overwrite
    #     pass
    #
    # def test_invalid(self):
    #     pass
    #
    # def test_single_expand(self):
    #     pass
    #
    # def test_multiple_line_overwrite(self):
    #     pass
