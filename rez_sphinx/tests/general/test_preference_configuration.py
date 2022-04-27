"""A variety of tests to ensure all settings in :doc:`configuring_rez_sphinx` work.

This module is essentially a more thorough extension of :doc:`test_preference`.

"""

import unittest

from rez_sphinx.preferences import preference, preference_help_

from ..common import package_wrap, run_test


class SphinxApiDocAllowApidocTemplates(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.sphinx-apidoc.allow_apidoc_templates`."""

    def test_global(self):
        """Set the value, globally."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx-apidoc": {
                        "allow_apidoc_templates": False,
                    },
                },
            }

            run_test.clear_caches()
            disabled = preference.allow_apidoc_templates()

        self.assertFalse(disabled)
        run_test.clear_caches()
        self.assertTrue(preference.allow_apidoc_templates())

    def test_package(self):
        """Set for a Rez source package."""
        package = package_wrap.make_package_configuration(
            {
                "sphinx-apidoc": {
                    "allow_apidoc_templates": False,
                },
            }
        )

        run_test.clear_caches()
        self.assertFalse(preference.allow_apidoc_templates(package=package))


class ApiTocTreeLine(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.api_toctree_line` is queried as expected."""

    def test_global(self):
        """Set :ref:`rez_sphinx.api_toctree_line` in a global `rezconfig`_."""
        expected = "foo <api/modules>"

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "api_toctree_line": expected,
                },
            }

            run_test.clear_caches()
            self.assertEqual(expected, preference.get_master_api_documentation_line())

        default = "API Documentation <api/modules>"
        run_test.clear_caches()
        self.assertEqual(default, preference.get_master_api_documentation_line())

    def test_per_package(self):
        """Set :ref:`rez_sphinx.api_toctree_line` on a Rez source package."""
        expected = "foo <api/modules>"
        package = package_wrap.make_package_configuration(
            {
                "api_toctree_line": expected,
            }
        )

        run_test.clear_caches()
        self.assertEqual(
            expected, preference.get_master_api_documentation_line(package=package)
        )


class AutoHelpFilterBy(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.auto_help.filter_by` is queried as expected."""

    def test_global(self):
        """Set :ref:`rez_sphinx.auto_help.filter_by` in a global `rezconfig`_."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "auto_help": {
                        "filter_by": "prefer_generated",
                    },
                },
            }

            run_test.clear_caches()
            self.assertEqual(
                preference_help_.filter_original, preference.get_filter_method()
            )

        default = preference_help_.filter_generated
        run_test.clear_caches()
        self.assertEqual(default, preference.get_filter_method())

    def test_package(self):
        """Set :ref:`rez_sphinx.auto_help.filter_by` in a Rez source package."""
        package = package_wrap.make_package_configuration(
            {"auto_help": {"filter_by": "prefer_generated"}}
        )

        run_test.clear_caches()
        self.assertEqual(
            preference_help_.filter_original,
            preference.get_filter_method(package=package),
        )


class AutoHelpSortOrder(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.auto_help.sort_order` is queried as expected."""

    def test_global(self):
        """Set :ref:`rez_sphinx.auto_help.sort_order` in a global `rezconfig`_."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "auto_help": {
                        "sort_order": "prefer_generated",
                    },
                },
            }

            run_test.clear_caches()
            self.assertEqual(
                preference_help_.sort_generated, preference.get_sort_method()
            )

        default = preference_help_.alphabetical
        run_test.clear_caches()
        self.assertEqual(default, preference.get_sort_method())

    def test_package(self):
        """Set :ref:`rez_sphinx.auto_help.sort_order` in a Rez source package."""
        package = package_wrap.make_package_configuration(
            {"auto_help": {"sort_order": "prefer_generated"}}
        )

        run_test.clear_caches()
        self.assertEqual(
            preference_help_.sort_generated, preference.get_sort_method(package=package)
        )


class BuildDocumentation(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.build_documentation` is queried as expected."""

    def test_global(self):
        """Set :ref:`rez_sphinx.build_documentation_key` in a global `rezconfig`_."""
        expected_string = "foo"
        expected_list = ["fizz", "buzz"]

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "build_documentation_key": expected_string,
                },
            }

            run_test.clear_caches()
            result_from_string = preference.get_build_documentation_keys()

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "build_documentation_key": expected_list,
                },
            }

            run_test.clear_caches()
            result_from_list = preference.get_build_documentation_keys()

        self.assertEqual([expected_string], result_from_string)
        self.assertEqual(expected_list, result_from_list)

    def test_package(self):
        """Set :ref:`rez_sphinx.build_documentation_key` in a Rez source package."""
        expected_string = "foo"
        expected_list = ["fizz", "buzz"]

        package_with_string = package_wrap.make_package_configuration(
            {
                "build_documentation_key": expected_string,
            }
        )
        package_with_list = package_wrap.make_package_configuration(
            {
                "build_documentation_key": expected_list,
            }
        )

        run_test.clear_caches()
        result_from_string = preference.get_build_documentation_keys(
            package=package_with_string
        )
        run_test.clear_caches()
        result_from_list = preference.get_build_documentation_keys(
            package=package_with_list
        )

        self.assertEqual([expected_string], result_from_string)
        self.assertEqual(expected_list, result_from_list)


