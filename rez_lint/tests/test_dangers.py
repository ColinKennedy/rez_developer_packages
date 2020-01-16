#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap

from rez.config import config
from rez_lint import cli
from rez_utilities import inspection
from six.moves import mock

from . import packaging


class Requirements(packaging.BasePackaging):
    def test_no_impropers_001(self):
        package = self._make_installed_package(
            "my_package",
            textwrap.dedent(
                """\
                name = "my_package"
                version = "1.0.0"
                build_command = "echo 'foo'"
                """
            ),
        )
        directory = inspection.get_package_root(package)

        results = cli.lint(directory)
        has_issue = any(
            description
            for description in results
            if description.get_summary() == "Improper package requirements were found"
        )

        self.assertFalse(has_issue)

    def test_no_impropers_002(self):
        dependency_package = self._make_installed_package(
            "some_dependency_that_is_okay",
            textwrap.dedent(
                """\
                name = "some_dependency_that_is_okay"
                version = "1.0.0"
                build_command = "echo 'foo'"
                """
            ),
        )
        dependency_directory = inspection.get_package_root(dependency_package)
        dependency_path = inspection.get_packages_path_from_package(dependency_package)

        original = list(config.packages_path)
        config.packages_path[:] = [dependency_path] + original

        try:
            installed_package = self._make_installed_package(
                "my_package",
                textwrap.dedent(
                    """\
                    name = "my_package"
                    version = "1.0.0"

                    requires = [
                        "some_dependency_that_is_okay",
                    ]

                    build_command = "echo 'foo'"
                    """
                ),
            )
        except Exception:
            raise
        finally:
            config.packages_path[:] = original

        directory = inspection.get_package_root(installed_package)
        original = list(config.packages_path)
        config.packages_path[:] = [directory, dependency_path] + original

        try:
            results = cli.lint(directory)
        except Exception:
            raise
        finally:
            config.packages_path[:] = original

        has_issue = any(
            description
            for description in results
            if description.get_summary() == "Improper package requirements were found"
        )

        self.assertFalse(has_issue)

    # TODO : Do these
    # def test_one_impropers(self):
    #     pass
    #
    # def test_multiple_impropers(self):
    #     pass
    #
    # def test_mixed_impropers(self):
    #     pass
