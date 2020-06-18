#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check to make sure ``rez_pip_boy`` makes "source" Rez pip packages as we expect."""

import atexit
import copy
import functools
import inspect
import os
import platform
import shlex
import shutil
import tempfile
import unittest

from rez import packages
from rez_pip_boy import cli
from rez_pip_boy.core import _build_command, exceptions
from rez_utilities import creator, finder
from six.moves import mock

_BUILD_COMMAND_CODE = inspect.getsource(_build_command)


def _is_missing_python_version(version):
    """Check if the given version / version-range has a valid package."""
    return packages.get_latest_package("python", version) is None


class Integrations(unittest.TestCase):
    """Build source Rez packages, using Rez-generated pip packages."""

    def setUp(self):
        """Keep track of the user's current environment so it can be restored, later."""
        self._environment = os.environ.copy()
        os.environ["PIP_BOY_TAR_LOCATION"] = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_tar_location"
        )
        atexit.register(
            functools.partial(shutil.rmtree, os.environ["PIP_BOY_TAR_LOCATION"])
        )

    def tearDown(self):
        """Restore the user's old environment."""
        os.environ.clear()
        os.environ.update(self._environment)

    def _verify_source_package(self, directory, variants):
        """Make sure the the Rez package which ``rez_pip_boy`` converted has the expected files.

        Args:
            directory (str): The path leading to a source Rez package.
                It should contain one rezbuild.py file and one package.py file.
            variants (list[list[str]]): All Rez variations to take into account.
                e.g. [["python-2.7"]].

        """
        directory = os.path.expanduser(os.path.expandvars(directory))
        rezbuild = os.path.join(
            directory, cli._BUILD_FILE_NAME  # pylint: disable=protected-access
        )

        with open(rezbuild, "r") as handler:
            rezbuild_code = handler.read()

        package = finder.get_nearest_rez_package(directory)
        self.assertIsNotNone(package)

        self.assertEqual(_BUILD_COMMAND_CODE, rezbuild_code)
        package_variants = [map(str, variant) for variant in package.variants or []]
        self.assertEqual(variants, package_variants)
        self.assertEqual("python {root}/rezbuild.py", package.build_command)

        return package

    def _verify_installed_package(self, directory):
        """Build a Rez package and make sure it builds correctly.

        Args:
            directory (str): The absolute path where a Rez source package is defined.

        """
        install_directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_verify_installed_package"
        )
        atexit.register(functools.partial(shutil.rmtree, install_directory))

        package = finder.get_nearest_rez_package(directory)
        creator.build(package, install_directory, quiet=True)

        installed_package_directory = os.path.join(
            install_directory, package.name, str(package.version)
        )
        self.assertTrue(
            os.path.isfile(os.path.join(installed_package_directory, "package.py"))
        )
        self.assertFalse(
            os.path.isfile(os.path.join(installed_package_directory, "rezbuild.py"))
        )

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_simple(self):
        """Install a really simple pip package (a package with no dependencies)."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_simple")
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )

        source_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(source_directory, [["python-2.7"]])
        self._verify_installed_package(source_directory)

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_recurring(self):
        """Install a package and then install the same package again."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_recurring")
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )
        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )

        source_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(source_directory, [["python-2.7"]])
        self._verify_installed_package(source_directory)

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_partial_install(self):
        """Install a package, delete one of its depedencies, and then install it again."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_partial_install"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command(
            "rez_pip_boy --install importlib_metadata==1.6.0 --python-version=2.7 -- {directory}".format(  # pylint: disable=line-too-long
                directory=directory
            )
        )

        source_directory = os.path.join(directory, "importlib_metadata", "1.6.0")
        dependency = os.path.join(directory, "zipp", "1.2.0")
        self.assertTrue(os.path.isfile(os.path.join(dependency, "package.py")))
        shutil.rmtree(dependency)
        self.assertFalse(os.path.isfile(os.path.join(dependency, "package.py")))

        _run_command(
            "rez_pip_boy --install importlib_metadata==1.6.0 --python-version=2.7 -- {directory}".format(  # pylint: disable=line-too-long
                directory=directory
            )
        )
        self.assertTrue(os.path.isfile(os.path.join(dependency, "package.py")))

        self._verify_source_package(dependency, [["python-2.7", "contextlib2"]])
        self._verify_source_package(
            source_directory,
            [["python-2.7", "contextlib2", "configparser-3.5+", "pathlib2"]],
        )

    @staticmethod
    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_make_folders():
        """Make a destination folder if it doesn't exist."""
        directory = tempfile.mkdtemp(prefix="rez_pip_boy_", suffix="_test_make_folder")
        shutil.rmtree(directory)

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_regular_variants(self):
        """Make sure non-hashed variants work."""
        # Simulate a call to rez-pip where the user had written hashed_variants = False
        normal_rez_pip_arguments = {
            "commands": "env.PYTHONPATH.append('{root}/python')",
            "help": [["Home Page", u"https://github.com/jaraco/zipp"]],
            "hashed_variants": True,
            "description": u"Backport of pathlib-compatible object wrapper for zip files",
            "is_pure_python": True,
            "from_pip": True,
            "version": "1.2.0",
            "authors": [u"Jason R. Coombs (jaraco@jaraco.com)"],
            "variants": [["python-2.7", "contextlib2"]],
            "pip_name": u"zipp (1.2.0)",
            "name": u"zipp",
        }

        mocked_rez_pip_arguments = copy.copy(normal_rez_pip_arguments)
        mocked_rez_pip_arguments["hashed_variants"] = False

        import_to_mock = "rez.package_maker.PackageMaker._get_data"

        try:
            from rez import package_maker as _
        except ImportError:
            import_to_mock = "rez.package_maker__.PackageMaker._get_data"

        with mock.patch(import_to_mock) as patcher:
            patcher.return_value = mocked_rez_pip_arguments

            directory = tempfile.mkdtemp(
                prefix="rez_pip_boy_", suffix="_test_regular_variants"
            )
            atexit.register(functools.partial(shutil.rmtree, directory))

            _run_command(
                "rez_pip_boy --install zipp==1.2.0 --python-version=2.7 -- {directory}".format(
                    directory=directory
                )
            )

        source_directory = os.path.join(directory, "zipp", "1.2.0")
        self._verify_source_package(source_directory, [["python-2.7", "contextlib2"]])

    @unittest.skipIf(
        _is_missing_python_version("2.7") or _is_missing_python_version("3.6"),
        "Rez is missing Python 2.7 or 3.6",
    )
    def test_combine_variants(self):
        """Install 2 different variants and ensure the result package.py is correct."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_combine_variants"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=3.6 -- {directory}".format(
                directory=directory
            )
        )
        source_directory = os.path.join(directory, "six", "1.14.0")

        self._verify_source_package(source_directory, [["python-3.6"]])

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )

        self._verify_source_package(source_directory, [["python-3.6"], ["python-2.7"]])
        self._verify_installed_package(source_directory)

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_expanded_paths(self):
        """Ensure ~ paths will work."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_expanded_paths"
        )

        if platform.system() == "Windows":
            directory = (os.sep).join(directory.split(os.sep)[1:])
            directory = os.path.join("%USER%", directory)
        else:
            directory = "~" + directory

        atexit.register(functools.partial(shutil.rmtree, os.path.expanduser(directory)))

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )

        source_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(source_directory, [["python-2.7"]])

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_environment_variables(self):
        """Ensure $STUFF environment variable paths will work."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_environment_variables"
        )

        if platform.system() == "Windows":
            os.environ["STUFF"] = "C:"
            directory = (os.sep).join(directory.split(os.sep)[1:])
            directory = os.path.join("%STUFF%", directory)
        else:
            os.environ["STUFF"] = "~"
            directory = "$STUFF" + directory

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )

        atexit.register(
            functools.partial(
                shutil.rmtree, os.path.expanduser(os.path.expandvars(directory))
            )
        )

        source_directory = os.path.join(directory, "six", "1.14.0")
        self._verify_source_package(source_directory, [["python-2.7"]])

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_hashed_variants(self):
        """Install a Rez package using encoded (hashed) variant names."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_hashed_variants"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        os.environ["PIP_BOY_TAR_LOCATION"] = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_no_hashed_variants_tar_location"
        )
        atexit.register(
            functools.partial(shutil.rmtree, os.environ["PIP_BOY_TAR_LOCATION"])
        )

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory} --hashed-variants".format(  # pylint: disable=line-too-long
                directory=directory
            )
        )

        source_directory = os.path.join(directory, "six", "1.14.0")
        package = self._verify_source_package(source_directory, [["python-2.7"]])
        self._verify_installed_package(source_directory)
        self.assertTrue(package.hashed_variants)

        tar_directory = os.path.join(os.environ["PIP_BOY_TAR_LOCATION"], "six")

        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    tar_directory,
                    "six-1.14.0-ff5a17a870e473adea6d65972631222d54a381e6.tar.gz",
                )
            )
        )

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_no_hashed_variants(self):
        """Install a Rez package but keep each variant as a named folder."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_hashed_variants"
        )
        atexit.register(functools.partial(shutil.rmtree, directory))

        os.environ["PIP_BOY_TAR_LOCATION"] = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_no_hashed_variants_tar_location"
        )
        atexit.register(
            functools.partial(shutil.rmtree, os.environ["PIP_BOY_TAR_LOCATION"])
        )

        _run_command(
            "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory}".format(
                directory=directory
            )
        )

        source_directory = os.path.join(directory, "six", "1.14.0")
        package = self._verify_source_package(source_directory, [["python-2.7"]])
        self._verify_installed_package(source_directory)
        self.assertFalse(package.hashed_variants)

        tar_directory = os.path.join(os.environ["PIP_BOY_TAR_LOCATION"], "six")

        self.assertTrue(
            os.path.isfile(os.path.join(tar_directory, "six-1.14.0-python-2.7.tar.gz"))
        )


class Invalid(unittest.TestCase):
    """Test that invalid input is caught correctly."""

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_missing_folder(self):
        """The destination directory must exist."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_missing_folder"
        )
        shutil.rmtree(directory)

        with self.assertRaises(exceptions.MissingDestination):
            _run_command(
                "rez_pip_boy --install six==1.14.0 --python-version=2.7 -- {directory} --no-make-folders".format(  # pylint: disable=line-too-long
                    directory=directory
                )
            )

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_missing_double_dash(self):
        """Raise an exception if the user is misisng " -- "."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_missing_double_dash"
        )

        with self.assertRaises(exceptions.MissingDoubleDash):
            _run_command(
                "rez_pip_boy --install six==1.14.0 --python-version=2.7 {directory} --no-make-folders".format(  # pylint: disable=line-too-long
                    directory=directory,
                )
            )

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_multiple_double_dash(self):
        """Raise an exception if the user added " -- " 2+ times."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_multiple_double_dash"
        )

        with self.assertRaises(exceptions.DuplicateDoubleDash):
            _run_command(
                "rez_pip_boy --install six==1.14.0 -- --python-version=2.7 -- {directory} --no-make-folders".format(  # pylint: disable=line-too-long
                    directory=directory,
                )
            )

    @unittest.skipIf(_is_missing_python_version("2.7"), "Rez is missing Python 2.7")
    def test_swapped_double_dash(self):
        """Raise an exception if the user added `rez-pip` arguments to the right of the " -- "."""
        directory = tempfile.mkdtemp(
            prefix="rez_pip_boy_", suffix="_test_swapped_double_dash"
        )

        with self.assertRaises(exceptions.SwappedArguments):
            _run_command(
                "rez_pip_boy {directory} --no-make-folders -- --install six==1.14.0 --python-version=2.7".format(  # pylint: disable=line-too-long
                    directory=directory,
                )
            )


def _run_command(command):
    """Syntax sugar. Run `command` silently."""
    items = shlex.split(command)

    if items[0] == "rez_pip_boy":
        items = items[1:]

    cli.main(items)
