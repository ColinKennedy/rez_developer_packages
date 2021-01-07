#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All tests related to generating Python .egg files."""

import atexit
import functools
import os
import shutil
import sys
import tempfile
import textwrap
import unittest
import zipfile

import pkg_resources
from python_compatibility import wrapping
from rez_build_helper import exceptions, filer

from .common import common, creator, finder


class Egg(unittest.TestCase):
    """Make sure .egg generation works as expected."""

    @classmethod
    def setUpClass(cls):
        """Copy over dependent packages so rez_build_helper resolves to the latest version.

        If a user sets their REZ_PACKAGES_PATH in their shell start-up
        scripts, it causes tests to fail. So this block of code copies
        packages into a temporary location so that they can be used in
        place of the user's packages_path, so that tests will always
        can be made to pass.

        """
        build_package = finder.get_nearest_rez_package(
            os.environ["REZ_REZ_BUILD_HELPER_ROOT"]
        )
        build_path = os.path.dirname(
            os.path.dirname(finder.get_package_root(build_package))
        )
        directory = tempfile.mkdtemp(suffix="_test_egg_Egg_folder")
        atexit.register(functools.partial(shutil.rmtree, directory))

        for name in ("arch", "os", "platform", "python", "rez", "setuptools", "six"):
            package = finder.get_nearest_rez_package(
                os.environ["REZ_{name}_ROOT".format(name=name.upper())]
            )
            root = os.path.dirname(finder.get_package_root(package))
            path = os.path.dirname(root)
            destination = os.path.join(directory, os.path.relpath(root, path))

            if not os.path.isdir(destination):
                os.makedirs(destination)
                copytree(root, destination)

        cls._packages_path = [build_path, directory]

    def setUp(self):
        """Keep track of the users loadable Python paths so it can be reverted."""
        self._paths = list(sys.path)

    def tearDown(self):
        """Restore the old set of loadable Python paths."""
        sys.path[:] = self._paths

    def test_extra_metadata(self):
        """Make sure platform data is recorded, if it is included in requires."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_extra_metadata_directory_"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {"__init__.py": None, "inner_module.py": None,},
                    }
                }
            },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    description = "A test packages for rez_build_helper"

                    help = "http://www.some_home_page.com"

                    authors = ["ColinKennedy"]

                    requires = ["platform-linux", "python-3.6+<3.8"]

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_extra_metadata_destination_"
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(
            package, destination, quiet=True, packages_path=self._packages_path
        )
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.islink(os.path.join(install_location, "python.egg")))
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

        egg = zipfile.ZipFile(os.path.join(install_location, "python.egg"), "r")
        self.assertEqual(
            {
                "EGG-INFO/PKG-INFO",
                "EGG-INFO/SOURCES.txt",
                "EGG-INFO/dependency_links.txt",
                "EGG-INFO/zip-safe",
                "EGG-INFO/top_level.txt",
                "some_thing/__init__.py",
                "some_thing/__pycache__/__init__.cpython-36.pyc",
                "some_thing/__pycache__/some_module.cpython-36.pyc",
                "some_thing/inner_folder/__init__.py",
                "some_thing/inner_folder/__pycache__/__init__.cpython-36.pyc",
                "some_thing/inner_folder/__pycache__/inner_module.cpython-36.pyc",
                "some_thing/inner_folder/inner_module.py",
                "some_thing/some_module.py",
            },
            {item.filename for item in egg.filelist},
        )
        package_information = textwrap.dedent(
            """\
            Metadata-Version: 1.2
            Name: some-package
            Version: 1.0.0
            Summary: A test packages for rez_build_helper
            Home-page: http://www.some_home_page.com
            Author: ColinKennedy
            License: UNKNOWN
            Description: UNKNOWN
            Platform: linux
            Requires-Python: 3.6+<3.8
            """
        )
        self.assertEqual(
            package_information, egg.open("EGG-INFO/PKG-INFO").read().decode("utf-8"),
        )

    def test_import_pkg_resources(self):
        """Make sure a generated .egg file can be imported via pkg_resources."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_import_pkg_resources_directory_"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "another_file.dat": None,
                        "some_module.py": None,
                        "inner_folder": {"__init__.py": None, "inner_module.py": None,},
                    }
                }
            },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    description = "A test packages for rez_build_helper"

                    help = "http://www.some_home_page.com"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_pkg_resources_destination_"
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        with wrapping.keep_sys_path():
            sys.path.append(os.path.join(install_location, "python.egg"))
            egg = zipfile.ZipFile(os.path.join(install_location, "python.egg"), "r")
            pkg_resources.resource_filename("some_thing", "another_file.dat")

        egg = zipfile.ZipFile(os.path.join(install_location, "python.egg"), "r")
        self.assertIn(
            "some_thing/another_file.dat", {item.filename for item in egg.filelist}
        )

    def test_single(self):
        """Create a collapsed .egg file for a Python folder."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_single_directory_",
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {"__init__.py": None, "inner_module.py": None,},
                    }
                }
            },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    description = "A test packages for rez_build_helper"

                    help = "http://www.some_home_page.com"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_single_destination_"
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(
            package, destination, quiet=True, packages_path=self._packages_path
        )
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertTrue(os.path.isfile(os.path.join(install_location, "python.egg")))
        self.assertFalse(os.path.islink(os.path.join(install_location, "python.egg")))
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

        egg = zipfile.ZipFile(os.path.join(install_location, "python.egg"), "r")
        self.assertEqual(
            {
                "EGG-INFO/PKG-INFO",
                "EGG-INFO/SOURCES.txt",
                "EGG-INFO/dependency_links.txt",
                "EGG-INFO/zip-safe",
                "EGG-INFO/top_level.txt",
                "some_thing/__init__.py",
                "some_thing/__pycache__/__init__.cpython-36.pyc",
                "some_thing/__pycache__/some_module.cpython-36.pyc",
                "some_thing/inner_folder/__init__.py",
                "some_thing/inner_folder/__pycache__/__init__.cpython-36.pyc",
                "some_thing/inner_folder/__pycache__/inner_module.cpython-36.pyc",
                "some_thing/inner_folder/inner_module.py",
                "some_thing/some_module.py",
            },
            {item.filename for item in egg.filelist},
        )
        package_information = textwrap.dedent(
            """\
            Metadata-Version: 1.0
            Name: some-package
            Version: 1.0.0
            Summary: A test packages for rez_build_helper
            Home-page: http://www.some_home_page.com
            Author: UNKNOWN
            Author-email: UNKNOWN
            License: UNKNOWN
            Description: UNKNOWN
            Platform: any
            """
        )
        self.assertEqual(
            package_information, egg.open("EGG-INFO/PKG-INFO").read().decode("utf-8"),
        )
        self.assertEqual("some_thing\n", egg.open("EGG-INFO/top_level.txt").read().decode("utf-8"))

    def test_multiple(self):
        """Create more than one collapsed egg files for a Python folder."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_multiple_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_thing": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {"__init__.py": None, "inner_module.py": None,},
                    }
                },
                "another": {
                    "stuff": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {"__init__.py": None, "inner_module.py": None,},
                    }
                },
            },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python another"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_multiple_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        self.assertFalse(os.path.islink(os.path.join(install_location, "python.egg")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python.egg")))
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

        self.assertFalse(os.path.islink(os.path.join(install_location, "another.egg")))
        self.assertTrue(os.path.isfile(os.path.join(install_location, "another.egg")))
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

    def test_invalid(self):
        """Disallow non-root folders for .egg generation."""
        directory = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_invalid_directory_"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))
        destination = tempfile.mkdtemp(
            prefix="rez_build_helper_Egg_test_invalid_destination"
        )
        atexit.register(functools.partial(shutil.rmtree, destination))

        with self.assertRaises(exceptions.NonRootItemFound):
            filer.build(directory, destination, ["/asdf/asdf"], eggs=["foo/bar"])

    def test_loadable(self):
        """Create a Python package .egg file and make sure it'source_ importable."""
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_loadable_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_package": {
                        "__init__.py": None,
                        "some_module.py": None,
                        "inner_folder": {"__init__.py": None, "inner_module.py": None,},
                    }
                }
            },
            directory,
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Cli_test_loadable_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        egg_file = os.path.join(install_location, "python.egg")
        self.assertTrue(os.path.isfile(os.path.join(install_location, "python.egg")))

        # Make the python.egg importable
        sys.path.append(egg_file)

        from some_package import some_module  # pylint: disable=import-error

        self.assertEqual(
            os.path.join(
                install_location, "python.egg", "some_package", "some_module.py"
            ),
            os.path.realpath(some_module.__file__),
        )


def copytree(source, destination, symlinks=False, ignore=None):
    """Copy `source` into `destination`.

    Why is this not just default behavior. Guido, explain yourself!

    Reference:
        https://stackoverflow.com/a/12514470/3626104

    Args:
        source (str):
            The folder to copy from.
        destination (str):
            The folder to copy into.
        symlinks (bool, optional):
            If True, copy through symlinks. If False, copy just the
            symlink. Default is False.
        ignore (set[str], optional):
            The names of the files/folders to ignore during copy.

    """
    for item in os.listdir(source):
        source_ = os.path.join(source, item)
        destination_ = os.path.join(destination, item)

        if os.path.isdir(source_):
            shutil.copytree(source_, destination_, symlinks, ignore)
        else:
            shutil.copy2(source_, destination_)
