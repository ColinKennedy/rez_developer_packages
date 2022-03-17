"""Make sure :ref:`rez_sphinx config` works."""

import unittest

from rez_sphinx.core import exception
from python_compatibility import wrapping
from six.moves import mock

from .common import run_test


class Check(unittest.TestCase):
    """Make sure :ref:`rez_sphinx config check` works."""

    def test_invalid(self):
        """Report that the user's applied overrides are invalid."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = 'not valid'

            with self.assertRaises(exception.ConfigurationError), wrapping.silence_printing():
                run_test.test('config check')

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["enable_apidoc"] = None

            with self.assertRaises(exception.ConfigurationError), wrapping.silence_printing():
                run_test.test('config check')

    def test_valid(self):
        """Report success if the applied overrides are okay."""
        with wrapping.silence_printing():
            run_test.test('config check')

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["enable_apidoc"] = False

            with wrapping.silence_printing():
                run_test.test('config check')


class List(unittest.TestCase):
    """Make sure :ref:`rez_sphinx config list` works."""

    def test_applied(self):
        """Print the applied user settings."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["enable_apidoc"] = False

            run_test.test('config list')

    def test_default(self):
        """Print default :ref:`rez_sphinx` settings."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["enable_apidoc"] = False

            with wrapping.capture_pipes() as (stdout, _):
                run_test.test('config list-default')

        text = stdout.getvalue()
        print('TEXt', text)
        stdout.close()

        raise ValueError()

    def test_default_sparse(self):
        """Print default :ref:`rez_sphinx` settings."""
        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["enable_apidoc"] = False

            with wrapping.capture_pipes(), mock.patch("pprint.pprint") as patch:
                run_test.test('config list-default --sparse')

        args, kwargs = patch.call_args
        actual = args[0]
        expected = {
            'enable_apidoc': False,
            'documentation_root': '',
            'init_options': {},
            'sphinx_conf_overrides': {},
            'sphinx_extensions': [],
            'sphinx-apidoc': [],
            'extra_requires': [],
            'sphinx-quickstart': [],
            'build_documentation_key': '',
            'auto_help': {},
            'api_toctree_line': '',
        }

        self.assertEqual(expected, actual)

    def test_invalid(self):
        """Report that the user's applied overrides are invalid."""
        raise ValueError()
