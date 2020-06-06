#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test classes and functions in the :mod:`rez_lint.plugins.contexts.packaging` module."""

import os
import tempfile
import textwrap

from rez import packages_
from rez_lint.core import lint_constant
from rez_lint.plugins.contexts import packaging
from rez_utilities import creator, inspection

from .. import packaging as testing_packaging


class SourceResolved(testing_packaging.BasePackaging):
    """Test cases for the :class:`rez_lint.plugins.contexts.SourceResolvedContext` class."""

    def test_get_context(self):
        """Check that Rez can resolve a context correctly and return it."""
        directory = testing_packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = [
                    "some_dependency-1",
                ]
                """
            ),
        )
        self.delete_item_later(os.path.dirname(directory))

        package = packages_.get_developer_package(directory)

        dependency_directory = testing_packaging.make_fake_source_package(
            "some_dependency",
            textwrap.dedent(
                """\
                name = "some_dependency"
                version = "1.1.0"
                build_command = "echo 'foo'"
                """
            ),
        )
        self.delete_item_later(os.path.dirname(dependency_directory))

        dependency_package = packages_.get_developer_package(dependency_directory)
        dependency_build_path = tempfile.mkdtemp(suffix="_dependency_build_path")
        self.delete_item_later(dependency_build_path)
        dependency_package = creator.build(dependency_package, dependency_build_path, quiet=True)
        dependency_path = inspection.get_packages_path_from_package(dependency_package)

        context = dict()

        with testing_packaging.override_packages_path([dependency_path], prepend=True):
            packaging.SourceResolvedContext.run(package, context)

        self.assertTrue(lint_constant.RESOLVED_SOURCE_CONTEXT in context)
        rez_resolved = context[lint_constant.RESOLVED_SOURCE_CONTEXT]
        self.assertEqual(
            os.path.join(directory), rez_resolved.get_environ()["REZ_SOME_PACKAGE_ROOT"]
        )
        self.assertEqual(set(), context[lint_constant.DEPENDENT_PACKAGES])

    def test_no_commands(self):
        """If the Rez package has no commands, make sure this does not cause an error.

        Instead, just have the context return early.

        """
        directory = testing_packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                """
            ),
        )
        self.delete_item_later(os.path.dirname(directory))

        package = packages_.get_developer_package(directory)
        context = dict()
        packaging.SourceResolvedContext.run(package, context)
        rez_resolved = context[lint_constant.RESOLVED_SOURCE_CONTEXT]
        self.assertEqual(
            os.path.join(directory), rez_resolved.get_environ()["REZ_SOME_PACKAGE_ROOT"]
        )
        self.assertEqual(set(), context[lint_constant.DEPENDENT_PACKAGES])
