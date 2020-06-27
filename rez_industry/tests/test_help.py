#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests for :mod:`rez_industry.core.adapter.help_adapter`."""

import textwrap
import unittest

import parso
from rez_industry import api


class Add(unittest.TestCase):
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

            build_requires = [
                "something",
            ]

            help = [
                ["README", "README.md"],
            ]"""
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

            requires = [
                "another",
            ]

            def commands():
                pass


            help = [
                ["README", "README.md"],
            ]"""
        )

        self._test(expected, original, overrides)


class Function(unittest.TestCase):
    """A variation of :class:`Add` which tests @early functions."""

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

    def test_replace_different_001(self):
        """Change a help function into a different help function."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
            """
        )

        code_block = textwrap.dedent(
            """
            @early()
            def help():
                import foo

                return [["foo", "bar.{blah}".format(blah=blah)],
                    ["Some Existing", "stuff"]]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            @early()
            def help():
                import foo

                return [["foo", "bar.{blah}".format(blah=blah)],
                    ["Some Existing", "stuff"]]
            """
        )

        self._test(expected, original, parso.parse(code_block))

    def test_replace_different_002(self):
        """Change a help function into a help string."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
            """
        )

        code_block = textwrap.dedent(
            """
            help = "asdfasfd"
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = "asdfasfd"
            """
        )

        self._test(expected, original, parso.parse(code_block))

    def test_replace_different_003(self):
        """Change a help function into a help list."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
            """
        )

        code_block = textwrap.dedent(
            """
            help = [["TTT", "foo bar"]]
            """
        )

        expected = textwrap.dedent(
            """\
            name = "whatever"

            help = [["TTT", "foo bar"]]
            """
        )

        self._test(expected, original, parso.parse(code_block))

    def test_replace_itself(self):
        """Replace a help function with itself."""
        original = textwrap.dedent(
            """\
            name = "whatever"

            @early()
            def help():
                return [["foo", "bar"], ["Some Existing", "stuff"]]
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
