#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that everything in explains.py works as expected."""

import os
import textwrap

from rez_lint import cli
from rez_lint.core import message_description
from rez_lint.plugins.checkers import base_checker
from rez_utilities import inspection
from six.moves import mock

from .. import packaging


class FileChecks(packaging.BasePackaging):
    """Check that expected files in the Rez package exist."""

    @staticmethod
    def _get_no_changelog_message(directory):
        return message_description.Description(
            ["Rez package has no CHANGELOG file"],
            message_description.Location(directory, 0, 0, ""),
            base_checker.Code(short_name="E", long_name="no-change-log"),
        )

    @staticmethod
    def _get_no_documentation_message(directory):
        summary = "No documentation found"

        return message_description.Description(
            [summary],
            message_description.Location(directory, 0, 0, ""),
            base_checker.Code(short_name="E", long_name="no-documentation"),
            full=[
                summary,
                "Consider adding documentation to your Python package.",
                "Reference: https://www.sphinx-doc.org/en/master/usage/quickstart.html",
            ],
        )

    @staticmethod
    def _get_no_readme_message(directory):
        return message_description.Description(
            ["Rez package has no README file"],
            message_description.Location(directory, 0, 0, ""),
            base_checker.Code(short_name="E", long_name="no-read-me"),
        )

    def _make_generic_installed_package(self):
        package = self._make_installed_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                build_command = "echo 'foo'"
                """
            ),
        )

        return inspection.get_package_root(package)

    def test_has_changelog(self):
        """Report a missing CHANGELOG file if none exists."""
        directory = self._make_generic_installed_package()
        open(os.path.join(directory, "CHANGELOG.rst"), "a").close()

        results = cli.lint(directory)
        issue = self._get_no_changelog_message(directory)

        self.assertTrue(issue not in results)

    def test_no_changelog(self):
        """Report a missing CHANGELOG file if none exists."""
        directory = self._make_generic_installed_package()

        results = cli.lint(directory)
        issue = self._get_no_changelog_message(directory)

        self.assertTrue(issue in results)

    def test_has_documentation(self):
        """Report a missing Sphinx documentation conf.py if none exists."""
        directory = self._make_generic_installed_package()
        documentation = os.path.join(directory, "documentation", "source")
        os.makedirs(documentation)
        open(os.path.join(documentation, "conf.py"), "a").close()

        results = cli.lint(directory)
        issue = self._get_no_documentation_message(directory)

        self.assertTrue(issue not in results)

    def test_no_documentation(self):
        """Report a missing Sphinx documentation conf.py file if none exists."""
        directory = self._make_generic_installed_package()

        with mock.patch(
            "rez_lint.plugins.checkers.explains._has_context_python_package"
        ) as patched:
            patched.return_value = True
            results = cli.lint(directory)

        issue = self._get_no_documentation_message(directory)

        self.assertTrue(issue in results)

    def test_has_readme(self):
        """Report a missing README file if none exists."""
        directory = self._make_generic_installed_package()
        open(os.path.join(directory, "README.md"), "a").close()

        results = cli.lint(directory)
        issue = self._get_no_readme_message(directory)

        self.assertTrue(issue not in results)

    def test_no_readme(self):
        """Report a missing README file if none exists."""
        directory = self._make_generic_installed_package()

        results = cli.lint(directory)
        issue = self._get_no_readme_message(directory)

        self.assertTrue(issue in results)


class NoHelp(packaging.BasePackaging):
    """Test that the :class:`rez_lint.plugins.checkers.explains.NoHelp.` class works."""

    def _test_found(self, name, code):
        """Run a test that assumes that there is "no-help" issue.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.

        Raises:
            AssertionError: If `code` actually does not return a "no-help" issue.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.delete_item_later(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "The help attribute is undefined or empty"
        ]

        self.assertEqual(1, len(issues))

        first_non_summary_line = issues[0].get_message(verbose=True)[1].lstrip()

        self.assertTrue(
            first_non_summary_line
            == "Every Rez package should always point to some documentation."
        )

    def _test_not_found(self, name, code):
        """Run a test that assumes that there is no "no-help" issue.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.

        Raises:
            AssertionError: If `code` actually does return a "no-help" issue.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.delete_item_later(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "The help attribute is undefined or empty"
        ]

        self.assertEqual([], issues)

    def test_undefined(self):
        """Return an error if there's no defined help."""
        self._test_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                """
            ),
        )

    def test_empty_001(self):
        """Return an error if there's an empty URL list."""
        self._test_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = []
                """
            ),
        )

    def test_empty_002(self):
        """Return an error if there's an empty URL string."""
        self._test_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = ""
                """
            ),
        )

    def test_okay_001(self):
        """Don't return an issue if there is a labeled help URL."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = [["some label", "some_website"]]
                """
            ),
        )

    def test_okay_002(self):
        """Don't return an issue if there is a help URL string."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = "some_website"
                """
            ),
        )

    def test_multiple(self):
        """Don't return an issue if there are 2+ help URLs."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = [["some label", "some_website"], ["another", "thing"]]
                """
            ),
        )
