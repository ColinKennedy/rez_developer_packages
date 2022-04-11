"""Make sure setting environment variables from the terminal works."""

import os
import unittest

from python_compatibility import wrapping

from rez_sphinx.preferences import preference, preference_help

from ..common import run_test


class Environment(unittest.TestCase):
    """Set preferences using environment variables."""

    def test_bool(self):
        """Set a bool preference."""
        run_test.clear_caches()
        self.assertTrue(preference.allow_apidoc_templates())

        run_test.clear_caches()

        with wrapping.keep_os_environment():
            os.environ["REZ_SPHINX_SPHINX_APIDOC_ALLOW_APIDOC_TEMPLATES"] = "0"
            self.assertFalse(preference.allow_apidoc_templates())

    def test_dict(self):
        """Set a dict preference."""
        run_test.clear_caches()
        self.assertEqual({}, preference.get_package_link_map())

        expected = {"foo": "bar"}
        run_test.clear_caches()

        with wrapping.keep_os_environment():
            os.environ["REZ_SPHINX_INTERSPHINX_SETTINGS"] = repr(
                {
                    "package_link_map": expected,
                }
            )
            self.assertEqual(expected, preference.get_package_link_map())

    def test_list(self):
        """Set a list preference."""
        run_test.clear_caches()
        self.assertEqual(
            ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx.ext.viewcode"],
            preference.get_sphinx_extensions(),
        )

        run_test.clear_caches()

        with wrapping.keep_os_environment():
            os.environ[
                "REZ_SPHINX_SPHINX_CONF_OVERRIDES_EXTENSIONS"
            ] = "['foo', 'bar', 'thing']"
            self.assertEqual(
                ["foo", "bar", "thing"],
                preference.get_sphinx_extensions(),
            )

    def test_str(self):
        """Set a str preference."""
        run_test.clear_caches()
        self.assertEqual(
            "API Documentation <api/modules>",
            preference.get_master_api_documentation_line(),
        )

        expected = "blah"
        run_test.clear_caches()

        with wrapping.keep_os_environment():
            os.environ["REZ_SPHINX_API_TOCTREE_LINE"] = expected
            self.assertEqual(expected, preference.get_master_api_documentation_line())

    def test_use(self):
        """Set a preference which has dynamic evaluation configured."""
        run_test.clear_caches()
        self.assertEqual(
            preference_help.DEFAULT_SORT._callable,
            preference.get_sort_method(),
        )

        expected = "prefer_original"
        run_test.clear_caches()

        with wrapping.keep_os_environment():
            os.environ["REZ_SPHINX_AUTO_HELP_SORT_ORDER"] = expected
            self.assertEqual(
                preference_help.OPTIONS[expected],
                preference.get_sort_method(),
            )
