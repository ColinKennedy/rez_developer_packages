"""Ensure :ref:`rez_sphinx view sphinx-conf` works."""

import os
import unittest

from python_compatibility import wrapping
from rez_utilities import finder

from rez_sphinx.core import exception

from ..common import run_test

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class PublishUrl(unittest.TestCase):
    """Ensure :ref:`rez_sphinx view publish-url` works."""

    def test_get_url(self):
        """Get the URL where documentation will go to.

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
                                "type": "github",
                            },
                            "repository_uri": "git@something.com:Blah/Thing",
                            "view_url": "https://ColinKennedy.github.io/{package.name}",
                        },
                    ],
                },
            }

            with wrapping.capture_pipes() as (stdout, _):
                run_test.test("view publish-url")

            value = stdout.getvalue()
            stdout.close()

            self.assertEqual(
                "https://ColinKennedy.github.io/rez_sphinx/versions/1.0",
                value.rstrip(),
            )

    def test_no_get_url(self):
        """Try to get a publish URL but fail because none is defined."""
        with self.assertRaises(exception.ConfigurationError):
            run_test.test("view publish-url")


class SphinxConf(unittest.TestCase):
    """Ensure :ref:`rez_sphinx view sphinx-conf` works."""

    def test_overrides(self):
        """Test :ref:`sphinx_conf_overrides` and :ref:`rez_sphinx view sphinx-conf`."""
        package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)

        with wrapping.keep_cwd(), run_test.keep_config() as config:
            os.chdir(finder.get_package_root(package))

            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["sphinx_conf_overrides"] = {
                "rst_prolog": "thing"
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
