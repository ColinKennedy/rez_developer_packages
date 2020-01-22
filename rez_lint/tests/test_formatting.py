#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test that :class:`rez_lint.core.message_description.Description` formats correctly."""

import unittest

from rez_lint.plugins.checkers import base_checker
from rez_lint.core import message_description


class Description(unittest.TestCase):
    """Test that :class:`rez_lint.core.message_description.Description` formats correctly."""

    def test_empty(self):
        """Creating a description with basically nothing in it should still be valid."""
        message_description.Description(
            [],
            message_description.Location("", 0, 0, ""),
            base_checker.Code(short_name="", long_name=""),
        )

    def test_summary(self):
        """Make sure description summarizes print as-expected."""
        description = message_description.Description(
            ["Some important message"],
            message_description.Location("", 0, 0, ""),
            base_checker.Code(short_name="Z", long_name="some-code"),
        )

        self.assertEqual(['Z: 0, 0: Some important message (some-code)'], description.get_message())

    def test_full(self):
        """Make sure description summarizes print as-expected."""
        summary = "Some important message"
        description = message_description.Description(
            [summary],
            message_description.Location("", 0, 0, ""),
            base_checker.Code(short_name="Z", long_name="some-code"),
            full=[summary, "More information here", "And even more"],
        )

        self.assertEqual(
            [
                'Z: 0, 0: Some important message (some-code)',
                "    More information here",
                "    And even more",
            ],
            description.get_message(verbose=True),
        )
