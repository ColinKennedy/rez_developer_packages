"""Make sure all version / latest logic works as expected."""

import io
import os
import re
import unittest

from rez.vendor.version import version as version_
from six.moves import mock

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
            documentation,
            version_folder,
            package,
            any_version,
        )
        patch_published = _do_version_publish(
            documentation,
            version_folder,
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
            documentation,
            version_folder,
            package,
            any_version,
        )
        patch_published = _do_version_publish(
            documentation,
            version_folder,
            patch,
            any_version,
        )

        self.assertTrue(original_published)
        self.assertTrue(patch_published)

    def test_overwrite_version(self):
        """Overwrite the version folder if the Rez package is a new patch."""
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        package = _make_mock_package("1.1.0")
        patch = _make_mock_package("1.1.1")
        major_minor = "{package.version.major}.{package.version.minor}"
        original_published = _do_version_publish(
            documentation,
            version_folder,
            package,
            major_minor,
            skip_existing_version=False,
        )

        inner_file = os.path.join(version_folder, "1.1", "foo.html")
        before_update = os.path.isfile(inner_file)

        with io.open(os.path.join(documentation, "foo.html"), "a", encoding="utf-8"):
            pass

        patch_published = _do_version_publish(
            documentation,
            version_folder,
            patch,
            major_minor,
            skip_existing_version=False,
        )
        after_update = os.path.isfile(inner_file)

        self.assertTrue(original_published)
        self.assertTrue(patch_published)
        self.assertFalse(before_update)
        self.assertTrue(after_update)

    def test_overwrite_latest(self):
        """Overwrite the latest folder if the Rez package is a new version."""
        latest_folder = package_wrap.make_temporary_directory("_latest_folder")
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        package = _make_mock_package("1.1.0")
        patch = _make_mock_package("1.1.1")
        major_minor = "{package.version.major}.{package.version.minor}"
        original_published = _do_latest_publish(
            documentation,
            latest_folder,
            version_folder,
            package,
            major_minor,
            skip_existing_version=False,
        )

        inner_file = os.path.join(latest_folder, "foo.html")
        before_update = os.path.isfile(inner_file)

        with io.open(os.path.join(documentation, "foo.html"), "a", encoding="utf-8"):
            pass

        patch_published = _do_latest_publish(
            documentation,
            latest_folder,
            version_folder,
            patch,
            major_minor,
            skip_existing_version=False,
        )
        after_update = os.path.isfile(inner_file)

        self.assertTrue(original_published)
        self.assertTrue(patch_published)
        self.assertFalse(before_update)
        self.assertTrue(after_update)

    def test_regex_001(self):
        """Allow users to specify a regular expression for finding versions."""
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        package = _make_mock_package("1.1.0.0")
        patch = _make_mock_package("1.1.0.1")
        only_first_patch = re.compile(r"\d+\.\d+\.\d+")
        original_published = _do_version_publish(
            documentation,
            version_folder,
            package,
            only_first_patch,
        )
        patch_published = _do_version_publish(
            documentation,
            version_folder,
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
            documentation,
            version_folder,
            package,
            up_to_second_patch,
        )
        patch_published = _do_version_publish(
            documentation,
            version_folder,
            patch,
            up_to_second_patch,
        )

        self.assertTrue(original_published)
        self.assertTrue(patch_published)

    def test_skip_latest(self):
        """Don't overwrite the latest folder if the Rez package is an older version."""
        latest_folder = package_wrap.make_temporary_directory("_latest_folder")
        version_folder = package_wrap.make_temporary_directory("_version_folder")
        documentation = package_wrap.make_temporary_directory("_documentation")

        newer = _make_mock_package("1.2.0")
        back_patch = _make_mock_package("1.1.1")
        any_version = ""
        original_published = _do_latest_publish(
            documentation,
            latest_folder,
            version_folder,
            newer,
            any_version,
        )

        # Fake adding a versioned documentation folder
        os.makedirs(os.path.join(version_folder, "1.2.0"))

        patch_published = _do_latest_publish(
            documentation,
            latest_folder,
            version_folder,
            back_patch,
            any_version,
        )

        self.assertTrue(original_published)
        self.assertFalse(patch_published)


