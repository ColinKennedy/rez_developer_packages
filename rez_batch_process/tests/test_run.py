#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that is tests the logic of the :func:`.fix` command.

:func:`.fix` also calls :func:`.report` so that get's tested too, by-extension.

"""

# TODO : Add tests for skipping. Very important!

import logging
import os
import tempfile

import git
import wurlitzer
from rez import packages_
from rez.config import config
from rez_batch_process.core import exceptions, worker
from rez_utilities import creator, inspection
from six.moves import mock

from . import package_common

_LOGGER = logging.getLogger(__name__)


class Fix(package_common.Tests):
    """Apply documentation to the package(s) that need them."""

    def test_empty(self):
        """Check that zero packages does not error."""
        self._test((set(), [], []), [])

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_one(self, run_command):
        """Run command on a single Rez package.

        Unlike :meth:`Fix.test_two` which has special logic for dealing
        with source vs release packages, this test will just run on a
        single source Rez package.

        In other words, this test is intentionally simpler than
        :meth:`Fix.test_two`.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        run_command.return_value = ""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        packages = [
            package_common.make_package(
                "project_a", root, package_common.make_source_python_package
            )
        ]
        repository, packages, remote_root = package_common.make_fake_repository(
            packages, root
        )
        self.add_item(repository.working_dir)
        self.add_item(remote_root)

        self._test((set(), [], []), packages)
        self.assertEqual(1, run_command.call_count)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_two(self, run_command):
        """Run command on two Rez packages from the same repository.

        This test creates 2 "source" Rez packages and "releases" them
        to some directory and then runs fix on them (which in turn
        should detect that they're released) and then reconstruct
        the source repository that they came from and run the
        :func:`.run_command` function on them.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        run_command.return_value = ""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        packages = [
            package_common.make_package(
                "project_a", root, package_common.make_source_python_package
            ),
            package_common.make_package(
                "project_b",
                root,
                package_common.make_source_python_package,
                dependencies={"project_a-1+<2"},
            ),
        ]

        repository, packages, remote_root = package_common.make_fake_repository(
            packages, root
        )
        self.add_item(repository.working_dir)
        self.add_item(remote_root)
        release_path = _release_packages(packages)
        self.add_item(release_path)

        self._test((set(), [], []), packages, paths=[release_path])
        self.assertEqual(2, run_command.call_count)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_mix(self, run_command):
        """Run command on only to the Rez packages that need it.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        run_command.return_value = ""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        packages = [
            package_common.make_package(
                "project_a", root, package_common.make_source_package,
            ),
            package_common.make_package(
                "project_b",
                root,
                package_common.make_source_python_package,
                dependencies={"project_a-1+<2"},
            ),
        ]

        repository, packages, remote_root = package_common.make_fake_repository(
            packages, root
        )
        self.add_item(repository.working_dir)
        self.add_item(remote_root)

        release_path = _release_packages(packages)
        self.add_item(release_path)

        package = next(package for package in packages if package.name == "project_a")

        self._test(
            (
                set(),
                [],
                [
                    worker.Skip(
                        package,
                        inspection.get_package_root(package),
                        "not a Python package",
                    )
                ],
            ),
            packages,
            paths=[release_path],
        )
        self.assertEqual(1, run_command.call_count)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_multiple(self, run_command):
        """Run command on Rez packages with more than one repository.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        run_command.return_value = ""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        repository_a, packages_a, remote_root = package_common.make_fake_repository(
            [
                package_common.make_package(
                    "project_a", root, package_common.make_source_python_package,
                ),
                package_common.make_package(
                    "project_b",
                    root,
                    package_common.make_source_python_package,
                    dependencies={"project_a-1+<2"},
                ),
            ],
            root,
        )
        self.add_item(repository_a.working_dir)
        self.add_item(remote_root)
        release_path_a = _release_packages(packages_a)
        self.add_item(release_path_a)

        repository_b, packages_b, remote_root = package_common.make_fake_repository(
            [
                package_common.make_package(
                    "project_c", root, package_common.make_source_python_package,
                ),
                package_common.make_package(
                    "project_d",
                    root,
                    package_common.make_source_python_package,
                    dependencies={"project_a-1+<2"},
                ),
                package_common.make_package(
                    "project_e", root, package_common.make_source_python_package,
                ),
            ],
            root,
        )
        self.add_item(repository_b.working_dir)
        self.add_item(remote_root)
        release_path_b = _release_packages(packages_b, search_paths=[release_path_a])
        self.add_item(release_path_b)

        self._test(
            (set(), [], [],), packages_a, paths=[release_path_a],
        )
        self._test(
            (set(), [], [],), packages_b, paths=[release_path_b, release_path_a],
        )

        self.assertEqual(5, run_command.call_count)


# TODO : This class assumes that build Rez packages are in git
# repositories. Which is never the case I need actual unittests for when
# the build packages are NOT in a git repository but instead point to a
# source directory that does have them
#
class Variations(package_common.Tests):
    """Check that different types of Rez packages execute correctly.

    Types such as

    - source
    - source with variants
    - build
    - build with variants
    - released

    etc.

    """

    def _setup_test(self, run_command, builder, variants=None):
        """Build an environment that tests in this class can use.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.
            builder (callable[str, str, str, str] -> str):
                The function that is used to generate the "contents" of the
                Rez package. This function is only responsible for creating
                the package.py/rezbuild.py files, it doesn't create a Python
                package, for example. This parameter is responsible for
                creating the rest of the files of the package.
            variants (list[list[str]]):
                The extra Rez package build configurations for this package.
                No variants will be installed if nothing is given. Default
                is None.

        Returns:
            list[:class:`rez.developer_package.Package`]:
                The generated Rez packages that are inside of a git repository
                and will be used for unittesting.

        """
        run_command.return_value = ""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        packages = [
            package_common.make_package("project_a", root, builder, variants=variants)
        ]
        path_root = inspection.get_packages_path_from_package(packages[0])
        repository, packages, remote_root = package_common.make_fake_repository(
            packages, path_root
        )
        self.add_item(repository.working_dir)
        self.add_item(remote_root)

        return packages

    def _test_release(self, run_command, builder):
        """Build a Rez package, release it, and then test it.

        This is a convenience function to keep unittests a bit more concise.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.
            builder (callable[str, str, str, str] -> str):
                The function that is used to generate the "contents" of the
                Rez package. This function is only responsible for creating
                the package.py/rezbuild.py files, it doesn't create a Python
                package, for example. This parameter is responsible for
                creating the rest of the files of the package.

        """
        packages = self._setup_test(run_command, builder, variants=[["python-2.7"]],)

        release_path = _release_packages(
            packages, search_paths=config.packages_path,  # pylint: disable=no-member
        )
        self.add_item(release_path)

        packages = [
            packages_.get_developer_package(
                os.path.join(release_path, package.name, str(package.version))
            )
            for package in packages
        ]

        self._test((set(), [], []), packages)
        self.assertEqual(1, run_command.call_count)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_build(self, run_command):
        """Create a build package and run a command on it.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        packages = self._setup_test(
            run_command, package_common.make_build_python_package,
        )
        self._test((set(), [], []), packages)
        self.assertEqual(1, run_command.call_count)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_build_variant(self, run_command):
        """Create a build package that has 1+ Rez package variants and run a command on it.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        packages = self._setup_test(
            run_command,
            package_common.make_build_python_package,
            variants=[["python-2.7"]],
        )
        self._test((set(), [], []), packages)
        self.assertEqual(1, run_command.call_count)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_released(self, run_command):
        """Create a released Rez package and then test that we can run shell commands for it.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        self._test_release(run_command, package_common.make_source_python_package)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_released_variant(self, run_command):
        """Create a released Rez package and then test that we can run shell commands for it.

        This method will create a released Rez package that contains at
        least one variant.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        self._test_release(
            run_command, package_common.make_source_variant_python_package
        )

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_source_no_variant(self, run_command):
        """Create a source (non-built) Rez package and run a command on it.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        packages = self._setup_test(
            run_command, package_common.make_source_python_package,
        )
        self._test((set(), [], []), packages)
        self.assertEqual(1, run_command.call_count)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_source_variant(self, run_command):
        """Create a source (non-built) Rez package that has 1+ variants and run a command on it.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        packages = self._setup_test(
            run_command, package_common.make_source_variant_python_package,
        )
        self._test((set(), [], []), packages)
        self.assertEqual(1, run_command.call_count)


class Bad(package_common.Tests):
    """A series of scenarios where a bad environment or bad input is given."""

    @staticmethod
    def _make_source_package_with_no_remote(text, name, _, root):
        """Make a source Rez package with a repository that has no remote destination.

        Args:
            text (str): The contents of the package.py file that will be created.
            name (str): The name of the Rez package.
            root (str): An absolute folder on-disk where the package.py will be written to.

        Returns:
            str: The full path on-disk where the package.py file is written to.

        """

        def _make_fake_git_repository_at_directory(root):
            repository = git.Repo.init(root)
            repository.index.add(".")
            repository.index.commit("initial commit")

        path = package_common.make_source_package(text, name, None, root)
        _make_fake_git_repository_at_directory(root)

        return path

    def test_no_repository(self):
        """Check that a fix will not run if the package has no destination repository."""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        package = package_common.make_package(
            "project_a", root, self._make_source_package_with_no_remote
        )

        invalids = [
            exceptions.NoGitRepository(
                package,
                os.path.join(root, "project_a"),
                "Package could not be found: project_a==1.0.0",
            )
        ]
        expected = (set(), invalids, [])
        self._test(expected, [package])

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand.run")
    def test_released_dependency_missing(self, run_command):
        """Fail to resolve a package because "project_a" could not be found.

        Args:
            run_command (:class:`mock.MagicMock`):
                A replacement for the function that would normally run
                as part of the commands that run on a Rez package. If
                this function gets run, we know that this test passes.

        """
        run_command.return_value = ""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        packages = [
            package_common.make_package(
                "project_a", root, package_common.make_source_python_package
            ),
            package_common.make_package(
                "project_b",
                root,
                package_common.make_source_python_package,
                dependencies={"project_a-1+<2"},
            ),
        ]

        repository, packages, remote_root = package_common.make_fake_repository(
            packages, root
        )
        self.add_item(repository.working_dir)
        self.add_item(remote_root)

        package = packages[1]
        package_root = inspection.get_package_root(package)
        self._test(
            (
                set(),
                [
                    exceptions.InvalidPackage(
                        package,
                        package_root,
                        "Package could not be found: project_a-1+<2",
                    )
                ],
                [],
            ),
            packages,
        )
        self.assertEqual(1, run_command.call_count)

    def test_skip(self):
        """Do not run fix if the Rez package does not define a Python package / module."""
        root = os.path.join(tempfile.mkdtemp(), "test_folder")
        os.makedirs(root)
        self.add_item(root)

        package = package_common.make_package(
            "project_a", root, package_common.make_source_package
        )
        repository, packages, remote_root = package_common.make_fake_repository(
            [package], root
        )
        self.add_item(repository.working_dir)
        self.add_item(remote_root)
        package = packages[0]

        expected = (
            set(),
            [],
            [
                worker.Skip(
                    package,
                    os.path.join(repository.working_dir, "project_a"),
                    "not a Python package",
                )
            ],
        )
        self._test(expected, packages)


def _release_packages(packages, search_paths=None):
    """Release 1+ Rez packages.

    Args:
        packages (list[:class:`rez.packages_.Package`]):
            The source Rez packages that will be built and released.
        search_paths (list[str], optional):
            The directories on-disk that can be used to help find extra
            dependencies that a Rez package might require. Default is None.

    Raises:
        ValueError: If `packages` is invalid.

    Returns:
        str:
            The directory where the released package was sent to.
            Normally, this should always be `new_release_path`. But
            if `new_release_path` wasn't given then this returns a
            temporary directory.

    """
    if not packages:
        raise ValueError("No packages were given")

    if not search_paths:
        search_paths = []

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

    package = packages[0]

    _LOGGER.info(
        'Releasing the fake package "%s" to a temporary directory.', package.name
    )

    temporary_path = tempfile.mkdtemp()

    # Rez prints a lot of text to console during release so we'll silence it all
    with wurlitzer.pipes():
        new_release_path = creator.release_package(
            inspection.get_package_root(package),
            options,
            parser,
            temporary_path,
            search_paths=search_paths,
        )

    for package in packages[1:]:
        with wurlitzer.pipes():
            _LOGGER.info(
                'Releasing the fake package "%s" to "%s".',
                package.name,
                new_release_path,
            )
            creator.release_package(
                inspection.get_package_root(package),
                options,
                parser,
                new_release_path,
                search_paths=search_paths,
            )

    return new_release_path