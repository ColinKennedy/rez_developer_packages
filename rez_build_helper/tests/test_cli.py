#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=too-many-lines

"""Make sure :mod:`rez_build_helper` works as expected."""

from __future__ import unicode_literals

import atexit
import functools
import io
import os
import shutil
import tempfile
import textwrap
import unittest

from rez import exceptions as rez_exceptions

from .common import common, creator, finder, pymix


def _allowed_to_symlink() -> bool:
    """bool: Check if symlinking works on the current machine."""
    if not hasattr(os, "symlink"):
        return False

    source = os.path.realpath(tempfile.mkdtemp(suffix="_symlink_source"))
    destination = os.path.realpath(tempfile.mkdtemp(suffix="_symlink_destination"))
    shutil.rmtree(destination)

    try:
        os.symlink(source, destination)
    except OSError:
        # Occurs on Windows when not in a developer mode. Usually errors with
        # "A required privilege is not held by the client"
        #
        return False

    return True


class Cli(unittest.TestCase):
    """Make sure the basic CLI functions work as-expected."""

    def test_empty(self) -> None:
        """Build even if the package just contains just a package.py file."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_empty_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper"

                    def commands():
                        pass
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_empty_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isfile(os.path.join(install_location, "package.py")))

    def test_copy(self) -> None:
        """Copy folder(s) for the build Rez package."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_copy_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                }
            },
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --items python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_copy_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isdir(os.path.join(install_location, "python")))

        if pymix.can_check_links():
            self.assertFalse(os.path.islink(os.path.join(install_location, "python")))

        self.assertTrue(
            os.path.isdir(os.path.join(install_location, "python", "some_thing"))
        )
        self.assertTrue(
            os.path.isdir(
                os.path.join(install_location, "python", "some_thing", "inner_folder")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "__init__.py")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "some_module.py")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "__init__.py",
                )
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "inner_module.py",
                )
            )
        )


class SharedPythonPackages(unittest.TestCase):
    """Make sure :ref:`--shared-python-packages` works as expected."""

    def test_single_file(self) -> None:
        """Create a shared Python namespace for a single Python file."""
        directory = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_single_file_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {"some_thing.py": None}},
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = (
                        "python -m rez_build_helper "
                        "--shared-python-packages root:python"
                    )

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_single_file_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isdir(os.path.join(install_location, "python")))

        if pymix.can_check_links():
            self.assertFalse(os.path.islink(os.path.join(install_location, "python")))

        self.assertTrue(os.path.isdir(os.path.join(install_location, "python", "root")))
        self.assertTrue(
            os.path.isfile(
                os.path.join(install_location, "python", "root", "some_thing.py")
            )
        )

    def test_invalid_001_missing_namespace(self) -> None:
        """Fail to build with :ref:`--shared-python-packages` if no namespace exists."""
        directory = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_invalid_001_missing_namespace_source_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {"python": {"some_thing.py": None}},
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = (
                        "python -m rez_build_helper "
                        "--shared-python-packages :python"
                    )

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_invalid_001_missing_namespace_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        with self.assertRaises(rez_exceptions.BuildError):
            creator.build(package, destination, quiet=True)

    def test_invalid_002_no_namespace(self) -> None:
        """Fail to build with :ref:`--shared-python-packages` if there's no : value."""
        directory = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_invalid_002_no_namespace_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = (
                        "python -m rez_build_helper "
                        "--shared-python-packages python"
                    )

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_invalid_002_no_namespace_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        with self.assertRaises(rez_exceptions.BuildError):
            creator.build(package, destination, quiet=True)

    def test_invalid_003_missing_path(self) -> None:
        """Fail to build with :ref:`--shared-python-packages` if there's no : value."""
        directory = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_invalid_003_missing_path_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = (
                        "python -m rez_build_helper "
                        "--shared-python-packages root:python"
                    )

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_invalid_003_missing_path_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        with self.assertRaises(rez_exceptions.BuildError):
            creator.build(package, destination, quiet=True)

    def test_single_shared_namespace(self) -> None:
        """Create a shared Python namespace for a Python package."""
        directory = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_simple_package_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                }
            },
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = (
                        "python -m rez_build_helper "
                        "--shared-python-packages root.inner:python"
                    )

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="SharedPythonPackages_test_simple_package_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isdir(os.path.join(install_location, "python")))

        if pymix.can_check_links():
            self.assertFalse(os.path.islink(os.path.join(install_location, "python")))

        self.assertTrue(
            os.path.isdir(
                os.path.join(
                    install_location,
                    "python",
                    "root",
                    "inner",
                    "some_thing",
                    "inner_folder",
                )
            )
        )

        self.assertTrue(
            os.path.isfile(
                os.path.join(install_location, "python", "root", "__init__.py")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(install_location, "python", "root", "inner", "__init__.py")
            )
        )

        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "root",
                    "inner",
                    "some_thing",
                    "__init__.py",
                )
            )
        )

        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "root",
                    "inner",
                    "some_thing",
                    "__init__.py",
                )
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "root",
                    "inner",
                    "some_thing",
                    "some_module.py",
                )
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "root",
                    "inner",
                    "some_thing",
                    "inner_folder",
                    "__init__.py",
                )
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "root",
                    "inner",
                    "some_thing",
                    "inner_folder",
                    "inner_module.py",
                )
            )
        )