def _make_custom_pattern(
    publish_pattern,
    package,
    skip_existing_version=True,
):
    """Create a quick publisher, for unittesting.

    Args:
        publish_pattern (str or _sre.Pattern):
            A description of the version documentation folder to create.
        package (mock.MagicMock):
            A fake Rez package to query, for testing. It has an assigned
            version value but not much else.
        skip_existing_version (bool, optional):
            If True and ``package``'s version did not generate a unique version
            folder name, the documentation is not copied. If False, even if
            ``package`` has a duplicate version, the documentation is copied
            anyway.

    Returns:
        :class:`rez_docbot.bases.base.Publisher`: The generated instance.

    """
    return boilerplate.get_quick_publisher(
        {
            "authentication": [
                {"token": "fake_access_token", "user": "fake_user"},
            ],
            "publisher": "github",
            "skip_existing_version": skip_existing_version,
            "publish_pattern": publish_pattern,
            "repository_uri": "git@github.com:FakeUser/{package.name}",
            "view_url": "https://www.some_fake.website",
        },
        package=package,
    )


def _do_latest_publish(  # pylint: disable=too-many-arguments
    documentation,
    latest_folder,
    version_folder,
    package,
    publish_pattern,
    skip_existing_version=True,
):
    """Create a "latest" documentation folder.

    Args:
        documentation (str):
            The absolute directory to built documentation on-disk.
        latest_folder (str):
            The absolute directory where the latest documentation lives.
        version_folder (str):
            The absolute directory where all versioned documentation lives.
        package (mock.MagicMock):
            A fake Rez package to query, for testing. It has an assigned
            version value but not much else.
        publish_pattern (str or _sre.Pattern):
            A description of the version documentation folder to create.
        skip_existing_version (bool, optional):
            If True and ``package``'s version did not generate a unique version
            folder name, the documentation is not copied. If False, even if
            ``package`` has a duplicate version, the documentation is copied
            anyway.

    Returns:
        bool: If ``documentation`` was copied into the :ref:`latest folder`.

    """
    publisher = _make_custom_pattern(
        publish_pattern, package, skip_existing_version=skip_existing_version
    )

    return publisher._copy_into_latest_if_needed(  # pylint: disable=protected-access
        documentation, latest_folder, version_folder
    )


def _do_version_publish(
    documentation, version_folder, package, publish_pattern, skip_existing_version=True
):
    """Create a versioned documentation folder.

    Args:
        documentation (str):
            The absolute directory to built documentation on-disk.
        version_folder (str):
            The absolute directory where all versioned documentation lives.
        package (mock.MagicMock):
            A fake Rez package to query, for testing. It has an assigned
            version value but not much else.
        publish_pattern (str or _sre.Pattern):
            A description of the version documentation folder to create.
        skip_existing_version (bool, optional):
            If True and ``package``'s version did not generate a unique version
            folder name, the documentation is not copied. If False, even if
            ``package`` has a duplicate version, the documentation is copied
            anyway.

    Returns:
        bool: If ``documentation`` was copied into the :ref:`version folder`.

    """
    publisher = _make_custom_pattern(
        publish_pattern, package, skip_existing_version=skip_existing_version
    )

    return publisher._copy_into_versioned_if_needed(  # pylint: disable=protected-access
        documentation,
        version_folder,
    )


def _make_mock_package(version):
    """Make a Rez "package", for unittesting.

    Args:
        version (str): Some version, SemVer or not, to track. e.g. ``"1.2.3"``.

    Returns:
        mock.MagicMock: The created "package".

    """
    package = mock.MagicMock()
    package.version = version_.Version(version)

    return package