class DocumentationRoot(unittest.TestCase):
    """Set :ref:`rez_sphinx.documentation_root` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.documentation_root` in a global `rezconfig`_."""
        expected = "foo"

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "documentation_root": expected,
                },
            }

            run_test.clear_caches()
            self.assertEqual(expected, preference.get_documentation_root_name())

        default = "documentation"
        run_test.clear_caches()
        self.assertEqual(default, preference.get_documentation_root_name())

    def test_package(self):
        """Set :ref:`rez_sphinx.documentation_root` in a Rez source package."""
        expected = "foo"
        package = package_wrap.make_package_configuration(
            {"documentation_root": expected}
        )

        run_test.clear_caches()
        self.assertEqual(
            expected, preference.get_documentation_root_name(package=package)
        )


class InitOptionsCheckDefaultFiles(unittest.TestCase):
    """Set :ref:`rez_sphinx.init_options.default_files` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.init_options.default_files` in a global `rezconfig`_."""
        expected = False

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "init_options": {"check_default_files": expected},
                },
            }

            run_test.clear_caches()
            self.assertEqual(expected, preference.check_default_files())

        run_test.clear_caches()
        self.assertTrue(preference.check_default_files())  # The default is True

    def test_package(self):
        """Set :ref:`rez_sphinx.init_options.default_files` in a Rez source package."""
        expected = False
        package = package_wrap.make_package_configuration(
            {"init_options": {"check_default_files": expected}},
        )

        run_test.clear_caches()
        self.assertFalse(preference.check_default_files(package=package))


class IntersphinxSettingsPackageLinkMap(unittest.TestCase):
    """Set :ref:`rez_sphinx.intersphinx_settings.package_link_map`."""

    def test_global(self):
        """Set the value, globally."""
        expected = {"foo": "https://bar.com/en/latest"}

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "intersphinx_settings": {"package_link_map": expected},
                }
            }

            run_test.clear_caches()
            self.assertEqual(expected, preference.get_package_link_map())

        run_test.clear_caches()
        self.assertEqual({}, preference.get_package_link_map())  # The default value

    def test_package(self):
        """Set for a Rez source package."""
        expected = {"fizz": "https://buzz.com/en/latest"}
        package = package_wrap.make_package_configuration(
            {
                "intersphinx_settings": {
                    "package_link_map": expected,
                },
            }
        )

        run_test.clear_caches()
        self.assertEqual(expected, preference.get_package_link_map(package=package))


