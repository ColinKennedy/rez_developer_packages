"""Make sure all version / latest logic works as expected."""

import re
import unittest

from six.moves import mock
from rez.vendor.version import version as version_

from .common import boilerplate, package_wrap


class Publish(unittest.TestCase):
    """Skip / Overwrite documentation, under certain circumstances."""

    def test_any_version_never_skip_001(self):
        """Publish documentation for every new version, no matter what.

        .. seealso::

            :doc:`publishing_per_version`

        """
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        package = _make_mock_package("1.1.0")
        patch = _make_mock_package("1.1.1")
        any_version = re.compile(".+")
        original_published = _do_version_publish(
            version_folder,
            documentation,
            package,
            any_version,
        )
        patch_published = _do_version_publish(
            version_folder,
            documentation,
            patch,
            any_version,
        )

        self.assertTrue(original_published)
        self.assertTrue(patch_published)

    def test_any_version_never_skip_002(self):
        """Publish documentation for every new version, no matter what.

        .. seealso::

            :doc:`publishing_per_version`

        """
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        package = _make_mock_package("1.1.0")
        patch = _make_mock_package("1.1.1")
        any_version = ""
        original_published = _do_version_publish(
            version_folder,
            documentation,
            package,
            any_version,
        )
        patch_published = _do_version_publish(
            version_folder,
            documentation,
            patch,
            any_version,
        )

        self.assertTrue(original_published)
        self.assertTrue(patch_published)

    def test_overwrite_version(self):
        """Overwrite the version folder if the Rez package is a new patch."""
        raise ValueError()

    def test_overwrite_latest(self):
        """Overwrite the latest folder if the Rez package is a new version."""
        raise ValueError()

    def test_regex_001(self):
        """Allow users to specify a regular expression for finding versions."""
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        package = _make_mock_package("1.1.0.0")
        patch = _make_mock_package("1.1.0.1")
        only_first_patch = re.compile(r"\d+\.\d+\.\d+")
        original_published = _do_version_publish(
            version_folder,
            documentation,
            package,
            only_first_patch,
        )
        patch_published = _do_version_publish(
            version_folder,
            documentation,
            patch,
            only_first_patch,
        )

        self.assertTrue(original_published)
        self.assertFalse(patch_published)

    def test_regex_002(self):
        """Allow users to specify a regular expression for finding versions."""
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        package = _make_mock_package("1.1.0.0")
        patch = _make_mock_package("1.1.0.1")
        up_to_second_patch = re.compile(r"\d+\.\d+\.\d+\.\d+")
        original_published = _do_version_publish(
            version_folder,
            documentation,
            package,
            up_to_second_patch,
        )
        patch_published = _do_version_publish(
            version_folder,
            documentation,
            patch,
            up_to_second_patch,
        )

        self.assertTrue(original_published)
        self.assertTrue(patch_published)

    def test_skip_version(self):
        """Don't overwrite the version folder if the Rez package is an older patch."""
        raise ValueError()

    def test_skip_latest(self):
        """Don't overwrite the latest folder if the Rez package is an older version."""
        raise ValueError()


def _do_version_publish(version_folder, documentation, package, publish_pattern):
    # TODO : Docstring
    publisher = boilerplate.get_quick_publisher(
        {
            "authentication": [
                {"token": "fake_access_token", "user": "fake_user"},
            ],
            "publisher": "github",
            "skip_existing_version": True,
            "publish_pattern": publish_pattern,
            "repository_uri": "git@github.com:FakeUser/{package.name}",
            "view_url": "https://www.some_fake.website",
        },
        package=package,
    )

    return publisher._copy_into_versioned_if_needed(
        documentation, version_folder
    )


def _make_mock_package(version):
    # TODO : Docstring
    package = mock.MagicMock()
    package.version = version_.Version(version)

    return package
