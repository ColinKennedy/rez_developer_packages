#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test that :class:`rez_lint.core.message_description.Description` works."""

import os
import unittest

from rez_lint.core import message_description
from rez_lint.plugins.checkers import base_checker


class Description(unittest.TestCase):
    """Test that :class:`rez_lint.core.message_description.Description` formats correctly."""

    def test_empty(self):
        """Creating a description with basically nothing in it should still be valid."""
        message_description.Description(
            [],
            message_description.Location(".", 0, 0, ""),
            base_checker.Code(short_name="", long_name=""),
        )

    def test_summary(self):
        """Make sure description summarizes print as-expected."""
        description = message_description.Description(
            ["Some important message"],
            message_description.Location(".", 0, 0, ""),
            base_checker.Code(short_name="Z", long_name="some-code"),
        )

        self.assertEqual(
            ["Z: 0, 0: Some important message (some-code)"], description.get_message()
        )

    def test_full(self):
        """Make sure description summarizes print as-expected."""
        summary = "Some important message"
        description = message_description.Description(
            [summary],
            message_description.Location(".", 0, 0, ""),
            base_checker.Code(short_name="Z", long_name="some-code"),
            full=[summary, "More information here", "And even more"],
        )

        self.assertEqual(
            [
                "Z: 0, 0: Some important message (some-code)",
                "    More information here",
                "    And even more",
            ],
            description.get_message(verbose=True),
        )


class Header(unittest.TestCase):
    """Make sure the description header is already formatted as expected."""

    def test_empty(self):
        """An empty location should error - there needs to always be some file path."""
        with self.assertRaises(ValueError):
            message_description.Description(
                [],
                message_description.Location("", 0, 0, ""),
                base_checker.Code(short_name="Z", long_name="some-code"),
            )

    def test_relative_001(self):
        """A location that is below the current directory should return relative."""
        description = message_description.Description(
            [],
            message_description.Location(
                os.path.join(os.getcwd(), "something", "else"), 0, 0, ""
            ),
            base_checker.Code(short_name="Z", long_name="some-code"),
        )

        self.assertEqual(os.path.join("something", "else"), description.get_header())

    def test_absolute(self):
        """A location that is next to or above the current directory should return absolute."""
        parent = os.path.dirname(os.getcwd())

        description = message_description.Description(
            [],
            message_description.Location(parent, 0, 0, ""),
            base_checker.Code(short_name="Z", long_name="some-code"),
        )

        self.assertEqual(parent, description.get_header())

    def test_dot(self):
        """A single dot path (e.g. ".") should return the current directory."""
        description = message_description.Description(
            [],
            message_description.Location(".", 0, 0, ""),
            base_checker.Code(short_name="Z", long_name="some-code"),
        )

        self.assertEqual(os.getcwd(), description.get_header())
