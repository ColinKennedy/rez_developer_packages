#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO : Add tests that have SURROUNDING nodes, not just the nodes by themselves

"""Test that the :class:`.NeedsComment` class works as expected."""

import textwrap
import unittest

import parso
from rez_lint.plugins.checkers import explains_comment


class _Common(unittest.TestCase):
    """A basic class that will test :class:`.NeedsComment`."""

    def _test(self, expected, code):
        """Parse some Python code and compare it with an expected result.

        Args:
            expected (dict[str, str]): The output that `code` should be transformed into.
            code (str): The raw Python code to test with.

        """
        graph = parso.parse(code)

        pairs = explains_comment.NeedsComment._get_comment_pairs(  # pylint: disable=protected-access
            graph
        )

        self.assertEqual(expected, pairs)


class Layouts(_Common):
    """Test that parsing a users's package.py works as expected."""

    def test_empty(self):
        """Make sure that the checker does not report an issue when there's no `requires`."""
        code = textwrap.dedent(
            """\
            requires = []

            """
        )

        self._test(dict(), code)

    def test_ender(self):
        """Make sure that the checker does not accidentally add ending comments."""
        code = textwrap.dedent(
            """\
            requires = [
                "foo",
            ]  # ending comment here

            """
        )

        self._test({"foo": ""}, code)

    def test_full(self):
        """A basic test that has multiple dependencies, each with their own comment."""
        code = textwrap.dedent(
            """\
            requires = [
                "foo",  # ending comment here
                "bar",  # another comment here
                "thing",  # more!
            ]

            """
        )

        self._test(
            {
                "foo": "ending comment here",
                "bar": "another comment here",
                "thing": "more!",
            },
            code,
        )

    def test_inline(self):
        """Test that comments on the same line works."""
        code = textwrap.dedent(
            """\
            requires = [
                "foo-1+<2",  # something
            ]

            """
        )

        self._test({"foo-1+<2": "something"}, code)

    def test_multi_line_001(self):
        """Check that lines can be added above the requirement that they describe."""
        code = textwrap.dedent(
            """\
            requires = [
                # Some multi-line comment that is actually just a single line
                "foo-1+<2",
            ]

            """
        )

        self._test(
            {"foo-1+<2": "Some multi-line comment that is actually just a single line"},
            code,
        )

    def test_multi_line_002(self):
        """Check that lines can be added above the requirement that they describe."""
        code = textwrap.dedent(
            """\
            requires = [
                # Some multi-line comment
                # that is more than one line
                #
                "foo-1+<2",
            ]

            """
        )

        self._test(
            {"foo-1+<2": "Some multi-line comment that is more than one line"}, code,
        )

    def test_multi_line_003(self):
        """Check that lines can be added above the requirement that they describe."""
        code = textwrap.dedent(
            """\
            requires = [
                # Some multi-line comment
                #     that has indentation
                #
                "foo-1+<2",
            ]

            """
        )

        self._test(
            {"foo-1+<2": "Some multi-line comment     that has indentation"}, code,
        )

    def test_multi_line_004(self):
        """Check that lines can be added above the requirement that they describe."""
        code = textwrap.dedent(
            """\
            requires = [
                # Some multi-line comment
                #
                # that is more than one line
                #
                "foo-1+<2",
            ]

            """
        )

        self._test(
            {"foo-1+<2": "Some multi-line comment\nthat is more than one line"}, code,
        )

    def test_multi_line_005(self):
        """Check that lines can be added above the requirement that they describe."""
        code = textwrap.dedent(
            """\
            requires = [
                # Some multi-line comment that is actually just a single line
                "foo-1+<2",
            ]

            """
        )

        self._test(
            {"foo-1+<2": "Some multi-line comment that is actually just a single line"},
            code,
        )

    def test_over_line(self):
        """Check that lines written below a package apply to the next requirement underneath."""
        code = textwrap.dedent(
            """\
            requires = [
                "foo-1+<2",
                       # something
                "bar",
            ]

            """
        )

        self._test({"foo-1+<2": "", "bar": "something"}, code)

    def test_under_line(self):
        """If the user has weird formatting, make sure it doesn't break the parser."""
        code = textwrap.dedent(
            """\
            requires = [
                "foo-1+<2"
                       # something
                    ,
                "bar",
            ]

            """
        )

        self._test({"foo-1+<2": "something", "bar": ""}, code)


class Oops(_Common):
    """Test edge cases to make sure unexpected failures don't occur."""

    def test_inline(self):
        """An in-line comment with multiple # markers should still parse correctly."""
        code = textwrap.dedent(
            """\
            requires = [
                "foo-1+<2",  #  # # something
            ]

            """
        )

        self._test({"foo-1+<2": "something"}, code)

    def test_multi_line_001(self):
        """A multi-line comment with multiple # markers should still parse correctly."""
        code = textwrap.dedent(
            """\
            requires = [
                # ### Some lines here
                # # and more lines
                #
                "foo-1+<2",
            ]

            """
        )

        self._test({"foo-1+<2": "Some lines here and more lines"}, code)
