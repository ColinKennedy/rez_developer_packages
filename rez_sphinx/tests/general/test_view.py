"""Ensure :ref:`rez_sphinx view sphinx-conf` works."""

import ast
import os
import unittest

from python_compatibility import wrapping
from rez_utilities import finder
from six.moves import mock

from rez_sphinx.core import exception

from ..common import run_test

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(_CURRENT_DIRECTORY))


class PackageHelp(unittest.TestCase):
    """Ensure :ref:`rez_sphinx view package-help` works."""

    @classmethod
    def setUpClass(cls):
        cls._package_with_no_preprocess = os.path.join(
            _PACKAGE_ROOT,
            "_test_data",
            "package_help_data",
            "source_packages",
            "package_to_test",
        )

        cls._package_with_preprocess = os.path.join(
            _PACKAGE_ROOT,
            "_test_data",
            "package_help_data",
            "source_packages",
            "preprocess_package",
        )

    def test_both_preprocess_and_release_hook(self):
        """Warn if the user has pre-process and the release hook enabled."""
        raise ValueError()

    def test_no_preprocess_or_release_hook(self):
        """Warn if there's no configured preprocess or release hook found."""
        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, run_test.keep_config() as config:
            patch.return_value = False
            config.optionvars = {"rez_docbot": {}, "rez_sphinx": {}}

            with wrapping.capture_pipes() as (_, stderr):
                run_test.test("view package-help")

        value = stderr.getvalue()
        stderr.close()

        self.assertIn(
            "No preprocess or release hook found. Results may not be fully resolved",
            value,
        )

    def test_rez_docbot_no_publish_url(self):
        """Fail if the user has docbot loaded but an invalid configuration."""
        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, wrapping.keep_cwd(), self.assertRaises(
            exception.PluginConfigurationError
        ):
            os.chdir(self._package_with_no_preprocess)
            patch.return_value = True

            run_test.test("view package-help")

    def test_rez_docbot_release_hook_normal(self):
        """Find and expand a viewing URL, using the :ref:`rez_docbot` plug-in."""
        required_folder = os.path.join(
            os.environ["REZ_REZ_SPHINX_ROOT"],
            "python",
            "rez_sphinx_plugins",
        )

        if not os.path.exists(required_folder):
            raise EnvironmentError(
                'Directory "{required_folder}" does not exist.'.format(
                    required_folder=required_folder
                )
            )

        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, run_test.keep_config() as config, wrapping.keep_cwd():
            os.chdir(self._package_with_no_preprocess)

            config.plugin_path = [required_folder]
            config.release_hooks = ["publish_documentation"]
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }
            patch.return_value = True

            with wrapping.capture_pipes() as (stdout, _):
                run_test.test("view package-help")

        value = stdout.getvalue()
        stdout.close()
        result = ast.literal_eval(value)

        expected = [
            [
                "Developer Documentation",
                "https://Foo.github.io/Bar/package_to_test/versions/2.1/developer_documentation.html",  # pylint: disable=line-too-long
            ],
            [
                "User Documentation",
                "https://Foo.github.io/Bar/package_to_test/versions/2.1/user_documentation.html",  # pylint: disable=line-too-long
            ],
            ["foo", "bar"],
            [
                "rez_sphinx objects.inv",
                "https://Foo.github.io/Bar/package_to_test/versions/2.1",
            ],
        ]

        self.assertEqual(expected, result)

    def test_overwritten_preprocess(self):
        """Warn if the Rez source package overwrote the global preprocess."""
        required_folder = os.path.join(
            os.environ["REZ_REZ_SPHINX_ROOT"],
            "python",
            "rez_sphinx",
            "preprocess",
        )

        if not os.path.exists(required_folder):
            raise EnvironmentError(
                'Directory "{required_folder}" does not exist.'.format(
                    required_folder=required_folder
                )
            )

        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, run_test.keep_config() as config, wrapping.keep_cwd():
            os.chdir(self._package_with_preprocess)

            config.package_definition_build_python_paths = [required_folder]
            config.package_preprocess_mode = "override"
            config.package_preprocess_function = "preprocess_entry_point.run"
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }
            patch.return_value = True

            with self.assertRaises(exception.ConfigurationError):
                run_test.test("view package-help")

    def test_overwritten_preprocess_not_001(self):
        """Don't warn because the Rez source package does not overwrite anything.

        It doesn't override because `package_preprocess_mode`_ is not set to
        ``"override"``.

        """
        required_folder = os.path.join(
            os.environ["REZ_REZ_SPHINX_ROOT"],
            "python",
            "rez_sphinx",
            "preprocess",
        )

        if not os.path.exists(required_folder):
            raise EnvironmentError(
                'Directory "{required_folder}" does not exist.'.format(
                    required_folder=required_folder
                )
            )

        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, run_test.keep_config() as config, wrapping.keep_cwd():
            os.chdir(self._package_with_preprocess)

            config.package_definition_build_python_paths = [required_folder]
            config.package_preprocess_mode = "before"
            config.package_preprocess_function = "preprocess_entry_point.run"
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }
            patch.return_value = True

            with wrapping.capture_pipes() as (_, _):
                run_test.test("view package-help")

    def test_overwritten_preprocess_not_002(self):
        """Don't warn because the Rez source package does not overwrite anything.

        It doesn't override because `package_preprocess_mode`_ is set
        ``"override"`` but the package doesn't define a `preprocess`_ function.

        """
        required_folder = os.path.join(
            os.environ["REZ_REZ_SPHINX_ROOT"],
            "python",
            "rez_sphinx",
            "preprocess",
        )

        if not os.path.exists(required_folder):
            raise EnvironmentError(
                'Directory "{required_folder}" does not exist.'.format(
                    required_folder=required_folder
                )
            )

        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, run_test.keep_config() as config, wrapping.keep_cwd():
            os.chdir(self._package_with_no_preprocess)

            config.package_definition_build_python_paths = [required_folder]
            config.package_preprocess_mode = "override"
            config.package_preprocess_function = "preprocess_entry_point.run"
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }
            patch.return_value = True

            with wrapping.capture_pipes() as (_, _):
                run_test.test("view package-help")

    def test_unloadable_preprocess(self):
        """Warn if the user defines preprocess but it cannot be imported."""
        required_folder = os.path.join(
            os.environ["REZ_REZ_SPHINX_ROOT"],
            "python",
            "rez_sphinx",
            "preprocess",
        )

        if not os.path.exists(required_folder):
            raise EnvironmentError(
                'Directory "{required_folder}" does not exist.'.format(
                    required_folder=required_folder
                )
            )

        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, run_test.keep_config() as config, wrapping.keep_cwd():
            os.chdir(self._package_with_preprocess)

            config.package_preprocess_mode = "override"
            config.package_preprocess_function = "preprocess_entry_point.run"
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }
            patch.return_value = True

            with self.assertRaises(exception.ConfigurationError):
                run_test.test("view package-help")

    def test_unloadable_release_hook(self):
        """Warn if the user defines a release hook but Rez cannot load it.

        This test is more of a Rez implementation detail. But we should at
        least try to give the user a nice error message.

        Raises:
            EnvironmentError: If the folder needed for this test doesn't exist.

        """
        raise ValueError("FINISH THIS")

        required_folder = os.path.join(os.environ["REZ_REZ_SPHINX_ROOT"], "python")

        if not os.path.exists(required_folder):
            raise EnvironmentError(
                'Directory "{required_folder}" does not exist.'.format(
                    required_folder=required_folder
                )
            )

        with mock.patch(
            "rez_sphinx.core.environment.is_publishing_enabled"
        ) as patch, run_test.keep_config() as config, wrapping.keep_cwd():
            os.chdir(self._package_with_no_preprocess)

            config.release_hooks = ["publish_documentation"]
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }
            patch.return_value = True

            with self.assertRaises(exception.ConfigurationError):
                run_test.test("view package-help")


