"""Make sure :ref:`rez_sphinx config` works."""

from __future__ import print_function

import ast
import contextlib
import textwrap
import unittest

import schema
import yaml
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
            config.optionvars["rez_sphinx"]["sphinx-apidoc"] = dict()
            config.optionvars["rez_sphinx"]["sphinx-apidoc"]["enable_apidoc"] = None

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
    """Make sure :ref:`rez_sphinx config list-defaults` works."""

    def test_format_sparse(self):
        """Print to `yaml`_, instead of as Python objects."""
        with mock.patch("builtins.print") as patch:
            run_test.test("config list-defaults --sparse --format yaml")

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
                run_test.test("config list-defaults")

        args, kwargs = patch.call_args
        actual = args[0]
        expected = {
            "auto_help": {
                "filter_by": preference_help.DEFAULT_FILTER,
                "sort_order": preference_help.DEFAULT_SORT,
            },
            "api_toctree_line": "API Documentation <api/modules>",
            "build_documentation_key": "build_documentation",
            "documentation_root": "documentation",
            "extra_requires": [],
            "init_options": {
                "default_files": preference._DEFAULT_ENTRIES,
                "check_default_files": True,
            },
            "sphinx-apidoc": {"allow_apidoc_templates": True, "enable_apidoc": True},
            "sphinx_conf_overrides": {"add_module_names": False, "master_doc": "index"},
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
                run_test.test("config list-defaults --sparse")

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


# TODO : Need tests for
# - format yaml
# - overrides only
#  - Need to work flat but also for nested structures
# - overrides + everything


class ListOverrides(unittest.TestCase):
    """Make sure :ref:`rez_sphinx config list-overrides` works."""

    def test_applied(self):
        """Print all current settings."""
        with _example_override(), wrapping.silence_printing():
            run_test.test("config list-overrides")

    def test_complex_types(self):
        """Make sure nested objects with non-dict types override correctly."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["init_options"] = dict()
            config.optionvars["rez_sphinx"]["init_options"]["default_files"] = []

            with wrapping.capture_pipes() as (stdout, _):
                run_test.test("config list-overrides --sparse")

        value = stdout.getvalue()
        stdout.close()
        data = ast.literal_eval(value)

        self.assertEqual({"init_options": {"default_files": []}}, data)

    def test_invalid(self):
        """Report that the user's applied overrides are invalid."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = "invalid thing"

            with self.assertRaises(schema.SchemaUnexpectedTypeError):
                run_test.test("config list-overrides")

    def test_sparse(self):
        """Print only the user's overwritten settings."""
        with wrapping.capture_pipes() as (stdout, _), _example_override():
            run_test.test("config list-overrides --sparse")

        value = stdout.getvalue()
        stdout.close()
        data = ast.literal_eval(value)

        self.assertEqual({"sphinx-apidoc": {"enable_apidoc": False}}, data)

    def test_yaml(self):
        """Ensure `yaml`_ outputting works as expected."""
        with wrapping.capture_pipes() as (stdout, _), _example_override():
            run_test.test("config list-overrides --sparse --format yaml")

        value = stdout.getvalue()
        stdout.close()
        data = yaml.safe_load(value)

        self.assertEqual({"sphinx-apidoc": {"enable_apidoc": False}}, data)


class Show(unittest.TestCase):
    """Make sure :ref:`rez_sphinx config show` works."""

    def test_names(self):
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test("config show documentation_root extra_requires")

        value = stdout.getvalue()
        stdout.close()

        self.assertEqual(
            textwrap.dedent(
                """\
                Found Output:
                documentation_root:
                    'documentation'
                extra_requires:
                    []
                """
            ),
            value,
        )

    def test_not_found(self):
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test("config show does_not_exist documentation_root")

        value = stdout.getvalue()
        stdout.close()

        self.assertEqual('Name "does_not_exist" does not exist.', value.rstrip())

    def test_list_all(self):
        with wrapping.capture_pipes() as (stdout, _):
            run_test.test("config show --list-all")

        value = stdout.getvalue()
        stdout.close()

        self.assertEqual(
            textwrap.dedent(
                """\
                All available paths:
                api_toctree_line
                auto_help.filter_by
                auto_help.sort_order
                build_documentation_key
                documentation_root
                extra_requires
                init_options.check_default_files
                init_options.default_files
                sphinx-apidoc.allow_apidoc_templates
                sphinx-apidoc.arguments
                sphinx-apidoc.enable_apidoc
                sphinx-quickstart
                sphinx_conf_overrides
                sphinx_conf_overrides.add_module_names
                sphinx_conf_overrides.master_doc
                sphinx_extensions
                """
            ),
            value,
        )


@contextlib.contextmanager
def _example_override():
    """Create a Python context minimize any extra unittest-related code."""
    with run_test.keep_config() as config:
        config.optionvars["rez_sphinx"] = dict()
        config.optionvars["rez_sphinx"]["sphinx-apidoc"] = dict()
        config.optionvars["rez_sphinx"]["sphinx-apidoc"]["enable_apidoc"] = False

        yield
