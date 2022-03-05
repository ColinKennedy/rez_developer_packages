"""Make sure :ref:`rez_sphinx init` works as expected."""

import unittest
import tempfile
import textwrap
import os

from python_compatibility import wrapping
from rez_utilities import finder
from rez_sphinx.core import configuration, exception
from rez_sphinx.preferences import preference_init

from .common import package_wrap, run_test


class AutoFiles(unittest.TestCase):
    def test_custom_files(self):
        raise ValueError()

    def test_default_files(self):
        """Make sure :ref:`rez_sphinx` makes example starting files for the user."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)
        run_test.test(["init", directory])

        developer = os.path.join(directory, "documentation", "source", "developer_documentation.rst")

        with open(developer, "r") as handler:
            developer_text = handler.read()

        user = os.path.join(directory, "documentation", "source", "user_documentation.rst")

        with open(user, "r") as handler:
            user_text = handler.read()

        master_text = _get_base_master_index_text(os.path.join(directory, "documentation", "source", "index.rst"))

        self.assertEqual(
            textwrap.dedent(
                """\
                User Documentation
                ==================

                ..
                    rez_sphinx_help:User Documentation

                This auto-generated file is meant to be written by the developer. Please
                provide anything that could be useful to the reader such as:

                - General Overview
                - A description of who the intended audience is (developers, artists, etc)
                - Tutorials
                - "Cookbook" style tutorials
                - Table Of Contents (toctree) to other Sphinx pages
                """
            ),
            user_text,
        )
        self.assertEqual(
            textwrap.dedent(
                """\
                Developer Documentation
                =======================

                ..
                    rez_sphinx_help:Developer Documentation

                This auto-generated file is meant to be written by the developer. Please
                provide anything that could be useful to the reader such as:

                - General Overview
                - A description of who the intended audience is (developers, artists, etc)
                - Tutorials
                - "Cookbook" style tutorials
                - Table Of Contents (toctree) to other Sphinx pages
                """
            ),
            developer_text,
        )
        raise ValueError(master_text)
        self.assertEqual(
            textwrap.dedent(
                """\
                Welcome to some_package's documentation!
                ========================================

                .. toctree::
                   :maxdepth: 2
                   :caption: Contents:

                   developer_documentation
                   user_documentation

                Indices and tables
                ==================

                * :ref:`genindex`
                * :ref:`modindex`
                * :ref:`search`"""
            ),
            master_text,
        )

    def test_enforce_non_default_text(self):
        raise ValueError()

    def test_no_files(self):
        raise ValueError()


class Init(unittest.TestCase):
    """Make sure :ref:`rez_sphinx init` works with expected cases."""

    def test_hello_world(self):
        """Initialize a very simple Rez package with Sphinx documentation."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)
        run_test.test(["init", directory])

    def test_hello_world_other_folder(self):
        """Initialize documentation again, but from a different PWD."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        with wrapping.keep_cwd():
            os.chdir(tempfile.gettempdir())

            run_test.test(["init", directory])


class QuickStartOptions(unittest.TestCase):
    """Make sure users can source options from the CLI / rez-config / etc."""

    def test_cli_argument(self):
        """Let the user change :ref:`sphinx-quickstart` options from a flag."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        run_test.test(
            "init {directory} --quickstart-arguments='--ext-coverage'".format(
                directory=directory
            )
        )

        sphinx = configuration.ConfPy.from_path(
            os.path.join(directory, "documentation", "source", "conf.py")
        )

        self.assertIn("sphinx.ext.coverage", sphinx.get_extensions())

    def test_cli_dash_separator(self):
        """Let the user change :ref:`sphinx-quickstart` options from a " -- "."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        run_test.test("init {directory} -- --ext-coverage".format(directory=directory))

        sphinx = configuration.ConfPy.from_path(
            os.path.join(directory, "documentation", "source", "conf.py")
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


def _get_base_master_index_text(path):
    """Get the text from ``path`` but without any top-level Sphinx comments.

    Args:
        path (str): The absolute or relative path to a Sphinx :ref:`index.rst` on disk.

    Returns:
        str: The document body of ``path``.

    """
    with open(path, "r") as handler:
        lines = handler.read().splitlines()

    raise ValueError(lines)

    found = -1

    for index, line in enumerate(lines):
        if line.startswith("Welcome to "):
            found = index

            break
    else:
        raise RuntimeError('No title line was found')

    return "\n".join(lines[found:])
