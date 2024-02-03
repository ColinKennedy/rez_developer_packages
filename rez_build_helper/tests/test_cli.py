#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from .common import common, creator, finder, pymix


class Cli(unittest.TestCase):
    """Make sure the basic CLI functions work as-expected."""

    def test_empty(self):
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

    def test_copy(self):
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


class Symlink(unittest.TestCase):
    """Make sure symlinks generate as expected."""

    def test_files(self):
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

    def test_folders(self):
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

    def test_basic(self):
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

    def test_multiple(self):
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

    def test_single(self):
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
