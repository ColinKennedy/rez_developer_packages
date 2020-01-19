#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests for building/installing Rez packages."""

import logging
import os
import tempfile
import textwrap

from python_compatibility.testing import common
from rez import exceptions, packages_
from rez_utilities import creator, inspection
from six.moves import mock
import wurlitzer
import git

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_LOGGER = logging.getLogger(__name__)


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


class Release(common.Common):
    """Make sure :func:`rez_utilities.creator.release_package` works as expected."""

    def test_normal(self):
        """Release a package and make sure it is valid."""
        def _make_fake_git_repository_at_directory(root):
            repository = git.Repo.init(root)
            repository.index.add(".")
            repository.index.commit("initial commit")

        source_path = tempfile.mkdtemp(suffix="_rez_package_source_path")
        self.add_item(source_path)

        with open(os.path.join(source_path, "package.py"), "w") as handler:
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

        release_path = tempfile.mkdtemp(suffix="_rez_package_release_path")
        self.add_item(release_path)

        with wurlitzer.pipes():
            new_release_path = creator.release(
                inspection.get_package_root(package),
                options,
                parser,
                release_path,
            )

        self.assertIsNotNone(packages_.get_developer_package(new_release_path))
        self.assertTrue(os.path.isfile(os.path.join(new_release_path, "some_packge", "1.0.0")))

    # def test_normal(self):
    #     """Release a package and make sure it is valid."""
    #     source_path = tempfile.mkdtemp(suffix="_rez_package_source_path")
    #     # self.add_item(source_path)
    #
    #     with open(os.path.join(source_path, "package.py"), "w") as handler:
    #         handler.write(
    #             textwrap.dedent(
    #                 """\
    #                 name = "some_package"
    #                 version = "1.0.0"
    #                 build_command = "echo 'foo'"
    #                 """
    #             )
    #         )
    #
    #     package = packages_.get_developer_package(source_path)
    #
    #     options = mock.MagicMock()
    #     options.cmd = "release"
    #     options.debug = False
    #     options.message = "Fake release message"
    #     options.no_message = False
    #     options.process = "local"
    #     options.variants = None
    #     options.vcs = None
    #
    #     parser = mock.MagicMock()
    #     parser.prog = "rez release"
    #
    #     release_path = tempfile.mkdtemp(suffix="_rez_package_release_path")
    #     # self.add_item(release_path)
    #
    #     # Rez prints a lot of text to console during release so we'll silence it all
    #     with mock.patch('rez.release_vcs.create_release_vcs') as patch:
    #         type(patch.return_value).pkg_root = inspection.get_package_root(package)
    #         type(patch.return_value).get_changelog = lambda x, y, max_revisions: "asdfasd"
    #
    #         new_release_path = creator.release(
    #             inspection.get_package_root(package),
    #             options,
    #             parser,
    #             release_path,
    #         )
    #
    #     self.assertIsNotNone(packages_.get_developer_package(new_release_path))
    #     self.assertTrue(os.path.isfile(os.path.join(new_release_path, "some_packge", "1.0.0")))


# def _release_packages(packages, search_paths=None):
#     """Release 1+ Rez packages.
#
#     Args:
#         packages (list[:class:`rez.packages_.Package`]):
#             The source Rez packages that will be built and released.
#         search_paths (list[str], optional):
#             The directories on-disk that can be used to help find extra
#             dependencies that a Rez package might require. Default is None.
#
#     Raises:
#         ValueError: If `packages` is invalid.
#
#     Returns:
#         str:
#             The directory where the released package was sent to.
#             Normally, this should always be `new_release_path`. But
#             if `new_release_path` wasn't given then this returns a
#             temporary directory.
#
#     """
#     if not packages:
#         raise ValueError("No packages were given")
#
#     if not search_paths:
#         search_paths = []
#
#     options = mock.MagicMock()
#     options.cmd = "release"
#     options.debug = False
#     options.message = "Fake release message"
#     options.no_message = False
#     options.process = "local"
#     options.variants = None
#     options.vcs = None
#
#     parser = mock.MagicMock()
#     parser.prog = "rez release"
#
#     package = packages[0]
#
#     _LOGGER.info(
#         'Releasing the fake package "%s" to a temporary directory.', package.name
#     )
#
#     release_path = tempfile.mkdtemp()
#
#     # Rez prints a lot of text to console during release so we'll silence it all
#     with wurlitzer.pipes():
#         new_release_path = creator.release(
#             inspection.get_package_root(package),
#             options,
#             parser,
#             release_path,
#             search_paths=search_paths,
#         )
#
#     for package in packages[1:]:
#         with wurlitzer.pipes():
#             _LOGGER.info(
#                 'Releasing the fake package "%s" to "%s".',
#                 package.name,
#                 new_release_path,
#             )
#             creator.release(
#                 inspection.get_package_root(package),
#                 options,
#                 parser,
#                 new_release_path,
#                 search_paths=search_paths,
#             )
#
#     return new_release_path
#
#
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
