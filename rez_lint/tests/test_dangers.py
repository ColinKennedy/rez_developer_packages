#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap

from python_compatibility.testing import common
from rez.config import config
from rez_lint import cli
from six.moves import mock

from . import packaging


class Requirements(common.Common):
    def test_no_impropers_001(self):
        directory = packaging.make_fake_source_package(
            "my_packge",
            textwrap.dedent(
                """\
                name = "my_package"
                version = "1.0.0"
                """
            )
        )
        self.add_item(directory)

        results = cli.lint(directory)
        has_issue = any(description for description in results if description.get_summary() == "Improper package requirements were found")

        self.assertFalse(has_issue)

    def test_no_impropers_002(self):
        directory = packaging.make_fake_source_package(
            "my_package",
            textwrap.dedent(
                """\
                name = "my_package"
                version = "1.0.0"

                requires = [
                    "some_dependency_that_is_okay",
                ]
                """
            ),
        )
        # self.add_item(directory)

        dependency_directory = packaging.make_fake_source_package(
            "some_dependency_that_is_okay",
            textwrap.dedent(
                """\
                name = "some_dependency_that_is_okay"
                version = "1.0.0"
                """
            ),
        )
        # self.add_item(dependency_directory)

        original = list(config.packages_path)
        config.packages_path[:] = [directory, dependency_directory] + original

        try:
            results = cli.lint(directory)
        except Exception:
            raise
        finally:
            config.packages_path[:] = original

        has_issue = any(description for description in results if description.get_summary() == "Improper package requirements were found")

        self.assertFalse(has_issue)

    def test_one_impropers(self):
        pass

    def test_multiple_impropers(self):
        pass

    def test_mixed_impropers(self):
        pass
