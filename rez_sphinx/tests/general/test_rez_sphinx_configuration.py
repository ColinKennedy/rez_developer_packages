"""A variety of tests to ensure all settings in :doc:`configuring_rez_sphinx` work."""

import atexit
import functools
import os
import shutil
import tempfile
import textwrap
import unittest

from rez import developer_package
from rez_sphinx.preferences import preference, preference_help_

from ..common import run_test


class SphinxApiDocAllowApidocTemplates(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.sphinx-apidoc.allow_apidoc_templates` is queried as expected."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.allow_apidoc_templates` in a global `rezconfig`_."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx-apidoc": {
                        "allow_apidoc_templates": False,
                    },
                },
            }

            _clear_caches()
            disabled = preference.allow_apidoc_templates()

        self.assertFalse(disabled)
        _clear_caches()
        self.assertTrue(preference.allow_apidoc_templates())

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.allow_apidoc_templates` in a Rez source package."""
        package = _make_package_config(
            {
                "sphinx-apidoc": {
                    "allow_apidoc_templates": False,
                },
            }
        )

        _clear_caches()
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

            _clear_caches()
            self.assertEqual(expected, preference.get_master_api_documentation_line())

        default = "API Documentation <api/modules>"
        _clear_caches()
        self.assertEqual(default, preference.get_master_api_documentation_line())

    def test_per_package(self):
        """Set :ref:`rez_sphinx.api_toctree_line` on a Rez source package."""
        expected = "foo <api/modules>"
        package = _make_package_config(
            {
                "api_toctree_line": expected,
            }
        )

        _clear_caches()
        self.assertEqual(expected, preference.get_master_api_documentation_line(package=package))


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

            _clear_caches()
            self.assertEqual(preference_help_.filter_original, preference.get_filter_method())

        default = preference_help_.filter_generated
        _clear_caches()
        self.assertEqual(default, preference.get_filter_method())

    def test_package(self):
        """Set :ref:`rez_sphinx.auto_help.filter_by` in a Rez source package."""
        package = _make_package_config({"auto_help": {"filter_by": "prefer_generated"}})

        _clear_caches()
        self.assertEqual(preference_help_.filter_original, preference.get_filter_method(package=package))


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

            _clear_caches()
            self.assertEqual(preference_help_.sort_generated, preference.get_sort_method())

        default = preference_help_.alphabetical
        _clear_caches()
        self.assertEqual(default, preference.get_sort_method())

    def test_package(self):
        """Set :ref:`rez_sphinx.auto_help.sort_order` in a Rez source package."""
        package = _make_package_config({"auto_help": {"sort_order": "prefer_generated"}})

        _clear_caches()
        self.assertEqual(preference_help_.sort_generated, preference.get_sort_method(package=package))


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

            _clear_caches()
            result_from_string = preference.get_build_documentation_keys()

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "build_documentation_key": expected_list,
                },
            }

            _clear_caches()
            result_from_list = preference.get_build_documentation_keys()

        self.assertEqual([expected_string], result_from_string)
        self.assertEqual(expected_list, result_from_list)

    def test_package(self):
        """Set :ref:`rez_sphinx.build_documentation_key` in a Rez source package."""
        expected_string = "foo"
        expected_list = ["fizz", "buzz"]

        package_with_string = _make_package_config(
            {
                "build_documentation_key": expected_string,
            }
        )
        package_with_list = _make_package_config(
            {
                "build_documentation_key": expected_list,
            }
        )

        _clear_caches()
        result_from_string = preference.get_build_documentation_keys(package=package_with_string)
        _clear_caches()
        result_from_list = preference.get_build_documentation_keys(package=package_with_list)

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

            _clear_caches()
            self.assertEqual(expected, preference.get_documentation_root_name())

        default = "documentation"
        _clear_caches()
        self.assertEqual(default, preference.get_documentation_root_name())

    def test_package(self):
        """Set :ref:`rez_sphinx.documentation_root` in a Rez source package."""
        expected = "foo"
        package = _make_package_config({"documentation_root": expected})

        _clear_caches()
        self.assertEqual(expected, preference.get_documentation_root_name(package=package))


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

            _clear_caches()
            self.assertEqual(expected, preference.check_default_files())

        _clear_caches()
        self.assertTrue(preference.check_default_files())  # The default is True

    def test_package(self):
        """Set :ref:`rez_sphinx.init_options.default_files` in a Rez source package."""
        expected = False
        package = _make_package_config(
            {"init_options": {"check_default_files": expected}},
        )

        _clear_caches()
        self.assertFalse(preference.check_default_files(package=package))


class IntersphinxSettingsPackageLinkMap(unittest.TestCase):
    """Set :ref:`rez_sphinx.intersphinx_settings.package_link_map` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.intersphinx_settings.package_link_map` in a global `rezconfig`_."""
        expected = {"foo": "https://bar.com/en/latest"}

        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "intersphinx_settings": {"package_link_map": expected},
                }
            }

            _clear_caches()
            self.assertEqual(expected, preference.get_package_link_map())

        _clear_caches()
        self.assertEqual(dict(), preference.get_package_link_map())  # The default value

    def test_package(self):
        """Set :ref:`rez_sphinx.intersphinx_settings.package_link_map` in a Rez source package."""
        expected = {"foo": "https://bar.com/en/latest"}
        package = _make_package_config(
            {
                "intersphinx_settings": {
                    "package_link_map": expected,
                },
            }
        )

        _clear_caches()
        self.assertFalse(preference.get_package_link_map(package=package))


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

            _clear_caches()
            self.assertEqual(expected, preference.get_api_options())

        _clear_caches()
        self.assertEqual(["--separate"], preference.get_api_options())  # The default value

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.arguments` in a Rez source package."""
        expected = ["a", "-b", "--foo", "thing"]
        package = _make_package_config(
            {
                "sphinx-apidoc": {
                    "arguments": expected,
                },
            }
        )

        _clear_caches()
        self.assertEqual(expected, preference.get_api_options(package=package))


