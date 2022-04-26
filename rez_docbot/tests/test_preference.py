"""Make sure :mod:`rez_docbot.core.preference` works as expected."""

import unittest

from rez.vendor.version import version as version_
from rez_docbot.core import preference
from six.moves import mock

from .common import run_test


class GetAllPublishers(unittest.TestCase):
    """Ensure :func:`rez_docbot.core.preference.get_all_publishers` works."""

    def test_normal(self):
        """Ensure global settings work."""
        configuration = {
            "authentication": [{"token": "fake_access_token", "user": "fake_user"}],
            "publisher": "github",
            "repository_uri": "git@github.com:FakeUser/{package.name}",
            "view_url": "https://www.some_fake.website",
        }

        package = mock.MagicMock()
        del package.rez_docbot_configuration

        with run_test.keep_config() as config:
            config.optionvars["rez_docbot"] = {"publishers": [configuration]}
            publishers = preference.get_all_publishers(package)

        self.assertEqual(1, len(publishers))

    def test_package(self):
        """Ensure per-function settings work."""
        repository_example = "git@github.com:FakeUser/{package.name}"
        configuration = {
            "authentication": [{"token": "fake_access_token", "user": "fake_user"}],
            "publisher": "github",
            "repository_uri": repository_example,
            "view_url": "https://www.some_fake.website",
        }

        package = mock.MagicMock()
        package.name = "foobar"
        package.rez_docbot_configuration = {"publishers": [configuration]}

        with run_test.keep_config() as config:
            config.optionvars["rez_docbot"] = {"publishers": []}
            publishers = preference.get_all_publishers(package)

        self.assertEqual(1, len(publishers))
        self.assertEqual(
            repository_example.format(package=package),
            publishers[0].get_resolved_repository_uri(),
        )


class GetFirstVersionedViewUrl(unittest.TestCase):
    """Ensure :func:`rez_docbot.core.preference.get_first_versioned_view_url` works."""

    def test_normal(self):
        """Ensure global settings work."""
        view_url = "https://www.some_fake.website"
        configuration = {
            "authentication": [{"token": "fake_access_token", "user": "fake_user"}],
            "publisher": "github",
            "repository_uri": "git@github.com:FakeUser/{package.name}",
            "view_url": view_url,
        }

        package = mock.MagicMock()
        package.name = "foobar"
        version = version_.Version("1.2.3")
        package.version = version
        del package.rez_docbot_configuration

        with run_test.keep_config() as config:
            config.optionvars["rez_docbot"] = {"publishers": [configuration]}
            publishers = preference.get_all_publishers(package)

        self.assertEqual(1, len(publishers))
        self.assertEqual(
            view_url.format(package=package) + "/versions/{version.major}.{version.minor}".format(version=version),
            publishers[0].get_resolved_view_url(),
        )

    def test_package(self):
        """Ensure per-function settings work."""
        view_url = "https://www.some_fake.website"
        configuration = {
            "authentication": [{"token": "fake_access_token", "user": "fake_user"}],
            "publisher": "github",
            "repository_uri": "git@github.com:FakeUser/{package.name}",
            "view_url": view_url,
        }

        package = mock.MagicMock()
        package.name = "foobar"
        version = version_.Version("1.2.3")
        package.version = version
        package.rez_docbot_configuration = {"publishers": [configuration]}

        with run_test.keep_config() as config:
            config.optionvars["rez_docbot"] = {"publishers": []}
            publishers = preference.get_all_publishers(package)

        self.assertEqual(1, len(publishers))
        self.assertEqual(
            view_url.format(package=package) + "/versions/{version.major}.{version.minor}".format(version=version),
            publishers[0].get_resolved_view_url(),
        )
