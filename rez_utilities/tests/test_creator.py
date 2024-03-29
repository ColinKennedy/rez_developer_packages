#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests for building/installing Rez packages."""

from __future__ import unicode_literals

import atexit
import contextlib
import copy
import functools
import io
import logging
import os
import shutil
import tempfile
import textwrap

import git
from python_compatibility.testing import common
from rez import exceptions, packages_
from rez.config import config
from six.moves import mock

from rez_utilities import creator, finder, silencer

from .common import pather

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_LOGGER = logging.getLogger(__name__)


class Build(common.Common):
    """Test that building Rez packages works or fails exactly whenever it's expected."""

    def test_build_build(self):
        """Test that a built Rez package cannot be built again."""
        root = tempfile.mkdtemp("_fake_source_package_with_build_method")
        build_package, build_root = _build_source_that_has_build_method(root)
        self.delete_item_later(root)
        self.delete_item_later(build_root)

        # Typically, you can't build something that has already been
        # built Unless the build process also copies the files needed to
        # build the package again. Which is non-standard and weird but I
        # guess still possible.
        #
        another_root = tempfile.mkdtemp(suffix="_another_root")
        self.delete_item_later(another_root)

        with self.assertRaises(exceptions.BuildSystemError):
            creator.build(build_package, another_root, quiet=True)

    def test_build_source(self):
        """Build a regular source Rez package."""
        root = tempfile.mkdtemp("_fake_source_package_with_build_method")
        build_package, build_root = _build_source_that_has_build_method(root)
        self.delete_item_later(root)
        self.delete_item_later(build_root)

        self.assertIsNotNone(build_package)

    def test_no_build_method(self):
        """Fail to build a Rez package if it has no declared way to build the package."""
        package_root = tempfile.mkdtemp("_fake_source_package_with_no_build_method")

        with io.open(
            os.path.join(package_root, "package.py"),
            "w",
            encoding="ascii",
        ) as handler:
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
        self.delete_item_later(root)

        with self.assertRaises(exceptions.BuildSystemError):
            creator.build(package, root, quiet=True)

    def test_packages_path(self):
        """Make sure packages_path isn't accidentally modified."""
        root = tempfile.mkdtemp("_fake_source_package_with_build_method")
        paths = ["/stuff"]

        with _clear_implicit_packages():
            build_package, build_root = _build_source_that_has_build_method(
                root, packages_path=paths
            )

        atexit.register(functools.partial(shutil.rmtree, root))
        atexit.register(functools.partial(shutil.rmtree, build_root))

        self.assertNotEqual(paths, build_package.config.packages_path)


class Release(common.Common):
    """Make sure :func:`rez_utilities.creator.release_package` works as expected."""

    def test_normal(self):
        """Release a package and make sure it is valid."""

        def _make_fake_git_repository_at_directory(root):
            repository = git.Repo.init(root)
            repository.index.add(".")
            repository.index.commit("initial commit")

        source_path = tempfile.mkdtemp(suffix="_rez_package_source_path")

        with io.open(
            os.path.join(source_path, "package.py"), "w", encoding="ascii"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"
                    version = "1.0.0"
                    build_command = "echo 'foo'"
                    """
                )
            )

        _make_fake_git_repository_at_directory(source_path)

        package = packages_.get_developer_package(source_path)

        options = mock.MagicMock()
        options.cmd = "release"
        options.debug = False
        options.message = "Fake release message"
        options.no_message = False
        options.process = "local"
        options.variants = None
        options.vcs = None

        parser = mock.MagicMock()
        parser.prog = "rez release"

        release_path = pather.normalize(
            tempfile.mkdtemp(suffix="_rez_package_release_path")
        )

        with silencer.get_context(), _clear_implicit_packages(), _clear_hooks():
            creator.release(
                finder.get_package_root(package), options, parser, release_path
            )

        release_package = packages_.get_developer_package(
            os.path.join(release_path, "some_package", "1.0.0")
        )

        self.assertIsNotNone(release_package)


def _build_source_that_has_build_method(root, packages_path=None):
    """Create a source Rez package and then build it to some temporary location."""
    with io.open(os.path.join(root, "package.py"), "w", encoding="ascii") as handler:
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

    return (
        creator.build(package, build_root, packages_path=packages_path, quiet=True),
        build_root,
    )


@contextlib.contextmanager
def _clear_hooks():
    """Prevent any user-defined release hooks from interfering with unittests.

    See Also:
        :obj:`rez.config.config`

    Yields:
        A context with no release hooks.

    """
    original_hooks = copy.copy(config.release_hooks)  # pylint: disable=no-member
    original_plugin_path = copy.copy(config.plugin_path)  # pylint: disable=no-member
    config.release_hooks[:] = []  # pylint: disable=no-member
    config.plugin_path[:] = []  # pylint: disable=no-member

    try:
        yield
    finally:
        config.release_hooks[:] = original_hooks  # pylint: disable=no-member
        config.plugin_path[:] = original_plugin_path  # pylint: disable=no-member


@contextlib.contextmanager
def _clear_implicit_packages():
    """Prevent any user-defined implicit packages from interfering with unittests.

    See Also:
        :obj:`rez.config.config`

    Yields:
        A context with no implicit_packages.

    """
    original = copy.copy(config.implicit_packages)  # pylint: disable=no-member
    config.implicit_packages[:] = []  # pylint: disable=no-member

    try:
        yield
    finally:
        config.implicit_packages[:] = original  # pylint: disable=no-member
