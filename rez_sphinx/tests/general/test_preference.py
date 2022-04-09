"""Make sure miscellaneous functions from :mod:`.preference` work.

These functions are important for internal uses of :ref:`rez_sphinx` but aren't
linked to specific configuration values. To see the configuration tests, check
out :doc:`test_preference_configuration`.

"""

import unittest

from rez_sphinx.preferences import preference

from ..common import package_wrap, run_test


class GetMasterDocumentName(unittest.TestCase):
    """Ensure :func:`rez_sphinx.preferences.preference.get_master_document_name` works."""

    def test_global(self):
        """Set for a "global" configuration setting."""
        expected = "foo_bar"

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx_conf_overrides": {
                        "master_doc": expected,
                    },
                },
            }

            run_test.clear_caches()
            self.assertEqual(expected, preference.get_master_document_name())

        run_test.clear_caches()
        default = "index"
        self.assertEqual(default, preference.get_master_document_name())

    def test_package(self):
        """Set for a Rez source package."""
        expected = "foo_bar"
        package = package_wrap.make_package_config(
            {
                "sphinx_conf_overrides": {
                    "master_doc": expected,
                },
            }
        )

        run_test.clear_caches()
        self.assertEqual(expected, preference.get_master_document_name(package=package))


class GetPreferenceFromPath(unittest.TestCase):
    """Ensure :func:`rez_sphinx.preferences.preference.get_preference_from_path` works."""

    def test_global(self):
        """Set for a "global" configuration setting."""
        expected = "foo_bar"
        path = "sphinx_conf_overrides.master_doc"

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx_conf_overrides": {
                        "master_doc": expected,
                    },
                },
            }

            run_test.clear_caches()
            self.assertEqual(expected, preference.get_preference_from_path(path))

        run_test.clear_caches()
        default = "index"
        self.assertEqual(default, preference.get_preference_from_path(path))

    def test_package(self):
        """Set for a Rez source package."""
        expected = "foo_bar"
        package = package_wrap.make_package_config(
            {
                "sphinx_conf_overrides": {
                    "master_doc": expected,
                },
            }
        )

        run_test.clear_caches()
        self.assertEqual(
            expected,
            preference.get_preference_from_path(
                "sphinx_conf_overrides.master_doc",
                package=package,
            ),
        )


class GetPreferencePaths(unittest.TestCase):
    """Ensure :func:`rez_sphinx.preferences.preference.get_preference_paths` works."""

    def test_global(self):
        """Set for a "global" configuration setting."""
        variable = "thing"
        expected = "blah"

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx_conf_overrides": {
                        variable: expected,
                    },
                },
            }

            run_test.clear_caches()
            self.assertIn(
                "sphinx_conf_overrides.thing", preference.get_preference_paths()
            )

        run_test.clear_caches()
        default = {
            "api_toctree_line",
            "auto_help.filter_by",
            "auto_help.sort_order",
            "build_documentation_key",
            "documentation_root",
            "extra_requires",
            "init_options.check_default_files",
            "init_options.default_files",
            "sphinx-apidoc.allow_apidoc_templates",
            "sphinx-apidoc.arguments",
            "sphinx-apidoc.enable_apidoc",
            "sphinx-quickstart",
            "sphinx_conf_overrides.add_module_names",
            "sphinx_conf_overrides.master_doc",
            "sphinx_conf_overrides.thing",
            "sphinx_extensions",
        }
        self.assertEqual(default, preference.get_preference_paths())

    def test_package(self):
        """Set for a Rez source package."""
        expected = "foo_bar"
        package = package_wrap.make_package_config(
            {
                "sphinx_conf_overrides": {
                    "thing": expected,
                },
            }
        )

        run_test.clear_caches()
        self.assertIn(
            "sphinx_conf_overrides.thing",
            preference.get_preference_paths(package=package),
        )


class PreferenceValidation(unittest.TestCase):
    """Ensure invalid settings are caught properly."""

    def test_global(self):
        """Set for a "global" configuration setting."""
        raise ValueError()

    def test_package(self):
        """Set for a Rez source package."""
        raise ValueError()
