#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check to make sure ``rez_pip_boy`` makes "source" Rez pip packages as we expect."""

import atexit
import shlex
import functools
import shutil
import tempfile
import subprocess
import inspect
import os
import unittest

from rez_utilities import creator, inspection
from rez_pip_boy import cli
from rez_pip_boy.core import _build_command, exceptions

_BUILD_COMMAND_CODE = inspect.getsource(_build_command)


class Integrations(unittest.TestCase):
    """Build source Rez packages, using Rez-generated pip packages."""

    def _verify_source_package(self, directory):
        """Make sure the the Rez package which ``rez_pip_boy`` converted has the expected files."""
        package = os.path.join(directory, "package.py")
        rezbuild = os.path.join(directory, "rezbuild.py")

        with open(rezbuild, "r") as handler:
            rezbuild_code = handler.read()

        with open(package, "r") as handler:
            package_code = handler.readlines()

        self.assertEqual(_BUILD_COMMAND_CODE, rezbuild_code)
        self.assertIn("build_command = 'python {root}/rezbuild.py'\n", package_code)

    def _verify_installed_package(self, directory):
        """Build a Rez package and make sure it builds correctly.

        Args:
            directory (str): The absolute path where a Rez source package is defined.

        """
        install_directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_verify_installed_package")
        atexit.register(functools.partial(shutil.rmtree, install_directory))

        package = inspection.get_nearest_rez_package(directory)
        creator.build(package, install_directory)

        installed_package_directory = os.path.join(install_directory, package.name, str(package.version))
        self.assertTrue(os.path.isfile(os.path.join(installed_package_directory, "package.py")))
        self.assertFalse(os.path.isfile(os.path.join(installed_package_directory, "rezbuild.py")))

    def test_simple(self):
        """Install a really simple pip package (a package with no dependencies)."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_simple")
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command('rez_pip_boy "--install six==1.14.0 --python-version=3.7" {directory}'.format(directory=directory))

        source_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(source_directory)
        self._verify_installed_package(source_directory)

    # def test_complex_001(self):
    #     """Install a package with many dependencies and make sure each one is installed."""
    #     pass
    #
    # def test_complex_002(self):
    #     """Install another package."""
    #     pass

    def test_recurring(self):
        """Install a package and then install the same package again."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_recurring")
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command('rez_pip_boy "--install six==1.14.0 --python-version=3.7" {directory}'.format(directory=directory))
        _run_command('rez_pip_boy "--install six==1.14.0 --python-version=3.7" {directory}'.format(directory=directory))

        source_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(source_directory)
        self._verify_installed_package(source_directory)

    def test_partial_install(self):
        """Install a package, delete one of its depedencies, and then install it again."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_partial_install")
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command('rez_pip_boy "--install importlib_metadata==1.6.0 --python-version=3.7" {directory}'.format(directory=directory))

        source_directory = os.path.join(directory, "importlib_metadata", "1.6.0")
        dependency = os.path.join(directory, "zipp", "1.2.0")
        self.assertTrue(os.path.isfile(os.path.join(dependency, "package.py")))
        shutil.rmtree(dependency)
        self.assertFalse(os.path.isfile(os.path.join(dependency, "package.py")))

        _run_command('rez_pip_boy "--install importlib_metadata==1.6.0 --python-version=3.7" {directory}'.format(directory=directory))
        self.assertTrue(os.path.isfile(os.path.join(dependency, "package.py")))

        self._verify_source_package(dependency)
        self._verify_installed_package(dependency)
        self._verify_source_package(source_directory)
        self._verify_installed_package(source_directory)

    def test_make_folder(self):
        """Make a destination folder if it doesn't exist."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_make_folder")
        shutil.rmtree(directory)

        _run_command('rez_pip_boy "--install six==1.14.0 --python-version=3.7" {directory} --make-folders'.format(directory=directory))

    # def test_hashed_variants(self):
    #     """Make sure hashed variants work."""
    #     pass
    #
    # def test_regular_variants(self):
    #     """Make sure non-hashed variants work."""
    #     pass
    #
    def test_combine_variants(self):
        """Install 2 different variants and ensure the result package.py is correct."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_simple")
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command('rez_pip_boy "--install six==1.14.0 --python-version=3.7" {directory}'.format(directory=directory))
        _run_command('rez_pip_boy "--install six==1.14.0 --python-version=2.7" {directory}'.format(directory=directory))

        source_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(source_directory)
        self._verify_installed_package(source_directory)

        package = inspection.get_nearest_rez_package(source_directory)

        expected = [["python-3.7"], ["python-2.7"]]
        variants = [map(str, variant) for variant in package.variants or []]
        self.assertEqual(expected, variants)


class Invalid(unittest.TestCase):
    """Test that invalid input is caught correctly."""

    def test_missing_folder(self):
        """The destination directory must exist."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_missing_folder")
        shutil.rmtree(directory)

        with self.assertRaises(exceptions.MissingDestination):
            _run_command('rez_pip_boy "--install six==1.14.0 --python-version=3.7" {directory}'.format(directory=directory))


def _run_command(command):
    """Syntax sugar. Run `command` silently."""
    items = shlex.split(command)

    if items[0] == "rez_pip_boy":
        items = items[1:]

    cli.main(items)
