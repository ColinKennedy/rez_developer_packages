#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that different Rez packages with missing or in-complete data behave as expected."""

import atexit
import functools
import os
import shutil
import tempfile
import textwrap

from rez_lint import cli
from rez_lint.core import exceptions

from . import packaging


class InvalidPackages(packaging.BasePackaging):
    """Check that different Rez packages with missing or in-complete data behave as expected."""

    def test_incomplete_package(self):
        """If a Rez package is completely invalid, exit early."""
        directory = packaging.make_fake_source_package("some_package", "")
        self.delete_item_later(os.path.dirname(directory))

        with self.assertRaises(exceptions.NoPackageFound):
            cli.lint(directory)

    def test_unresolved_dependency(self):
        """Let a package go through ``rez_lint`` even if there's a problem with it."""
        directory = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = ["a_dependency_that_does_not_resolve"]
                """
            ),
        )
        self.delete_item_later(os.path.dirname(directory))

        cli.lint(directory)

    def test_schema(self):
        """Stop linting on a package if it's invalid."""
        code = textwrap.dedent(
            """\
            name = "my_package"
            version = "1.0.0"
            build_command = "echo 'foo'"
            uuid = 8
            """
        )
        directory = packaging.make_fake_source_package("my_package", code)

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_code().long_name == "invalid-schema"
        ]

        self.assertNotEqual([], issues)

    def test_schema_recursive(self):
        """Stop linting on a package if it's invalid."""
        files = [
            # Invalid Rez packages
            textwrap.dedent(
                """\
                name = "my_package"
                version = "1.0.0"
                build_command = "echo 'foo'"
                uuid = 8
                """
            ),
            textwrap.dedent(
                """\
                name = "my_package"
                version = "1.0.0"
                build_command = "echo 'foo'"
                uuid = 8
                """
            ),

            # A valid Rez package
            textwrap.dedent(
                """\
                name = "my_package"
                version = "1.0.0"
                build_command = "echo 'foo'"
                uuid = "54f0a93c-a9db-4026-b856-def2d0b6e956"
                """
            ),
        ]

        directory = tempfile.mkdtemp(prefix="rez_lint_InvalidPackages_test_schema_recursive_")
        # atexit.register(functools.partial(shutil.rmtree, directory))

        for index, code in enumerate(files):
            destination = os.path.join(directory, "folder_{index}".format(index=index))
            os.makedirs(destination)

            with open(os.path.join(destination, "package.py"), "w") as handler:
                handler.write(code)

        results = cli.lint(directory, recursive=True)

        issues = [
            description
            for description in results
            if description.get_code().long_name == "invalid-schema"
        ]

        self.assertEqual(2, len(issues))
