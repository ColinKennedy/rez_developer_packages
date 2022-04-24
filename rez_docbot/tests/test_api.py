"""Make sure :mod:`rez_docbot.api` works as expected."""

import unittest

from rez_docbot.core import preference

from .common import package_wrap, run_test


class GetAllPublishers(unittest.TestCase):
    """Make sure :func:`rez_docbot.api.get_all_publishers` works as expected.

    This function uses :ref:`rez_docbot.publishers` to work.

    """

    def test_global(self):
        """Read from the global configuration."""
        with run_test.keep_config() as config:
            config.optionvars = {}

        raise ValueError()

    def test_package(self):
        """Read from a specific Rez package."""
        package = package_wrap.make_package_configuration(
            {
                "publishers": [
                    {
                        "authentication": {
                            "user": "Foo",
                            "token": "bar",
                            "type": "github",
                        },
                        "branch": "gh-pages",
                        "repository_uri": "git@github.com:Foo/{package.name}",
                        "view_url": "https://Foo.github.io/{package.name}",
                    },
                ],
            }
        )

        self.assertEqual(1, len(preference.get_all_publishers(package=package)))
        self.assertEqual(0, len(preference.get_all_publishers()))


class GetFirstVersionedViewUrl(unittest.TestCase):
    """Make sure :func:`rez_docbot.api.get_firse_versioned_view_url` works."""

    def test_allow_optionals(self):
        """Skip a given publisher if its documentation is considered optional."""
        raise ValueError()

    def test_global(self):
        """Read from the global configuration."""
        raise ValueError()

    def test_package(self):
        """Read from a specific Rez package."""
        raise ValueError()