class SphinxApidocEnableApidoc(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-apidoc.enable_apidoc` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.enable_apidoc` in a global `rezconfig`_."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_sphinx": {
                    "sphinx-apidoc": {
                        "enable_apidoc": False
                    },
                },
            }
            _clear_caches()
            disabled = preference.is_api_enabled()

        self.assertFalse(disabled)
        _clear_caches()
        self.assertTrue(preference.is_api_enabled())

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.enable_apidoc` in a Rez source package."""
        expected = False
        package = _make_package_config({"sphinx-apidoc": {"enable_apidoc": expected}})

        _clear_caches()
        self.assertFalse(preference.is_api_enabled(package=package))


class SphinxQuickStart(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-quickstart` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-quickstart` in a global `rezconfig`_."""
        _clear_caches()

        package = _make_package_config({"sphinx-quickstart": []})
        default = [
            '--author',
            '',
            '--ext-intersphinx',
            '--project',
            'foo',
            '--release',
            '',
            '-v',
            '',
            '--suffix',
            '.rst',
            '--master',
            'index',
            '--dot=_',
            '--no-sep',
            '--language',
            'en',
            '--no-makefile',
            '--no-batchfile',
            '--quiet',
        ]
        # ``get_quick_start_options`` requires a Rez package so, to simulate
        # getting "global" settings, we define a package but give it an empty
        # configuration.
        #
        self.assertEqual(default, preference.get_quick_start_options(package))

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-quickstart` in a Rez source package."""
        expected = ["a", "-b", "--thing"]
        package = _make_package_config({"sphinx-quickstart": expected})

        _clear_caches()
        results = preference.get_quick_start_options(package)

        for item in expected:
            self.assertIn(item, results)


class SphinxConfigOverridesAddModuleNames(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx_conf_overrides.add_module_names` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx_conf_overrides.add_module_names` in a global `rezconfig`_."""
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

            _clear_caches()
            enabled = preference.get_sphinx_configuration_overrides()[variable]

        self.assertTrue(enabled)
        _clear_caches()
        # False is the default value for ``get_sphinx_configuration_overrides``
        self.assertFalse(preference.get_sphinx_configuration_overrides()[variable])

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx_conf_overrides.add_module_names` in a Rez source package."""
        expected = True
        variable = "add_module_names"
        package = _make_package_config({"sphinx_conf_overrides": {variable: expected}})

        _clear_caches()
        self.assertEqual(expected, preference.get_sphinx_configuration_overrides(package=package)[variable])


def _get_preference_from_path(path, package=None):
    """Find the preference value located at ``path``.

    See Also:
        :func:`.get_preference_paths` and :ref:`rez_sphinx config show --list-all`.

    Args:
        path (str):
            Some dot-separated dict key to query. e.g.
            ``"init_options.check_default_files"``
        package (rez.packages.Package, optional):
            If provided, the settings from this package are checked.

    Raises:
        ConfigurationError: If ``path`` isn't a valid setting.

    Returns:
        object: Whatever value ``path`` points to. It could be anything.

    """
    _clear_caches()

    return preference.get_preference_from_path(path, package=package)


def _clear_caches():
    # TODO : Add doc
    preference.get_base_settings.cache_clear()


def _make_package_config(configuration):
    # TODO : Add doc
    directory = tempfile.mkdtemp(suffix="_make_package_config")
    atexit.register(functools.partial(shutil.rmtree, directory))

    template = textwrap.dedent(
        """\
        name = "foo"

        version = "1.0.0"

        rez_sphinx_configuration = {configuration!r}
        """
    )

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(template.format(configuration=configuration))

    return developer_package.DeveloperPackage.from_path(directory)
