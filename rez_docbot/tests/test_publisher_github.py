"""Make sure `GitHub`_-related unittests and integration tests work."""

import atexit
import functools
import io
import os
import tempfile
import textwrap
import unittest

import schema
from git.repo import base
from rez.vendor.version import version
from rez_utilities import finder
from six.moves import mock

from rez_docbot.core import common
from rez_docbot.publishers import generic

from .common import boilerplate, package_wrap, run_test


class Authentication(unittest.TestCase):
    """Make sure :class:`rez_docbot.publishers.github.Github` connects as expected."""

    def test_bad_permissions(self):
        """Fail gracefully if we cannot clone / push to a remote repository."""
        raise ValueError()

    def test_from_file(self):
        """Read authentication details from a file."""
        path = _make_temporary_file(
            "_test_from_file.json",
            textwrap.dedent(
                """\
                {
                    "token": "fake_access_token",
                    "user": "fake_user"
                }
                """
            ),
        )

        publisher = boilerplate.get_quick_publisher(
            {
                "authentication": [{"payload": path, "type": "from_json_path"}],
                "publisher": "github",
                "repository_uri": "git@github.com:FakeUser/{package.name}",
                "view_url": "https://www.some_fake.website",
            }
        )

        publisher.authenticate()

    def test_from_file_fail(self):
        """Fail to read authentication details from a non-existent file."""
        _, path = tempfile.mkstemp(suffix="_does_not_exist.json")
        os.remove(path)

        with self.assertRaises(schema.SchemaError):
            boilerplate.get_quick_publisher(
                {
                    "authentication": [
                        {"payload": "/does/not/exist.json", "type": "from_json_path"}
                    ],
                    "publisher": "github",
                    "repository_uri": "git@github.com:FakeUser/{package.name}",
                    "view_url": "https://www.some_fake.website",
                }
            )

    def test_normal(self):
        """Make sure :class:`rez_docbot.publishers.github.Github` authenticates."""
        publisher = boilerplate.get_quick_publisher(
            {
                "authentication": [
                    {"token": "fake_access_token", "user": "fake_user"},
                ],
                "publisher": "github",
                "repository_uri": "git@github.com:FakeUser/{package.name}",
                "view_url": "https://www.some_fake.website",
            }
        )

        publisher.authenticate()


class Remote(unittest.TestCase):
    """Make sure different remote configurations work as expected."""

    def test_mono_repository(self):
        """Allow users to publish to a branch within its own repository.

        If your repository only contains a single Rez package, as opposed to
        multiple Rez packages within subfolders, this configuration will allow
        users to publish to a dedicated documentation branch (like GitHub
        `gh-pages`_).

        """
        package, push_url = _make_package_with_remote()

        publisher = boilerplate.get_quick_publisher(
            {
                "authentication": [
                    {
                        "token": "fake_access_token",
                        "user": "fake_user",
                    },
                ],
                "publisher": "github",
                "repository_uri": None,
                "view_url": "https://www.FakeUser.github.io/{package.name}",
            },
            package=package,
        )

        details = publisher._get_repository_details()

        expected = common.RepositoryDetails(
            group="Thing",
            repository="blah",
            clone_url="git@foo.com:Thing/blah.git",
        )

        self.assertEqual(expected, details)

    def test_relative_path(self):
        """Allow users to specify a relative path ."""
        clone_path = package_wrap.make_temporary_directory("_clone_path")

        class _FakeHandler(object):
            def get_repository(self, *_, **__):
                mocker = mock.MagicMock()
                mocker.get_root.return_value = clone_path

                return mocker

        def _authenticate(self):
            self._handler = _FakeHandler()

        fake_remote = _make_headless_repository("_headless_git_repository.git")
        expected_documentation = package_wrap.make_temporary_directory(
            "_fake_documentation"
        )
        clone_path = package_wrap.make_temporary_directory("_clone_path")
        package = mock.MagicMock()
        package.version = version.Version("1.2.3")
        package.name = "my_package"

        relative_path = "inner/folder/{package.name}"

        publisher = boilerplate.get_quick_publisher(
            {
                "authentication": [
                    {"token": "fake_access_token", "user": "fake_user"},
                ],
                "publisher": "github",
                "relative_path": relative_path,
                "repository_uri": fake_remote,
                "view_url": "https://www.FakeUser.github.io/blah",
            },
            package=package,
        )

        with mock.patch.object(
            generic.GitPublisher,
            "authenticate",
            new=_authenticate,
        ), mock.patch(
            "rez_docbot.publishers.generic.GitPublisher._copy_documentation_if_needed"
        ) as copier:
            publisher.authenticate()
            publisher.quick_publish(expected_documentation)

        found_documentation, found_root = copier.call_args[0]

        expected_relative_path = relative_path.format(package=package)
        self.assertEqual(expected_documentation, found_documentation)
        self.assertEqual(
            os.path.join(clone_path, expected_relative_path),
            found_root,
        )


class Publish(unittest.TestCase):
    """Make sure :class:`rez_docbot.publishers.github.Github` works."""

    def test_initialization(self):  # pylint: disable=no-self-use
        """Make sure :class:`rez_docbot.publishers.github.Github` instantiates."""
        boilerplate.get_quick_publisher(
            {
                "authentication": [
                    {
                        "token": "fake_access_token",
                        "user": "fake_user",
                    },
                ],
                "publisher": "github",
                "repository_uri": "git@github.com:FakeUser/{package.name}",
                "view_url": "https://www.some_fake.website",
            }
        )


from . import run_test


def _make_headless_repository(suffix):
    """Create a headless git repository.

    For the sake of unittests, this directory is used in place of an actual
    remote repository.

    Args:
        suffix (str): Some phrase used to identify the directory.

    Returns:
        str: An absolute path to a directory on-disk.

    """
    directory = package_wrap.make_temporary_directory(suffix)

    base.Repo.init(directory, bare=True)

    return directory


def _make_package_with_remote():
    """tuple[rez.packages.Package, str]: A source Rez package in some git repository."""
    directory = tempfile.mkdtemp(suffix="_make_package_with_remote")

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "some_package"

                version = "1.0.0"
                """
            )
        )

    repository = base.Repo.init(directory)
    push_url = "git@foo.com:Thing/blah.git"
    repository.create_remote("origin", url=push_url)
    package = finder.get_nearest_rez_package(directory)

    return package, push_url


def _make_temporary_file(suffix, text=""):
    """Make a quick file, for testing.

    Args:
        suffix (str): A unique identifier for the file.
        text (str, optional): Text to write into the file, if needed.

    Returns:
        str: The created file.

    """
    _, path = tempfile.mkstemp(suffix=suffix)
    atexit.register(functools.partial(os.remove, path))

    if not text:
        return path

    with io.open(path, "w", encoding="utf-8") as handler:
        handler.write(text)

    return path
