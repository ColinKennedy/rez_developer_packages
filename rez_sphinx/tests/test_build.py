"""Make sure :ref:`rez_sphinx build` works as expected."""

import os
import unittest

from .common import package_wrap, run_test


class Build(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build` works as expected."""

    def test_hello_world(self):
        """Build documentation and auto-API .rst documentation onto disk."""
        directory = package_wrap.make_simple_developer_package()
        run_test.test('init "{directory}"'.format(directory=directory))
        run_test.test('build "{directory}"'.format(directory=directory))

        source = os.path.join(directory, "documentation", "source")
        api_source_gitignore = os.path.join(source, "api", ".gitignore")

        build = os.path.join(directory, "documentation", "build")
        master_path = os.path.join(build, "index.html")
        example_api_path = os.path.join(build, "api", "file.html")

        self.assertTrue(os.path.isfile(api_source_gitignore))
        self.assertTrue(os.path.isfile(master_path))
        self.assertTrue(os.path.isfile(example_api_path))

    def test_hello_world_other_folder(self):
        """Build documentation again, but from a different PWD."""
        raise ValueError()

    def test_intersphinx_loading(self):
        """Make sure sphinx.ext.intersphinx "sees" Rez packages as expected."""
        raise ValueError()


class Options(unittest.TestCase):
    """Make sure options (CLI, rez-config, etc) work as expected."""

    def test_auto_api_config(self):
        """Build API documentation because the rez-config says to."""
        raise ValueError()

    def test_auto_api_explicit(self):
        """Build API documentation because the CLI flag was explicitly added."""
        raise ValueError()

    def test_auto_api_implicit(self):
        """Auto-build API documentation if no CLI flag or Rez config option is set."""
        raise ValueError()

    def test_auto_api_implicit_pass(self):
        """Don't auto-build API documentation if no CLI / config / auto-detect.

        If all systems fail, just warn the user in a log and build
        documentation as normal. It would just mean that the user didn't want
        to have auto-documentation.

        """
        raise ValueError()

    def test_generate_api_config(self):
        """Build API documentation because the rez-config says to."""
        raise ValueError()

    def test_generate_api_explicit(self):
        """Build API documentation because the CLI flag was explicitly added."""
        raise ValueError()

    def test_generate_api_implicit(self):
        """Auto-build API documentation if no CLI flag or Rez config option is set."""
        raise ValueError()

    def test_generate_api_implicit_pass(self):
        """Don't auto-build API documentation if no CLI / config / auto-detect.

        If all systems fail, just warn the user in a log and build
        documentation as normal. It would just mean that the user didn't want
        to have auto-documentation.

        """
        raise ValueError()


class Invalid(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build` fails when expected."""

    def test_bad_permissions(self):
        """Fail building if the user lacks permissions to write to-disk."""
        raise ValueError()

    def test_no_package(self):
        """Fail early if no Rez package was found."""
        raise ValueError()

    def test_no_source(self):
        """Fail early if documentation source does not exist."""
        raise ValueError()

    def test_auto_api_no_python_files(self):
        """Fail to auto-build API .rst files if there's no Python files."""
        raise ValueError()
