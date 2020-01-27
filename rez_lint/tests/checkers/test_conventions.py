#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the classes in :mod:`rez_lint.plugins.checkers.conventions`."""

import os
import textwrap

from rez_lint import cli

from .. import packaging


class SemanticVersioning(packaging.BasePackaging):
    """Make sure :class:`rez_lint.plugins.checkers.conventions.SemanticVersioning` works."""

    def test_undefined(self):
        """If the version is undefined, don't report an issue."""
        directory = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                """
            ),
        )
        self.delete_item_later(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package has no version"
        ]

        self.assertEqual(1, len(issues))
        expected = 'Package {path}" has no version. Please define one.'.format(
            path=os.path.join(directory, "package.py")
        )

        self.assertEqual(issues[0].get_message(verbose=True)[1].lstrip(), expected)

    def test_not(self):
        """When the version is X.Y.Z (semantic), don't report an issue."""
        directory = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "2.10.3"
                """
            ),
        )
        self.delete_item_later(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package is not X.Y.Z semantic versioning."
        ]

        self.assertEqual([], issues)

    def test_is(self):
        """When the version is not X.Y.Z (semantic), report an issue."""
        directory = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "something.1.non_standard"
                """
            ),
        )
        self.delete_item_later(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package is not X.Y.Z semantic versioning."
        ]

        self.assertEqual(1, len(issues))

        expected = 'Package "{path}" has version "something.1.non_standard".'.format(
            path=os.path.join(directory, "package.py")
        )

        self.assertEqual(issues[0].get_message(verbose=True)[1].lstrip(), expected)
