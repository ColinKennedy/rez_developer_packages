"""Make sure :ref:`rez_sphinx init` works as expected."""

import os
import tempfile
import unittest

from python_compatibility import wrapping
from rez_utilities import finder

from rez_sphinx.core import configuration, exception

from ..common import package_wrap, run_test


class Init(unittest.TestCase):
    """Make sure :ref:`rez_sphinx init` works with expected cases."""

    def test_hello_world(self):
        """Initialize a very simple Rez package with Sphinx documentation."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)
        run_test.test(["init", directory])

        path = os.path.join(directory, "documentation", "conf.py")
        self.assertTrue(os.path.isfile(path))

    def test_hello_world_other_folder(self):
        """Initialize documentation again, but from a different PWD."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        with wrapping.keep_cwd():
            os.chdir(tempfile.gettempdir())

            run_test.test(["init", directory])

        path = os.path.join(directory, "documentation", "conf.py")
        self.assertTrue(os.path.isfile(path))


class QuickStartOptions(unittest.TestCase):
    """Make sure users can source options from the CLI / rez-config / etc."""

    def test_cli_argument(self):
        """Let the user change `sphinx-quickstart`_ options from a flag."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        run_test.test(
            "init {directory} --quickstart-arguments='--ext-coverage'".format(
                directory=directory
            )
        )

        sphinx = configuration.ConfPy.from_path(
            os.path.join(directory, "documentation", "conf.py")
        )

        self.assertIn("sphinx.ext.coverage", sphinx.get_extensions())

    def test_cli_dash_separator(self):
        """Let the user change `sphinx-quickstart`_ options from a " -- "."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        run_test.test("init {directory} -- --ext-coverage".format(directory=directory))

        sphinx = configuration.ConfPy.from_path(
            os.path.join(directory, "documentation", "conf.py")
        )

        self.assertIn("sphinx.ext.coverage", sphinx.get_extensions())

    def test_required_arguments(self):
        """Prevent users from setting things like "--project".

        That CLI argument, as well as others, are up to :ref:`rez_sphinx` to
        control.

        """
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        with self.assertRaises(exception.UserInputError):
            run_test.test("init {directory} -- --project".format(directory=directory))


class Invalids(unittest.TestCase):
    """Make sure :ref:`rez_sphinx init` fails when it's supposed to fail."""

    # TODO : Do these
    # def test_bad_permissions(self):
    #     raise ValueError()

    # def test_no_package(self):
    #     """Fail early if the user isn't in a Rez package."""
    #     raise ValueError()
    #
    # def test_no_python_files(self):
    #     """Fail early if there aren't Python files."""
    #     raise ValueError()
