#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests for building/installing Rez packages."""

import os
import tempfile
import textwrap

from python_compatibility.testing import common
from rez import exceptions, packages_
from rez_utilities import creator

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Build(common.Common):
    """Test that building Rez packages works or fails exactly whenever it's expected."""

    def test_build_build(self):
        """Test that a built Rez package cannot be built again."""
        root = tempfile.mkdtemp("_fake_source_package_with_build_method")
        build_package, build_root = _build_source_that_has_build_method(root)
        self.add_item(root)
        self.add_item(build_root)

        # Typically, you can't build something that has already been
        # built Unless the build process also copies the files needed to
        # build the package again. Which is non-standard and weird but I
        # guess still possible.
        #
        another_root = tempfile.mkdtemp(suffix="_another_root")
        self.add_item(another_root)

        with self.assertRaises(exceptions.BuildSystemError):
            creator.build(build_package, another_root)

    def test_build_source(self):
        """Build a regular source Rez package."""
        root = tempfile.mkdtemp("_fake_source_package_with_build_method")
        build_package, build_root = _build_source_that_has_build_method(root)
        self.add_item(root)
        self.add_item(build_root)

        self.assertIsNotNone(build_package)

    def test_no_build_method(self):
        """Fail to build a Rez package if it has no declared way to build the package."""
        package_root = tempfile.mkdtemp("_fake_source_package_with_no_build_method")

        with open(os.path.join(package_root, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                name = "foo"
                version = "1.0.0"
                """
                )
            )

        package = packages_.get_developer_package(package_root)
        root = tempfile.mkdtemp(suffix="_build_test")
        self.add_item(root)

        with self.assertRaises(exceptions.BuildSystemError):
            creator.build(package, root)


def _build_source_that_has_build_method(root):
    """Create a source Rez package and then build it to some temporary location."""
    with open(os.path.join(root, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
            name = "foo"
            version = "1.0.0"
            build_command = "echo 'this command does not need to do anything'"
            """
            )
        )

    package = packages_.get_developer_package(root)
    build_root = tempfile.mkdtemp(suffix="_build_test")

    return creator.build(package, build_root), build_root