class PublishUrl(unittest.TestCase):
    """Ensure :ref:`rez_sphinx view view-url` works."""

    def test_repository_uri(self):
        """Get all URLs / URIs where documentation will be pushed / published to."""
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }

            with wrapping.capture_pipes() as (stdout, _):
                run_test.test("view repository-uri")

            value = stdout.getvalue()
            stdout.close()

            self.assertEqual(
                'URI: "git@something.com:Foo/Bar" / Required: "True"',
                value.rstrip(),
            )

    def test_view_url(self):
        """Get the URL where documentation will be visible from.

        The first required URL is returned.

        """
        with run_test.keep_config() as config:
            config.optionvars = {
                "rez_docbot": {
                    "publishers": [
                        {
                            "authentication": {
                                "user": "foo",
                                "token": "bar",
                            },
                            "publisher": "github",
                            "repository_uri": "git@something.com:Foo/Bar",
                            "view_url": "https://Foo.github.io/Bar/{package.name}",
                        },
                    ],
                },
            }

            with wrapping.capture_pipes() as (stdout, _):
                run_test.test("view view-url")

            value = stdout.getvalue()
            stdout.close()

            self.assertEqual(
                "https://Foo.github.io/Bar/rez_sphinx/versions/1.0",
                value.rstrip(),
            )

    def test_no_repository_uri(self):
        """Try to get a publish URL but fail because none is defined."""
        with self.assertRaises(exception.ConfigurationError):
            run_test.test("view repository-uri")

    def test_no_view_url(self):
        """Try to get a publish URL but fail because none is defined."""
        with self.assertRaises(exception.ConfigurationError):
            run_test.test("view view-url")


class SphinxConf(unittest.TestCase):
    """Ensure :ref:`rez_sphinx view sphinx-conf` works."""

    def test_overrides(self):
        """Test :ref:`sphinx_conf_overrides` and :ref:`rez_sphinx view sphinx-conf`."""
        package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)

        with wrapping.keep_cwd(), run_test.keep_config() as config:
            os.chdir(finder.get_package_root(package))

            config.optionvars["rez_sphinx"] = {
                "sphinx_conf_overrides": {
                    "rst_prolog": "thing",
                },
            }

            with wrapping.capture_pipes() as (stdout, _):
                run_test.test("view sphinx-conf rst_prolog")

            value = stdout.getvalue()
            stdout.close()

            self.assertEqual("thing", value.rstrip())

    def test_overrides_not_found(self):
        """Test :ref:`sphinx_conf_overrides` and :ref:`rez_sphinx view sphinx-conf`."""
        package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)

        with wrapping.keep_cwd():
            os.chdir(finder.get_package_root(package))

            with self.assertRaises(exception.SphinxConfError):
                run_test.test("view sphinx-conf does_not_exist")
