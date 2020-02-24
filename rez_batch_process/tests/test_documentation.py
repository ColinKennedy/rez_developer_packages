#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic tests that add fake Python documentation to Rez packages.

This "add documentation" test is done to make sure that
:class:`.RezShellCommand` works as expected.

"""

import functools
import os
import tempfile
import textwrap
import uuid

import git
from python_compatibility.testing import common
from rez import exceptions
from rez_batch_process.core import registry, worker
from rez_utilities import creator, inspection
from six.moves import mock

from . import package_common


class Add(common.Common):
    """Check that :class:`.RezShellCommand` can run a command on different types of Rez packages."""

    def _test_package(self, packages):
        """Make sure that the given `packages` get "fixed" properly.

        This method works by setting the "run" command to create a file
        in the user's source Rez package. If the file exists, it ran
        successfully. If it doesn't, then the command must have failed.

        Args:
            packages (iter[:class:`rez.packages_.Package`]):
                The Rez packages to run a command on. e.g. adding documentation.

        """
        name = "{base}.txt".format(base=uuid.uuid4())
        arguments = _make_arguments(name)
        command = registry.get_command("shell")
        runner = functools.partial(command.run, arguments=arguments)

        with mock.patch(
            "rez_batch_process.core.gitter.git_registry.get_remote_adapter"
        ) as patch:
            patch.create_pull_request = lambda *args, **kwargs: None
            ran, un_ran, invalids = worker.run(runner, packages)

        self.assertEqual((set(), []), (un_ran, invalids))

        package = next(iter(ran))
        package_root = inspection.get_package_root(package)
        git_repository_root = os.path.dirname(package_root)
        git_repository = git.Repo(git_repository_root)

        for branch in git_repository.branches:
            if branch.name.startswith(arguments.pull_request_name):
                branch.checkout()

                break

        test_file = os.path.join(package_root, name)

        self.assertTrue(os.path.isfile(test_file))
        self.assertFalse(inspection.is_built_package(package))

    def _make_symlinkable_source_package(self):
        """Make a Rez package that builds using symlinks.

        Returns:
            :class:`rez.developer_package.DeveloperPackage`: The generated Rez package.

        """
        root = tempfile.mkdtemp(suffix="_source_root")
        self.delete_item_later(root)
        package = package_common.make_package(
            "package_name", root, package_common.make_source_python_package
        )
        package_root = inspection.get_package_root(package)
        rezbuild_file = os.path.join(package_root, "rezbuild.py")

        with open(rezbuild_file, "w") as handler:
            handler.write(
                textwrap.dedent(
                    '''\
                    #!/usr/bin/env python
                    # -*- coding: utf-8 -*-

                    """The main module which installs Maya onto the user's system."""

                    # IMPORT STANDARD LIBRARIES
                    import os
                    import shutil
                    import sys


                    def build(source_path, install_path):
                        for folder in ("python", ):
                            destination = os.path.join(install_path, folder)

                            if os.path.isdir(destination):
                                shutil.rmtree(destination)
                            elif os.path.isfile(destination):
                                os.remove(destination)

                            source = os.path.join(source_path, folder)
                            os.symlink(source, destination)


                    if __name__ == "__main__":
                        build(
                            source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
                            install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
                        )
                    '''
                )
            )

        return package

    def _wrap_in_repository(self, package):
        """Copy the given Rez package into a git repository and re-return it.

        Args:
            package (:class:`rez.packages_.Package`):
                The Rez package that will be copied.

        Returns:
            :class:`rez.packages_.Package`:
                The newly copied Rez package, located inside of the git repository.

        """
        root = os.path.dirname(inspection.get_package_root(package))
        repository, packages, remote_root = package_common.make_fake_repository(
            [package], root
        )
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        return packages[0]

    def test_build_symlinked(self):
        """Create a built Rez package that symlinks back to a source Rez package.

        The source Rez package is inside of a git repository. And this
        repository will be referenced to create the new documentation +
        pull request.

        Raises:
            RuntimeError: If for whatever reason a built Rez package could not be created.

        """
        package = self._make_symlinkable_source_package()
        package = self._wrap_in_repository(package)

        build_root = tempfile.mkdtemp(suffix="_build_folder")
        self.delete_item_later(build_root)
        build_package = creator.build(package, build_root)

        if not inspection.is_built_package(build_package):
            raise RuntimeError("Package is not built.")

        self._test_package([build_package])

    def test_invalid(self):
        """Make an invalid package and try to add it to a repository."""
        root = tempfile.mkdtemp(suffix="_source_package_with_no_variants")
        self.delete_item_later(root)

        package = package_common.make_package(
            "project_a", root, package_common.make_source_python_package
        )

        with open(package.filepath, "a") as handler:
            handler.write("\nsyntax error here, bro!")

        with self.assertRaises(exceptions.ResourceError):
            self._wrap_in_repository(package)

    def test_source_no_variant(self):
        """Create a Rez package that has no variants and run a command on it.

        Reference:
            https://github.com/nerdvegas/rez/wiki/Variants

        """
        root = tempfile.mkdtemp(suffix="_source_package_with_no_variants")
        self.delete_item_later(root)

        package = package_common.make_package(
            "project_a", root, package_common.make_source_python_package
        )
        package = self._wrap_in_repository(package)

        self._test_package([package])

    def test_source_with_variant(self):
        """Create a Rez package that has variants and run a command on it.

        Reference:
            https://github.com/nerdvegas/rez/wiki/Variants

        """
        root = tempfile.mkdtemp(suffix="_source_package_with_variants")
        self.delete_item_later(root)

        package = package_common.make_package(
            "project_a", root, package_common.make_source_variant_python_package
        )
        package = self._wrap_in_repository(package)

        self._test_package([package])

    # TODO : Finish
    # def test_release(self):
    #     pass


def _make_arguments(name):
    """Create fake user CLI input for the tests in this module.

    This CLI input tells rez_batch_process that the command to
    run is "touch `name`". Assuming `name` doesn't exist as a file in
    the user's Rez package already, it's the perfect way to test whether
    or not the command actually ran. You just check to see if the file
    exists and you're done.

    Args:
        name (str): The name of a file that will be created.

    Returns:
        :class:`mock.MagicMock`: The fake user-provided CLI options.

    """
    arguments = mock.MagicMock()
    arguments.command = "touch " + name
    arguments.pull_request_name = "ticket-name"
    arguments.exit_on_error = True

    return arguments
