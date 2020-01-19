#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import textwrap
import unittest

from python_compatibility.testing import common
from rez import packages_
from rez_utilities import url_help

_DEFAULT_HELP = object()


class Url(common.Common):
    """Check that different package help URLs settings all raise exceptions correctly."""

    def _test(self, code):
        """Get invalid URLs for the given Rez package code.

        Args:
            code (str):
                Python code that defines a valid Rez package.

        Returns:
            set[tuple[int, str, str]]:
                The position, help command label, and URL for each invalid URL found.

        """
        folder = tempfile.mkdtemp()

        with open(os.path.join(folder, "package.py"), "w") as handler:
            handler.write(code)

        self.add_item(folder)
        package = packages_.get_developer_package(folder)

        return set(name for _, name, _ in url_help.get_invalid_help_urls(package))

    def test_empty_001(self):
        """Check that setting help to `None` works."""
        self.assertFalse(self._test(_make_fake_package(help_text=None)))

    def test_empty_002(self):
        """Check that setting help to `[]` works."""
        self.assertFalse(self._test(_make_fake_package(help_text=[])))

    def test_empty_003(self):
        """Check that a (completely) missing help variable works."""
        self.assertFalse(self._test(_make_fake_package()))

    @unittest.skipIf(
        not url_help.is_url_reachable("https://google.com"),
        "This test will fail but it actually should pass",
    )
    def test_no_errors(self):
        """Check that the tool does not error when we expect it pass."""
        self.assertFalse(
            self._test(_make_fake_package([["home-page", "https://google.com"]]))
        )

    @unittest.skipIf(
        url_help.is_url_reachable("https://website_that_does_not_exist.com"),
        "The URL must not exist, otherwise this test will fail.",
    )
    def test_one_error(self):
        """Check that the tool contains a single error."""
        results = self._test(
            _make_fake_package([["url", "https://website_that_does_not_exist.com"]])
        )

        self.assertEqual({"url"}, results)

    @unittest.skipIf(
        all(
            [
                url_help.is_url_reachable("https://website_missing_here.gov"),
                url_help.is_url_reachable("https://another-one_here.com.bz"),
            ]
        ),
        "The URLs must not exist, otherwise this test will fail.",
    )
    def test_multiple_errors(self):
        """Check that the tool contains more than one error."""
        results = self._test(
            _make_fake_package(
                [
                    ["foo", "https://website_missing_here.gov"],
                    ["bar", "https://another-one_here.com.bz"],
                ]
            )
        )
        self.assertEqual({"foo", "bar"}, results)

    @unittest.skipIf(
        any(
            [
                url_help.is_url_reachable("https://website_missing_here.gov"),
                not url_help.is_url_reachable("https://google.com"),
                url_help.is_url_reachable("https://another-one_here.com.bz"),
                url_help.is_url_reachable("url://thing-one_here.com.bz"),
            ]
        ),
        "Each URL must exist or not exist in the correct sequence, otherwise this test will fail.",
    )
    def test_partial_errors_001(self):
        """Check certain URLs pass and others fail as expected."""
        results = self._test(
            _make_fake_package(
                [
                    ["thing", "https://website_missing_here.gov"],
                    ["existing", "https://google.com"],
                    ["another", "https://another-one_here.com.bz"],
                    ["foo_bar", "url://thing-one_here.com.bz"],
                ]
            )
        )
        self.assertEqual({"thing", "another", "foo_bar"}, results)

    @unittest.skipIf(
        any(
            [
                url_help.is_url_reachable("https://website_missing_here.gov"),
                not url_help.is_url_reachable("https://google.com"),
                url_help.is_url_reachable("https://another-one_here.com.bz"),
                url_help.is_url_reachable("url://thing-one_here.com.bz"),
            ]
        ),
        "Each URL must exist or not exist in the correct sequence, otherwise this test will fail.",
    )
    def test_partial_errors_002(self):
        """Check certain URLs pass and others fail as expected."""
        results = self._test(
            _make_fake_package(
                [
                    ["thing", "$BROWSER https://website_missing_here.gov"],
                    ["existing", "$BROWSER https://google.com"],
                    ["another", "$BROWSER https://another-one_here.com.bz"],
                    ["foo_bar", "$BROWSER url://thing-one_here.com.bz"],
                ]
            )
        )
        self.assertEqual({"thing", "another", "foo_bar"}, results)


def _make_fake_package(help_text=_DEFAULT_HELP):
    """With the given help information, create a fake Rez package for testing.

    Args:
        help_text (list[list[str]] or NoneType, optional):
            The help information to add to the output Rez package code.
            If no value is given, do not add ``help`` to the package.
            Default is :attr:`_DEFAULT_HELP`.

    Returns:
        str: The Rez package code.

    """
    base = textwrap.dedent(
        """\
        name = "my_fake_package"

        version = "1.0.0"

        description = "A fake Rez package"

        authors = [
            "Me",
        ]
        """
    )

    if help_text == _DEFAULT_HELP:
        return base

    base += "\nhelp = {help_text!r}"

    return base.format(help_text=help_text)
