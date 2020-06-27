#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that checks that replacing existing Rez package.py files work as expected.

The module tests this by checking each permutation of the
:func:`rez_industry.api.add_to_attribute` function.

"""

import textwrap
import unittest

from rez_industry import api
from six.moves import mock


class AddToAttributeRequires(unittest.TestCase):
    """Make sure that :func:`rez_industry.api.add_to_attribute` works for Rez "requires"."""

    def _test(self, expected, text, overrides, remove=False):
        """Run a test and check if it makes the expected results.

        Args:
            expected (str): The output of `text` mixed with `overrides`.
            text (str): The raw Rez package.py input.
            overrides (list[str], optional): The data that will
                append / remove / replace requires.
                e.g. "some_package-2+<3".
            remove (bool, optional): If True, the attribute is removed,
                not added. If False, `overrides` are added. Default is False.

        """
        if remove:
            api.remove_from_attribute("requires", overrides, text)

            return

        results = api.add_to_attribute("requires", overrides, text)
        self.assertEqual(expected, results)

    def test_empty_001(self):
        """Replace an empty list [] with a new requirement."""
        original = textwrap.dedent(
            """\
            name = "some_package"

            requires = []
            """
        )
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "new_requirement-2+<3",
            ]
            """
        )
        overrides = ["new_requirement-2+<3"]

        self._test(expected, original, overrides)

    def test_empty_002(self):
        """Replace an empty list [] with a new requirement."""
        original = textwrap.dedent(
            """\
            name = "some_package"

            requires = list()
            """
        )
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "new_requirement-2+<3",
            ]
            """
        )
        overrides = ["new_requirement-2+<3"]

        self._test(expected, original, overrides)

    def test_undefined(self):
        """Add the `requires` attribute since it does not already exist."""
        original = 'name = "some_package"'
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "new_requirement-2+<3",
            ]"""
        )
        overrides = ["new_requirement-2+<3"]

        self._test(expected, original, overrides)

    def test_add_requirement(self):
        """Add a completely new requirement to a list of requirements."""
        original = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement",
                    "another_requirement-2",
                "z_requirement_end-3+<4",
            ]
            """
        )
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement",
                    "another_requirement-2",
                "something_else==1.0.0",
                "z_requirement_end-3+<4",
            ]
            """
        )
        overrides = ["something_else==1.0.0"]

        self._test(expected, original, overrides)

    def test_remove_requirement(self):
        """Remove a requirement completely from the list of requirements."""
        original = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement",
                "another_one-2",
                "some_requirement_to_remove-2",
                "z_requirement_end-3+<4",
            ]
            """
        )
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement",
                "another_one-2",
                "z_requirement_end-3+<4",
            ]
            """
        )
        overrides = ["some_requirement_to_remove"]

        self._test(expected, original, overrides, remove=True)

    def test_replace_requirement_001(self):
        """Change the version information of an existing requirement."""
        original = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement-2",
                "another_requirement",
                "z_requirement_end-3+<4",
            ]
            """
        )
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement-2",
                "another_requirement==1.0.0",
                "z_requirement_end-3+<4",
            ]
            """
        )
        overrides = ["another_requirement==1.0.0"]

        self._test(expected, original, overrides)

        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement-2",
                "another_requirement-1+<2",
                "z_requirement_end-3+<4",
            ]
            """
        )
        overrides = ["another_requirement-1+<2"]

        self._test(expected, original, overrides)

    def test_replace_requirement_002(self):
        """Change the version information of an existing requirement."""
        original = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement-2",
                "another_requirement-2",
                "z_requirement_end-3+<4",
            ]
            """
        )
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement-2",
                "another_requirement==1.0.0",
                "z_requirement_end-3+<4",
            ]
            """
        )
        overrides = ["another_requirement==1.0.0"]

        self._test(expected, original, overrides)

        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "a_requirement-2",
                "another_requirement-1+<2",
                "z_requirement_end-3+<4",
            ]
            """
        )
        overrides = ["another_requirement-1+<2"]

        self._test(expected, original, overrides)

    def test_invalid(self):
        """Raise an exception if an invalid type or invalid input is given to `requires`."""
        text = 'name = "some_package"'
        overrides = None

        with self.assertRaises(ValueError):
            api.add_to_attribute("requires", overrides, text)

        overrides = []

        with self.assertRaises(ValueError):
            api.add_to_attribute("requires", overrides, text)

    def test_single_quotes_bug(self):
        """Fix an issue where Rez raises a syntax error when ''s are used."""
        original = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "another_requirement-2",
                'some_requirement-3.1.2.24+<4',
            ]
            """
        )
        expected = textwrap.dedent(
            """\
            name = "some_package"

            requires = [
                "another_requirement==1.0.0",
                'some_requirement-3.1.2.24+<4',
            ]
            """
        )
        overrides = ["another_requirement==1.0.0"]

        self._test(expected, original, overrides)


class AddToAttributeTests(unittest.TestCase):
    """Make sure that :func:`rez_industry.api.add_to_attribute` works for Rez "tests"."""

    def _test(self, expected, text, overrides):
        results = api.add_to_attribute("tests", overrides, text)
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
            "foo": {"command": "another thing", "requires": ["blah-1"]},
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
        """Add entries to an existing but empty "tests" attribute."""
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
            "another": {"command": "more", "requires": ["information"]},
            "bar": {"command": "thing", "requires": ["whatever-1"]},
            "foo": "thing",
            "second_thing": {"command": "and more", "requires": ["information"]},
        }

        self._test(expected, original, overrides)

    def test_empty_002(self):
        """Don't add any extries because `overrides` cannot be empty."""
        textwrap.dedent(
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

    def test_empty_003(self):
        """Add entries to an existing but empty "tests" attribute."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            tests = dict()
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
            "another": {"command": "more", "requires": ["information"]},
            "bar": {"command": "thing", "requires": ["whatever-1"]},
            "foo": "thing",
            "second_thing": {"command": "and more", "requires": ["information"]},
        }

        self._test(expected, original, overrides)

    def test_undefined(self):
        """Add a new assignment for "tests" if it doesn't already exist."""
        original = "name = 'thing'"
        overrides = {
            "another": {"command": "more", "requires": ["information"]},
            "bar": {"command": "thing", "requires": ["whatever-1"]},
            "foo": "thing",
            "second_thing": {"command": "and more", "requires": ["information"]},
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
        original = ""
        overrides = "something that is not a dict"

        with self.assertRaises(ValueError):
            api.add_to_attribute("tests", overrides, original)

    def test_single_line_expand(self):
        """Split a single-line definition of "tests" into multiple lines."""
        original = textwrap.dedent(
            """\
            name = 'thing'

            tests = {"foo": "bar", "another_test": {"command": "blah"}}
            """
        )
        overrides = {
            "another": {"command": "more", "requires": ["information"]},
            "bar": {"command": "thing", "requires": ["whatever-1"]},
            "foo": "thing",
            "second_thing": {"command": "and more", "requires": ["information"]},
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

    def test_replace_str_with_dict(self):
        """Change a str value into a dict value."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            tests = {
                "foo": "bar",
            }
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            tests = {
                "foo": {
                    "command": "more",
                    "requires": ["information"],
                },
            }
            """
        )
        overrides = {"foo": {"command": "more", "requires": ["information"]}}

        self._test(expected, original, overrides)

    def test_append_position(self):
        """Place `tests` at the end of the package.py file, if needed."""
        original = textwrap.dedent(
            """\
            name = "foo"
            """
        )

        overrides = {"thing": {"command": "thing", "run_on": "explicit"}}

        expected = textwrap.dedent(
            """\
            name = "foo"

            tests = {
                "thing": {
                    "command": "thing",
                    "run_on": "explicit",
                },
            }"""
        )

        self._test(expected, original, overrides)

    def test_between_position(self):
        """Place `tests` immediately before `private_build_requires`, if it exists."""
        original = textwrap.dedent(
            """\
            name = "foo"

            requires = [
                "something",
            ]

            private_build_requires = [
                "cmake",
            ]

            def commands():
                pass
            """
        )

        overrides = {"thing": {"command": "thing", "run_on": "explicit"}}

        expected = textwrap.dedent(
            """\
            name = "foo"

            requires = [
                "something",
            ]

            private_build_requires = [
                "cmake",
            ]

            def commands():
                pass


            tests = {
                "thing": {
                    "command": "thing",
                    "run_on": "explicit",
                },
            }"""
        )

        self._test(expected, original, overrides)

    def test_between_partial_position(self):
        """Place `tests` in as-correct of a position as possible when attributes are missing."""
        original = textwrap.dedent(
            """\
            name = "foo"

            def commands():
                pass
            """
        )

        overrides = {"thing": {"command": "thing", "run_on": "explicit"}}

        expected = textwrap.dedent(
            """\
            name = "foo"

            def commands():
                pass


            tests = {
                "thing": {
                    "command": "thing",
                    "run_on": "explicit",
                },
            }"""
        )

        self._test(expected, original, overrides)


class Types(unittest.TestCase):
    """Make sure expected types serialize correctly."""

    def _test(self, expected, text, overrides):
        """Check that `overrides` is added to `text` as expected.

        Args:
            expected (str): The output of `text` mixed with `overrides`.
            text (str): The raw Rez package.py input.
            overrides (object): The data that will append / replace tests.

        """
        results = api.add_to_attribute("tests", overrides, text)
        self.assertEqual(expected, results)

    @mock.patch(
        "rez_industry.core.adapters.tests_adapter.TestsAdapter.check_if_invalid"
    )
    def test_null(self, check_if_invalid):
        """Make sure None is serialized as None."""
        check_if_invalid.return_value = ""

        original = textwrap.dedent(
            """\
            name = 'thing'

            tests = {"foo": "bar", "another_test": {"command": "blah"}}
            """
        )
        overrides = {"foo": {"blah": None}}

        expected = textwrap.dedent(
            """\
            name = 'thing'

            tests = {
                "another_test": {
                    "command": "blah",
                },
                "foo": {
                    "blah": None,
                },
            }
            """
        )

        self._test(expected, original, overrides)

    @mock.patch(
        "rez_industry.core.adapters.tests_adapter.TestsAdapter.check_if_invalid"
    )
    def test_boolean(self, check_if_invalid):
        """Test that True/False are serialized correctly."""
        check_if_invalid.return_value = ""

        original = textwrap.dedent(
            """\
            name = 'thing'

            tests = {"foo": "bar", "another_test": {"command": "blah"}}
            """
        )
        overrides = {"foo": {"thing": False, "another": True}}

        expected = textwrap.dedent(
            """\
            name = 'thing'

            tests = {
                "another_test": {
                    "command": "blah",
                },
                "foo": {
                    "another": True,
                    "thing": False,
                },
            }
            """
        )

        self._test(expected, original, overrides)