@unittest.skipIf(not _allowed_to_symlink(), "No symlinking enabled")
class Symlink(unittest.TestCase):
    """Make sure symlinks generate as expected."""

    def test_files(self) -> None:
        """Symlink only files and not folders."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_files_directory_source_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "some_file.txt": None,
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                },
            },
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --items some_file.txt python --symlink-files"  # pylint: disable=line-too-long

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_files_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        file_path = os.path.join(install_location, "some_file.txt")

        if pymix.can_check_links():
            self.assertTrue(os.path.islink(file_path))

        self.assertTrue(os.path.isfile(file_path))
        self.assertTrue(os.path.isdir(os.path.join(install_location, "python")))
        self.assertTrue(
            os.path.isdir(os.path.join(install_location, "python", "some_thing"))
        )

    def test_folders(self) -> None:
        """Symlink only folders and not files."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_folders_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "some_file.txt": None,
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                },
            },
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --items some_file.txt python --symlink-folders"  # pylint: disable=line-too-long

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_folders_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        file_path = os.path.join(install_location, "some_file.txt")

        if pymix.can_check_links():
            self.assertFalse(os.path.islink(file_path))

        self.assertTrue(os.path.isfile(file_path))
        folder = os.path.join(install_location, "python")

        if pymix.can_check_links():
            self.assertTrue(os.path.islink(folder))

        self.assertTrue(os.path.isdir(folder))
        self.assertTrue(
            os.path.isdir(os.path.join(install_location, "python", "some_thing"))
        )

    def test_basic(self) -> None:
        """Create symlinks for each specified folder."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Symlink_test_basic_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                }
            },
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --items python --symlink"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Symlink_test_basic_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isdir(os.path.join(install_location, "python")))

        if pymix.can_check_links():
            self.assertTrue(os.path.islink(os.path.join(install_location, "python")))

        self.assertTrue(
            os.path.isdir(os.path.join(install_location, "python", "some_thing"))
        )
        self.assertTrue(
            os.path.isdir(
                os.path.join(install_location, "python", "some_thing", "inner_folder")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "__init__.py")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "some_module.py")
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "__init__.py",
                )
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "inner_module.py",
                )
            )
        )

    def test_multiple(self) -> None:
        """Create symlinks to represent egg files for Python folders."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_multiple_source_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                },
                "another": {
                    "stuff": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                },
            },
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python another --symlink"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_multiple_destination_",
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        if pymix.can_check_links():
            self.assertTrue(
                os.path.islink(os.path.join(install_location, "python.egg"))
            )

        self.assertFalse(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python")))
        self.assertFalse(
            os.path.isdir(os.path.join(install_location, "python", "some_thing"))
        )
        self.assertFalse(
            os.path.isdir(
                os.path.join(install_location, "python", "some_thing", "inner_folder")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "__init__.py")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "some_module.py")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "__init__.py",
                )
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "inner_module.py",
                )
            )
        )

        if pymix.can_check_links():
            self.assertTrue(
                os.path.islink(os.path.join(install_location, "another.egg"))
            )

        self.assertFalse(os.path.isfile(os.path.join(install_location, "another.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "another")))
        self.assertFalse(
            os.path.isdir(os.path.join(install_location, "another", "stuff"))
        )
        self.assertFalse(
            os.path.isdir(
                os.path.join(install_location, "another", "stuff", "inner_folder")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(install_location, "another", "stuff", "__init__.py")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(install_location, "another", "stuff", "some_module.py")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(
                    install_location, "another", "stuff", "inner_folder", "__init__.py"
                )
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "another",
                    "stuff",
                    "inner_folder",
                    "inner_module.py",
                )
            )
        )

    def test_single(self) -> None:
        """Create a symlink for (what would have normally been) an .egg file."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_single_directory_source_"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                }
            },
            directory,
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="utf-8"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python --symlink"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Symlink_test_single_destination_"
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        if pymix.can_check_links():
            self.assertTrue(
                os.path.islink(os.path.join(install_location, "python.egg"))
            )

        self.assertFalse(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.isdir(os.path.join(install_location, "python")))
        self.assertFalse(
            os.path.isdir(os.path.join(install_location, "python", "some_thing"))
        )
        self.assertFalse(
            os.path.isdir(
                os.path.join(install_location, "python", "some_thing", "inner_folder")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "__init__.py")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(install_location, "python", "some_thing", "some_module.py")
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "__init__.py",
                )
            )
        )
        self.assertFalse(
            os.path.isfile(
                os.path.join(
                    install_location,
                    "python",
                    "some_thing",
                    "inner_folder",
                    "inner_module.py",
                )
            )
        )
