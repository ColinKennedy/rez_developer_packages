#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All tests related to generating Python .egg files."""

from __future__ import unicode_literals

import atexit
import functools
import io
import os
import shutil
import sys
import tempfile
import textwrap
import zipfile

import pkg_resources
from python_compatibility import wrapping

from rez_build_helper import exceptions, filer

from .common import common, creator, finder, pymix, rez_configuration

_IS_PYTHON_2 = sys.version_info.major == 2
_INFO = sys.version_info
_REZ_PLATFORM = rez_configuration.get_current_platform_as_rez_name()
_REZ_PYTHON_VERSION = os.environ["REZ_PYTHON_VERSION"]
_VERSION = "{_INFO.major}.{_INFO.minor}.{_INFO.micro}".format(_INFO=_INFO)


class Egg(common.Common):
    """Make sure .egg generation works as expected."""

    def setUp(self):
        """Keep track of the users loadable Python paths so it can be reverted."""
        super(Egg, self).setUp()  # pylint: disable=super-with-arguments

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
                        "inner_folder": {
                            "__init__.py": None,
                            "inner_module.py": None,
                        },
                    }
                }
            },
            directory,
        )

        template = textwrap.dedent(
            """\
            name = "some_package"

            version = "1.0.0"

            description = "A test packages for rez_build_helper"

            help = "http://www.some_home_page.com"

            authors = ["ColinKennedy"]

            requires = ["platform-%s", "python-%s"]

            private_build_requires = ["rez_build_helper"]

            build_command = "python -m rez_build_helper --eggs python"

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
            """
        )

        with io.open(
            os.path.join(directory, "package.py"), "w", encoding="ascii"
        ) as handler:
            handler.write(template % (_REZ_PLATFORM, _REZ_PYTHON_VERSION))

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

        if pymix.can_check_links():
            self.assertFalse(
                os.path.islink(os.path.join(install_location, "python.egg"))
            )

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

        with zipfile.ZipFile(os.path.join(install_location, "python.egg"), "r") as egg:
            found_package_information = _get_package_information(egg)

        _py = functools.partial(
            _format_version,
            "{sys.version_info.major}{sys.version_info.minor}".format(sys=sys),
        )

        expected = {
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/SOURCES.txt",
            "EGG-INFO/dependency_links.txt",
            "EGG-INFO/top_level.txt",
            "EGG-INFO/zip-safe",
            "some_thing/__init__.py",
            "some_thing/inner_folder/__init__.py",
            "some_thing/inner_folder/inner_module.py",
            "some_thing/some_module.py",
            _py("some_thing/__pycache__/__init__.cpython-{}.pyc"),
            _py("some_thing/__pycache__/some_module.cpython-{}.pyc"),
            _py("some_thing/inner_folder/__pycache__/__init__.cpython-{}.pyc"),
            _py("some_thing/inner_folder/__pycache__/inner_module.cpython-{}.pyc"),
        }

        if _IS_PYTHON_2:
            expected = {
                "EGG-INFO/PKG-INFO",
                "EGG-INFO/SOURCES.txt",
                "EGG-INFO/dependency_links.txt",
                "EGG-INFO/top_level.txt",
                "EGG-INFO/zip-safe",
                "some_thing/__init__.py",
                "some_thing/inner_folder/__init__.py",
                "some_thing/inner_folder/inner_module.py",
                "some_thing/some_module.py",
                "some_thing/__init__.pyc",
                "some_thing/inner_folder/__init__.pyc",
                "some_thing/inner_folder/inner_module.pyc",
                "some_thing/some_module.pyc",
            }

        self.assertEqual(expected, {item.filename for item in egg.filelist})

        expected_package_information = [
            "Metadata-Version: 1.2",
            "Name: some-package",
            "Version: 1.0.0",
            "Summary: A test packages for rez_build_helper",
            "Home-page: http://www.some_home_page.com",
            "Author: ColinKennedy",
            "License: UNKNOWN",
            "Description: UNKNOWN",
            "Platform: {_REZ_PLATFORM}".format(_REZ_PLATFORM=_REZ_PLATFORM),
            "Requires-Python: =={_VERSION}".format(_VERSION=_VERSION),
        ]

        self.assertEqual(expected_package_information, found_package_information)

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
            os.path.join(directory, "package.py"), "w", encoding="ascii"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    description = "A test packages for rez_build_helper"

                    help = "http://www.some_home_page.com"

                    requires = ["platform-%s", "python-%s"]

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
                % (_REZ_PLATFORM, _REZ_PYTHON_VERSION)
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

            with zipfile.ZipFile(
                os.path.join(install_location, "python.egg"), "r"
            ) as egg:
                pkg_resources.resource_filename("some_thing", "another_file.dat")

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
            os.path.join(directory, "package.py"), "w", encoding="ascii"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    description = "A test packages for rez_build_helper"

                    authors = ["ColinKennedy"]

                    help = "http://www.some_home_page.com"

                    requires = ["platform-%s", "python-%s"]

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
                % (_REZ_PLATFORM, _REZ_PYTHON_VERSION)
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

        if pymix.can_check_links():
            self.assertFalse(
                os.path.islink(os.path.join(install_location, "python.egg"))
            )

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

        _py = functools.partial(
            _format_version,
            "{sys.version_info.major}{sys.version_info.minor}".format(sys=sys),
        )

        with zipfile.ZipFile(os.path.join(install_location, "python.egg"), "r") as egg:
            found_package_information = _get_package_information(egg)

            with egg.open("EGG-INFO/top_level.txt") as handler:
                found_top_level = handler.read().decode("ascii")

        expected = {
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/SOURCES.txt",
            "EGG-INFO/dependency_links.txt",
            "EGG-INFO/top_level.txt",
            "EGG-INFO/zip-safe",
            "some_thing/__init__.py",
            "some_thing/inner_folder/__init__.py",
            "some_thing/inner_folder/inner_module.py",
            "some_thing/some_module.py",
            _py("some_thing/__pycache__/__init__.cpython-{}.pyc"),
            _py("some_thing/__pycache__/some_module.cpython-{}.pyc"),
            _py("some_thing/inner_folder/__pycache__/__init__.cpython-{}.pyc"),
            _py("some_thing/inner_folder/__pycache__/inner_module.cpython-{}.pyc"),
        }

        if _IS_PYTHON_2:
            expected = {
                "EGG-INFO/PKG-INFO",
                "EGG-INFO/SOURCES.txt",
                "EGG-INFO/dependency_links.txt",
                "EGG-INFO/top_level.txt",
                "EGG-INFO/zip-safe",
                "some_thing/__init__.py",
                "some_thing/__init__.pyc",
                "some_thing/inner_folder/__init__.py",
                "some_thing/inner_folder/__init__.pyc",
                "some_thing/inner_folder/inner_module.py",
                "some_thing/inner_folder/inner_module.pyc",
                "some_thing/some_module.py",
                "some_thing/some_module.pyc",
            }

        self.assertEqual(expected, {item.filename for item in egg.filelist})
        expected_package_information = [
            "Metadata-Version: 1.2",
            "Name: some-package",
            "Version: 1.0.0",
            "Summary: A test packages for rez_build_helper",
            "Home-page: http://www.some_home_page.com",
            "Author: ColinKennedy",
            "License: UNKNOWN",
            "Description: UNKNOWN",
            "Platform: windows",
            "Requires-Python: =={_VERSION}".format(_VERSION=_VERSION),
        ]

        if _IS_PYTHON_2:
            expected_package_information = [
                "Metadata-Version: 1.2",
                "Name: some-package",
                "Version: 1.0.0",
                "Summary: A test packages for rez_build_helper",
                "Home-page: http://www.some_home_page.com",
                "Author: ColinKennedy",
                "License: UNKNOWN",
                "Description: UNKNOWN",
                "Platform: windows",
                "Requires-Python: =={_VERSION}".format(_VERSION=_VERSION),
            ]

        self.assertEqual(expected_package_information, found_package_information)
        self.assertEqual("some_thing\n", found_top_level)

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
            os.path.join(directory, "package.py"), "w", encoding="ascii"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    requires = ["platform-%s", "python-%s"]

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python another"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python.egg"))
                    """
                )
                % (_REZ_PLATFORM, _REZ_PYTHON_VERSION)
            )

        package = finder.get_nearest_rez_package(directory)
        destination = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_multiple_")
        atexit.register(functools.partial(shutil.rmtree, destination))

        creator.build(package, destination, quiet=True)
        install_location = os.path.join(destination, "some_package", "1.0.0")

        if pymix.can_check_links():
            self.assertFalse(
                os.path.islink(os.path.join(install_location, "python.egg"))
            )

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

        if pymix.can_check_links():
            self.assertFalse(
                os.path.islink(os.path.join(install_location, "another.egg"))
            )

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
        directory = tempfile.mkdtemp(prefix="rez_build_helper_Egg_test_loadable_")
        atexit.register(functools.partial(shutil.rmtree, directory))

        common.make_files(
            {
                "python": {
                    "some_package": {
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
            os.path.join(directory, "package.py"), "w", encoding="ascii"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"

                    version = "1.0.0"

                    description = "A test packages for rez_build_helper"

                    requires = ["platform-%s", "python-%s"]

                    private_build_requires = ["rez_build_helper"]

                    build_command = "python -m rez_build_helper --eggs python"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
                % (_REZ_PLATFORM, _REZ_PYTHON_VERSION)
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

        from some_package import (  # pylint: disable=import-outside-toplevel,import-error
            some_module,
        )

        some_module_path = os.path.join(
            install_location, "python.egg", "some_package", "some_module.py"
        )

        self.assertIn(
            os.path.realpath(some_module.__file__),
            {
                some_module_path,
                some_module_path + "c",  # some_module.pyc
            },
        )


def _format_version(version, text):
    """Add ``version`` to ``text``.

    Args:
        version (str): A Python version. e.g. ``"36"``.
        text (str): Some text to replace. e.g. ``"Foo {}"``.

    Returns:
        str: The formatted text, ``"Foo 36"``.

    """
    return text.format(version)


def _get_package_information(egg):
    """Read ``egg`` for file contents.

    Args:
        egg (handler): An open, read-mode file to check for contents.

    Returns:
        list[str]: The found file paths, if any.

    """
    text = egg.open("EGG-INFO/PKG-INFO").read().decode("ascii")
    output = []

    for line in text.split("\n"):
        line = line.strip()

        if line:
            output.append(line)

    return output