class SphinxApidocArguments(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-apidoc.arguments` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.arguments` in a global `rezconfig`_."""
        expected = ["a", "-b", "--foo", "thing"]

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx-apidoc": {
                        "arguments": expected,
                    },
                },
            }

            run_test.clear_caches()
            self.assertEqual(expected, preference.get_api_options())

        run_test.clear_caches()
        self.assertEqual(
            ["--separate"], preference.get_api_options()
        )  # The default value

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.arguments` in a Rez source package."""
        expected = ["a", "-b", "--foo", "thing"]
        package = package_wrap.make_package_configuration(
            {
                "sphinx-apidoc": {
                    "arguments": expected,
                },
            }
        )

        run_test.clear_caches()
        self.assertEqual(expected, preference.get_api_options(package=package))


class SphinxApidocEnableApidoc(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-apidoc.enable_apidoc` in a Rez source package."""

    def test_global(self):
        """Set the value, globally."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx-apidoc": {"enable_apidoc": False},
                },
            }
            run_test.clear_caches()
            disabled = preference.is_api_enabled()

        self.assertFalse(disabled)
        run_test.clear_caches()
        self.assertTrue(preference.is_api_enabled())

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.enable_apidoc` in a Rez source package."""
        expected = False
        package = package_wrap.make_package_configuration(
            {"sphinx-apidoc": {"enable_apidoc": expected}}
        )

        run_test.clear_caches()
        self.assertFalse(preference.is_api_enabled(package=package))


class SphinxBuild(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.sphinx-build` is queried as expected."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-build` in a global `rezconfig`_."""
        expected = ["-W"]

        with run_test.keep_config() as config:
            config.optionvars = {"rez_sphinx": {"sphinx-build": expected}}
            run_test.clear_caches()
            found = preference.get_build_options()

        self.assertEqual(expected, found)
        run_test.clear_caches()
        self.assertEqual([], preference.get_build_options())

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-build` in a package."""
        expected = ["-W"]
        package = package_wrap.make_package_configuration(
            {"sphinx-build": expected},
        )

        run_test.clear_caches()
        self.assertEqual(expected, preference.get_build_options(package=package))


class SphinxQuickStart(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-quickstart` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-quickstart` in a global `rezconfig`_."""
        run_test.clear_caches()

        package = package_wrap.make_package_configuration({"sphinx-quickstart": []})
        default = [
            "--author",
            "",
            "--ext-intersphinx",
            "--project",
            "foo",
            "--release",
            "",
            "-v",
            "",
            "--suffix",
            ".rst",
            "--master",
            "index",
            "--dot=_",
            "--no-sep",
            "--language",
            "en",
            "--no-makefile",
            "--no-batchfile",
            "--quiet",
        ]
        # ``get_quick_start_options`` requires a Rez package so, to simulate
        # getting "global" settings, we define a package but give it an empty
        # configuration.
        #
        self.assertEqual(default, preference.get_quick_start_options(package))

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-quickstart` in a Rez source package."""
        expected = ["a", "-b", "--thing"]
        package = package_wrap.make_package_configuration(
            {"sphinx-quickstart": expected}
        )

        run_test.clear_caches()
        results = preference.get_quick_start_options(package)

        for item in expected:
            self.assertIn(item, results)


class SphinxConfigOverridesAddModuleNames(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx_conf_overrides.add_module_names`."""

    def test_global(self):
        """Set the value, globally."""
        expected = True
        variable = "add_module_names"

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx_conf_overrides": {
                        variable: expected,
                    }
                }
            }

            run_test.clear_caches()
            enabled = preference.get_sphinx_configuration_overrides()[variable]

        self.assertTrue(enabled)
        run_test.clear_caches()
        # False is the default value for ``get_sphinx_configuration_overrides``
        self.assertFalse(preference.get_sphinx_configuration_overrides()[variable])

    def test_package(self):
        """Set for a Rez source package."""
        expected = True
        variable = "add_module_names"
        package = package_wrap.make_package_configuration(
            {"sphinx_conf_overrides": {variable: expected}}
        )

        run_test.clear_caches()
        self.assertEqual(
            expected,
            preference.get_sphinx_configuration_overrides(package=package)[variable],
        )
