"""Make sure :ref:`rez_sphinx config` works."""

from __future__ import print_function

import textwrap
import unittest

from python_compatibility import wrapping
from six.moves import mock

from rez_sphinx.core import exception
from rez_sphinx.preferences import preference, preference_help

from .common import run_test


class Check(unittest.TestCase):
    """Make sure :ref:`rez_sphinx config check` works."""

    def test_invalid(self):
        """Report that the user's applied overrides are invalid."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = "not valid"

            with self.assertRaises(
                exception.ConfigurationError
            ), wrapping.silence_printing():
                run_test.test("config check")

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["enable_apidoc"] = None

            with self.assertRaises(
                exception.ConfigurationError
            ), wrapping.silence_printing():
                run_test.test("config check")

    def test_valid(self):
        """Report success if the applied overrides are okay."""
        with wrapping.silence_printing():
            run_test.test("config check")

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["sphinx-apidoc"] = dict()
            config.optionvars["rez_sphinx"]["sphinx-apidoc"]["enable_apidoc"] = False

            with wrapping.silence_printing():
                run_test.test("config check")


class ListDefault(unittest.TestCase):
    """Make sure :ref:`rez_sphinx config list-default` works."""

    def test_format_sparse(self):
        """Print to yaml, instead of as Python objects."""
        with mock.patch("builtins.print") as patch:
            run_test.test("config list-default --sparse --format yaml")

        args, kwargs = patch.call_args
        actual = args[0]
        expected = textwrap.dedent(
            """\
            api_toctree_line: ''
            auto_help: {}
            build_documentation_key: ''
            documentation_root: ''
            extra_requires: []
            init_options: {}
            sphinx-apidoc: {}
            sphinx-quickstart: []
            sphinx_conf_overrides: {}
            sphinx_extensions: []
            """
        )

        self.assertEqual(expected, actual)

    def test_normal(self):
        """Print default :ref:`rez_sphinx` settings."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["sphinx-apidoc"] = dict()
            # Set a non-default value
            config.optionvars["rez_sphinx"]["sphinx-apidoc"]["enable_apidoc"] = False

            with mock.patch("pprint.pprint") as patch:
                run_test.test("config list-default")

        args, kwargs = patch.call_args
        actual = args[0]
        expected = {
            "api_toctree_line": "API Documentation <api/modules>",
            "auto_help": {
                "filter_by": preference_help.DEFAULT_FILTER,
                "sort_order": preference_help.DEFAULT_SORT,
            },
            "build_documentation_key": "build_documentation",
            "documentation_root": "documentation",
            "extra_requires": [],
            "init_options": {"default_files": preference._DEFAULT_ENTRIES},
            "sphinx-apidoc": {'allow_apidoc_templates': True, 'enable_apidoc': True},
            "sphinx_conf_overrides": {"add_module_names": False},
            "sphinx_extensions": [
                "sphinx.ext.autodoc",
                "sphinx.ext.intersphinx",
                "sphinx.ext.viewcode",
            ],
            "sphinx-quickstart": [],
        }

        self.assertEqual(expected, actual)

    def test_sparse(self):
        """Print default :ref:`rez_sphinx` settings."""
        value = False  # The default value is `True`

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["sphinx-apidoc"] = dict()
            config.optionvars["rez_sphinx"]["sphinx-apidoc"]["enable_apidoc"] = value

            with mock.patch("pprint.pprint") as patch:
                run_test.test("config list-default --sparse")

        args, kwargs = patch.call_args
        actual = args[0]
        expected = {
            "documentation_root": "",
            "init_options": {},
            "sphinx_conf_overrides": {},
            "sphinx_extensions": [],
            "sphinx-apidoc": dict(),
            "extra_requires": [],
            "sphinx-quickstart": [],
            "build_documentation_key": "",
            "auto_help": {},
            "api_toctree_line": "",
        }

        self.assertEqual(expected, actual)


class ListOverrides(unittest.TestCase):
    """Make sure :ref:`rez_sphinx config list-overrides` works."""

    def test_applied(self):
        """Print the applied user settings."""
        raise ValueError()

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["enable_apidoc"] = False

            run_test.test("config list")

    def test_invalid(self):
        """Report that the user's applied overrides are invalid."""
        raise ValueError()
