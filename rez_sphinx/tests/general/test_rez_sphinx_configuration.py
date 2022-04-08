"""A variety of tests to ensure all settings in :doc:`configuring_rez_sphinx` work."""

import atexit
import functools
import os
import shutil
import tempfile
import textwrap
import unittest

from rez import developer_package
from rez_sphinx.preferences import preference

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
        raise ValueError()

    def test_per_package(self):
        """Set :ref:`rez_sphinx.api_toctree_line` on a Rez source package."""
        optionvars = {
            "rez_sphinx": {
                "api_toctree_line": "API Documentation <api/modules>",
            },
        }
        raise ValueError()


class AutoHelp(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.auto_help` is queried as expected."""

    def test_filter_by_global(self):
        """Set :ref:`rez_sphinx.auto_help.filter_by` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "auto_help": {
                    "filter_by": "prefer_generated",
                },
            },
        }
        raise ValueError()

    def test_filter_by_package(self):
        """Set :ref:`rez_sphinx.auto_help.filter_by` in a Rez source package."""
        optionvars = {
            "rez_sphinx": {
                "auto_help": {
                    "filter_by": "prefer_generated",
                },
            },
        }
        raise ValueError()

    def test_sort_order_global(self):
        """Set :ref:`rez_sphinx.auto_help.sort_order` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "auto_help": {
                    "sort_order": "alphabetical",
                },
            },
        }
        raise ValueError()

    def test_sort_order_package(self):
        """Set :ref:`rez_sphinx.auto_help.sort_order` in a Rez source package."""
        optionvars = {
            "rez_sphinx": {
                "auto_help": {
                    "sort_order": "alphabetical",
                },
            },
        }
        raise ValueError()


class BuildDocumentation(unittest.TestCase):
    """Make sure :ref:`rez_sphinx.build_documentation` is queried as expected."""

    def test_global(self):
        """Set :ref:`rez_sphinx.build_documentation_key` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "build_documentation": "build_documentation",
            },
        }

        optionvars = {
            "rez_sphinx": {
                "build_documentation": ["build_documentation", "fallback_test_name"],
            },
        }

        raise ValueError()

    def test_package(self):
        """Set :ref:`rez_sphinx.build_documentation_key` in a Rez source package."""
        raise ValueError()


class DocumentationRoot(unittest.TestCase):
    """Set :ref:`rez_sphinx.documentation_root` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.documentation_root` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "documentation_root": "documentation",
            },
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.documentation_root` in a Rez source package."""
        raise ValueError()


class ExtraRequires(unittest.TestCase):
    """Set :ref:`rez_sphinx.extra_requires` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.extra_requires` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "extra_requires": [],  # <-- Your extra packages here
            },
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.extra_requires` in a Rez source package."""
        raise ValueError()


class InitOptionsCheckDefaultFiles(unittest.TestCase):
    """Set :ref:`rez_sphinx.init_options.default_files` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.init_options.default_files` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "init_options.check_default_files": True,
            },
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.init_options.default_files` in a Rez source package."""
        raise ValueError()


class IntersphinxSettingsPackageLinkMap(unittest.TestCase):
    """Set :ref:`rez_sphinx.intersphinx_settings.package_link_map` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.intersphinx_settings.package_link_map` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "intersphinx_settings": {
                    "package_link_map": {
                        "schema": "https://schema.readthedocs.io/en/latest",
                    }
                }
            }
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.intersphinx_settings.package_link_map` in a Rez source package."""
        raise ValueError()


class SphinxApidocAllowApidocTemplates(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-apidoc.allow_apidoc_templates` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.allow_apidoc_templates` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "sphinx-apidoc": {
                    "allow_apidoc_templates": False,
                },
            }
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.allow_apidoc_templates` in a Rez source package."""
        raise ValueError()


class SphinxApidocArguments(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-apidoc.arguments` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.arguments` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "sphinx-apidoc": {
                    "arguments": [],
                },
            },
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-apidoc.arguments` in a Rez source package."""
        raise ValueError()


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
        package = _make_package_config(
            {
                "sphinx-apidoc": {
                    "enable_apidoc": False
                },
            }
        )

        _clear_caches()
        self.assertFalse(preference.is_api_enabled(package=package))


class SphinxQuickStart(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx-quickstart` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx-quickstart` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "sphinx-quickstart": ["--ext-coverage"],
            },
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx-quickstart` in a Rez source package."""
        raise ValueError()


class SphinxConfigOverridesAddModuleNames(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx_conf_overrides.add_module_names` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx_conf_overrides.add_module_names` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "sphinx_conf_overrides": {
                    "add_module_names": False,  # Set this to True to get old behavior back
                }
            }
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx_conf_overrides.add_module_names` in a Rez source package."""
        raise ValueError()


class SphinxConfigOverridesMasterDoc(unittest.TestCase):
    """Set :ref:`rez_sphinx.sphinx_conf_overrides.master_doc` in a Rez source package."""

    def test_global(self):
        """Set :ref:`rez_sphinx.sphinx_conf_overrides.master_doc` in a global `rezconfig`_."""
        optionvars = {
            "rez_sphinx": {
                "sphinx_conf_overrides": {
                    "master_doc": "index",
                }
            }
        }

    def test_package(self):
        """Set :ref:`rez_sphinx.sphinx_conf_overrides.master_doc` in a Rez source package."""
        raise ValueError()


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
    preference.get_base_settings.cache_clear()


def _make_package_config(configuration):
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
