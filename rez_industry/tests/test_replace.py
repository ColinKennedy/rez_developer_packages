#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that checks that replacing existing Rez package.py files work as expected.

The module tests this by checking each permutation of the
:func:`rez_industry.api.add_to_attribute` function.

"""

import textwrap
import unittest

import parso
from rez_industry import api
from six.moves import mock


class AddToAttributeHelp(unittest.TestCase):
    """Make sure that :func:`rez_industry.api.add_to_attribute` works for Rez "help"."""

    def _test(self, expected, text, overrides):
        """Check that `overrides` is added to `text` as expected.

        Args:
            expected (str): The output of `text` mixed with `overrides`.
            text (str): The raw Rez package.py input.
            overrides (str or list[list[str, str]]): The data that will append / replace help.

        """
        results = api.add_to_attribute("help", overrides, text)
        self.assertEqual(expected, results)

    def test_empty_001(self):
        """Append should still work, even if help is just an empty string."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = ""
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "another"],
            ]
            """
        )

        self._test(expected, original, [["thing", "another"]])

    def test_empty_002(self):
        """Append should still work, even if help is just an empty list."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = []
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "another"],
            ]
            """
        )

        self._test(expected, original, [["thing", "another"]])

    def test_empty_003(self):
        """Don't add any extries because the override cannot be empty."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = []
            """
        )

        with self.assertRaises(ValueError):
            api.add_to_attribute("help", [], original)

    def test_empty_004(self):
        """Don't add any extries because the override cannot be empty."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = []
            """
        )

        with self.assertRaises(ValueError):
            api.add_to_attribute("help", "", original)

    def test_invalid_001(self):
        """Raise an exception if an invalid help attribute was given."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = []
            """
        )

        with self.assertRaises(ValueError):
            api.add_to_attribute("help", {"foo": "bar"}, original)

    def test_invalid_002(self):
        """Report an issue because you cannot override a list with a string."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["foo", "bar"],
            ]
            """
        )

        with self.assertRaises(ValueError):
            api.add_to_attribute("help", "something", original)

    def test_append_001(self):
        """Add a new entry to an existing list of help items."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "blah"],
            ]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "blah"],
                ["foo", "bar"],
            ]
            """
        )

        self._test(expected, original, [["foo", "bar"]])

    def test_append_002(self):
        """Create a duplicate label entry to an existing list of help items."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "blah"],
            ]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "another"],
            ]
            """
        )

        self._test(expected, original, [["thing", "another"]])

    def test_append_002b_override(self):
        """Fail to add the an existing entry more than once."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["something", "another"],
                ["thing", "foo"],
            ]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["something", "another"],
                ["foo", "bar"],
                ["thing", "blah"],
            ]
            """
        )

        self._test(expected, original, [["foo", "bar"], ["thing", "blah"]])

    def test_append_003(self):
        """Replace a `list()` initialization with a non-empty one."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = list()
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["foo", "bar"],
            ]
            """
        )

        self._test(expected, original, [["foo", "bar"]])

    def test_list_override(self):
        """Replace a label entry of an existing list."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "blah"],
            ]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["thing", "blah"],
                ["thing", "blah"],
            ]
            """
        )

        results = api.add_to_attribute(
            "help", [["thing", "blah"]], original, append=True
        )
        self.assertEqual(expected, results)

    def test_single_line_expand(self):
        """Change a single-line help list into a multiple-line help list."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = [["thing", "blah"], ["foo", "bar"]]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["foo", "bar"],
                ["woo", "blah"],
                ["thing", "another"],
            ]
            """
        )

        self._test(expected, original, [["woo", "blah"], ["thing", "another"]])

    def test_str_to_str(self):
        """Change a single help string into another string."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = "something"
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = "another"
            """
        )

        self._test(expected, original, "another")

    def test_str_to_list(self):
        """Convert a single help string into a list of lists, while inserting a new entry."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = "something"
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["Home Page", "something"],
                ["thing", "another"],
            ]
            """
        )

        self._test(expected, original, [["thing", "another"]])

    def test_append_position_001(self):
        """Place `help` at the end of the package.py file, if needed."""
        original = textwrap.dedent(
            """\
            name = "foo"
            """
        )

        overrides = [["README", "README.md"]]

        expected = textwrap.dedent(
            """\
            name = "foo"

            help = [
                ["README", "README.md"],
            ]"""
        )

        self._test(expected, original, overrides)

    def test_append_position_002(self):
        """Place `help` at the end of the package.py file, if needed."""
        original = 'name = "foo"'
        overrides = [["README", "README.md"]]

        expected = textwrap.dedent(
            """\
            name = "foo"

            help = [
                ["README", "README.md"],
            ]"""
        )

        self._test(expected, original, overrides)

    def test_between_position(self):
        """Place `help` immediately before `requires`, if it exists."""
        original = textwrap.dedent(
            """\
            name = "foo"

            build_requires = [
                "something",
            ]
            """
        )

        overrides = [["README", "README.md"]]

        expected = textwrap.dedent(
            """\
            name = "foo"

            help = [
                ["README", "README.md"],
            ]

            build_requires = [
                "something",
            ]
            """
        )

        self._test(expected, original, overrides)

    def test_between_partial_position(self):
        """Place `help` in as-correct of a position as possible when attributes are missing."""
        original = textwrap.dedent(
            """\
            name = "foo"

            version = "1.0.0"

            description = "Some important information here."

            authors = [
                "Someone",
            ]

            requires = [
                "another",
            ]

            def commands():
                pass
            """
        )

        overrides = [["README", "README.md"]]

        expected = textwrap.dedent(
            """\
            name = "foo"

            version = "1.0.0"

            description = "Some important information here."

            authors = [
                "Someone",
            ]

            help = [
                ["README", "README.md"],
            ]

            requires = [
                "another",
            ]

            def commands():
                pass
            """
        )

        self._test(expected, original, overrides)


class AddToAttributeHelpFunction(unittest.TestCase):
    """A variation of :class:`AddToAttributeHelp` which tests @early functions."""

    def _test(self, expected, text, overrides):
        """Check that `overrides` is added to `text` as expected.

        Args:
            expected (str): The output of `text` mixed with `overrides`.
            text (str): The raw Rez package.py input.
            overrides (str or list[list[str, str]]): The data that will append / replace help.

        """
        results = api.add_to_attribute("help", overrides, text)
        self.assertEqual(expected, results)

    def test_append(self):
        """Add the @early() help function to a package definition which doesn't have one."""
        original = 'name = "whatever"'

        code_block = textwrap.dedent(
            """
            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
            """
        )

        self._test(expected, original, parso.parse(code_block))

    def test_simple(self):
        """Make sure @early() help attribute works."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            help = [
                ["Some Existing", "stuff"],
            ]
            """
        )

        code_block = textwrap.dedent(
            """
            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
            """
        )

        self._test(expected, original, parso.parse(code_block))

    def test_format_001(self):
        """Make sure Python formatting works within an @early() function."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            version = "1.0.0"

            help = "stuff"
            """
        )

        code_block = textwrap.dedent(
            """
            @early()
            def help():
                return [["documentation", "foo.{this.major}.{this.minor}".format(this=this)]]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            version = "1.0.0"

            @early()
            def help():
                return [["documentation", "foo.{this.major}.{this.minor}".format(this=this)]]
            """
        )

        self._test(expected, original, parso.parse(code_block))

    def test_format_002(self):
        """Do both types of Python formatting and make sure they work."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            version = "1.0.0"

            help = "stuff"
            """
        )

        code_block = textwrap.dedent(
            """
            @early()
            def help():
                return [
                    ["documentation", "foo.{this.major}.{this.minor}".format(this=this)],
                    ["foo", "foo.%s.%s", (this.major, this.minor)],
                ]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            version = "1.0.0"

            @early()
            def help():
                return [
                    ["documentation", "foo.{this.major}.{this.minor}".format(this=this)],
                    ["foo", "foo.%s.%s", (this.major, this.minor)],
                ]
            """
        )

        self._test(expected, original, parso.parse(code_block))


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

            tests = {
                "thing": {
                    "command": "thing",
                    "run_on": "explicit",
                },
            }

            private_build_requires = [
                "cmake",
            ]

            def commands():
                pass
            """
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

            tests = {
                "thing": {
                    "command": "thing",
                    "run_on": "explicit",
                },
            }

            def commands():
                pass
            """
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
