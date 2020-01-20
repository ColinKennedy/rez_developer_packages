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
