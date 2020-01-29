#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import tempfile
import textwrap
import unittest

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

    def test_complex(self):
        """Partially override one key and completely replace another."""
        original = textwrap.dedent(
            """\
            name = "foo"

            tests = {
                "another": {
                    "command": "more",
                    "requires": ["information"],
                },
                "bar": {
                    "command": "another",
                    "requires": ["something"],
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
            "bar": {"command": "thing", "run_on": "explicit"},
            "foo": {"command": "another thing", "requires": ["blah-1"],},
        }

        expected = textwrap.dedent(
            """\
            name = "foo"

            tests = {
                "another": {
                    "command": "more",
                    "requires": ["information"],
                },
                "bar": {
                    "command": "thing",
                    "requires": ["something"],
                    "run_on": "explicit",
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
            api.add_to_attribute("tests", overrides, " ")

    # TODO : Hopefully we'll not need this unittest once parso is fully implemented
    def test_empty_003(self):
        overrides = {"thing": "asdf"}

        with self.assertRaises(ValueError):
            api.add_to_attribute("tests", overrides, " ")

    def test_undefined(self):
        original = "name = 'thing'"
        overrides = {
            "another": {"command": "more", "requires": ["information"],},
            "bar": {"command": "thing", "requires": ["whatever-1"],},
            "foo": "thing",
            "second_thing": {"command": "and more", "requires": ["information"],},
        }

        expected = textwrap.dedent(
            """\
            name = 'thing'

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
            }"""
        )

        self._test(expected, original, overrides)

    def test_invalid(self):
        """If `overrides` is not a dict, raise an exception."""
        original = os.path.join(tempfile.mkdtemp(suffix="_invalid"), "package.py")
        open(
            original, "a"
        ).close()  # TODO : Remove the need for this later once `parso` support is complete
        overrides = "something that is not a dict"

        with self.assertRaises(ValueError):
            api.add_to_attribute("tests", overrides, original)

    def test_single_line_expand(self):
        original = textwrap.dedent(
            """\
            name = 'thing'

            tests = {"foo": "bar", "another_test": {"command": "blah"}}
            """
        )
        overrides = {
            "another": {"command": "more", "requires": ["information"],},
            "bar": {"command": "thing", "requires": ["whatever-1"],},
            "foo": "thing",
            "second_thing": {"command": "and more", "requires": ["information"],},
        }

        expected = textwrap.dedent(
            """\
            name = 'thing'

            tests = {
                "another": {
                    "command": "more",
                    "requires": ["information"],
                },
                "another_test": {
                    "command": "blah",
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

        self._test(expected, original, overrides)
