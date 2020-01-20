#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test that querying rez help URLs works as expected."""

import os
import tempfile
import textwrap
import unittest

from python_compatibility.testing import common
from rez import packages_
from rez_utilities import url_help

_DEFAULT_HELP = object()


class CheckUrl(common.Common):
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


class FindUrl(common.Common):
    """Find the URLs to a Rez package's help documentation."""

    def _build_package(self, code):
        """Make a Rez package, given some Rez package definition code.

        Args:
            code (str): Python code that defines a valid Rez package.

        Returns:
            :class:`rez.developer_package.DeveloperPackage`:
                The generated Rez package. This package will be
                auto-deleted once a unittest is completed.

        """
        folder = tempfile.mkdtemp()

        with open(os.path.join(folder, "package.py"), "w") as handler:
            handler.write(code)

        self.add_item(folder)
        package = packages_.get_developer_package(folder)

        return package

    def test_api_found(self):
        """Find a Rez package's documentation, using its ``help`` attribute'."""
        url = "foo"
        self.assertEqual(
            url,
            url_help.find_package_documentation(
                self._build_package(
                    _make_fake_package(help_text=[["api_documentation", url]])
                )
            ),
        )

    def test_api_multiple_found(self):
        """Find a Rez package's documentation, using its ``help`` attribute'.

        Make sure to pick the key "api_documentation" because it's a
        perfect match. "some_api_key" is only a partial match, so it
        should not be preferred.

        """
        expected_url = "lka;sdfj"
        package = self._build_package(
            _make_fake_package(
                help_text=[
                    ["something", "blah"],
                    ["another", "thing"],
                    ["some_api_key", "ttt"],
                    ["api_documentation", expected_url],
                ]
            )
        )

        self.assertEqual(expected_url, url_help.find_package_documentation(package))

    def test_api_unknown_001(self):
        """Find a Rez package's documentation, using its ``help`` attribute'.

        Since "some_api_key" is the closest known label, make sure to
        return that.

        """
        expected_url = "blah"
        package = self._build_package(
            _make_fake_package(
                help_text=[
                    ["something", "ttt"],
                    ["some_api_key", expected_url],
                    ["another", "thing"],
                ]
            )
        )

        self.assertEqual(expected_url, url_help.find_package_documentation(package))

    def test_api_unknown_002(self):
        """Find a Rez package's documentation, using its ``help`` attribute'.

        No label is found so just return the first help entry.

        """
        expected_url = "blah"
        package = self._build_package(
            _make_fake_package(
                help_text=[
                    ["something", expected_url],
                    ["foo", "ttt"],
                    ["another", "thing"],
                ]
            )
        )

        self.assertEqual(expected_url, url_help.find_package_documentation(package))

    def test_api_unknown_003(self):
        """Return no API documentation if there's no Rez package ``help`` attribute."""
        package = self._build_package(_make_fake_package(help_text=[]))

        self.assertEqual("", url_help.find_package_documentation(package))

    def test_package_found_001(self):
        """Get a Rez package's API documentation using the pre-written list of documentation."""
        package_definition = _make_fake_package()
        package_definition += '\nname = "six"'
        package = self._build_package(package_definition)

        self.assertEqual(
            "https://six.readthedocs.io", url_help.find_api_documentation(package)
        )

    def test_package_found_002(self):
        """Get the "python" Rez package's API documentation."""
        package_definition = _make_fake_package()
        package_definition += '\nname = "python"'
        package_definition += '\nversion = "2.0"'
        package = self._build_package(package_definition)

        self.assertEqual("https://docs.python.org/2/index.html", url_help.find_api_documentation(package))

        package_definition += '\nversion = "3.7.6"'
        package = self._build_package(package_definition)

        self.assertEqual("https://docs.python.org/3.7/index.html", url_help.find_api_documentation(package))

    def test_package_not_found(self):
        """Return no API docs because the package is not in the pre-written list of URLs."""
        package_definition = _make_fake_package()
        package = self._build_package(package_definition)

        self.assertEqual("", url_help.find_api_documentation(package))


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
