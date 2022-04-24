"""Make sure `GitHub`_-related unittests and integration tests work."""

import atexit
import contextlib
import functools
import io
import os
import tempfile
import textwrap
import unittest

from python_compatibility import website
from rez_docbot.core import preference
from six.moves import mock
import schema

from .common import run_test

# TODO : Need test for ...
#
# - skipping version generation
# - publishing over an existing version folder
# - overwriting latest
# - skipping overwriting latest (because the user is back-patching)

# TODO : Add mono publishing support
# should be able to publish to the same repository as the current package!
# TODO : Add any-version-publishing use-case


class Authentication(unittest.TestCase):
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
            )
        )

        with _get_quick_publisher(
            {
                "authentication": [{"payload": path, "type": "from_json_path"}],
                "publisher": "github",
                "repository_uri": "git@github.com:FakeUser/{package.name}",
                "view_url": "https://www.some_fake.website",
            }
        ) as publisher:
            publisher.authenticate()

        _, path = tempfile.mkstemp(suffix="_does_not_exist.json")
        os.remove(path)

        with self.assertRaises(schema.SchemaError):
            with _get_quick_publisher(
                {
                    "authentication": [
                        {"payload": "/does/not/exist.json", "type": "from_json_path"}
                    ],
                    "publisher": "github",
                    "repository_uri": "git@github.com:FakeUser/{package.name}",
                    "view_url": "https://www.some_fake.website",
                }
            ) as publisher:
                publisher.authenticate()

    @unittest.skipIf(
        not website.is_internet_on(), "External Internet is not accessible."
    )  # pylint: disable=no-self-use
    def test_normal(self):
        """Make sure :class:`rez_docbot.publishers.github.Github` authenticates."""
        # TODO : Make a burner account so we can use it in this test, if needed
        with _get_quick_publisher(
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
        ) as publisher:
            publisher.authenticate()


class Publish(unittest.TestCase):
    """Make sure :class:`rez_docbot.publishers.github.Github` works."""

    def test_initialization(self):  # pylint: disable=no-self-use
        """Make sure :class:`rez_docbot.publishers.github.Github` instantiates."""
        with _get_quick_publisher(
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
        ):
            pass


# TODO : Remove this context if not needed, later
@contextlib.contextmanager
def _get_quick_publisher(configuration):
    """Make a quick Publisher, based on ``configuration``.

    This function assumes that ``configuration`` only defines a single Publisher.

    Args:
        configuration (dict[str, object]):
            The :ref:`rez_docbot` preferences to use in order to create the Publisher.

    Yields:
        :class:`rez_docbot.bases.base.Publisher`: The generated instance.

    """
    package = mock.MagicMock()

    del package.rez_docbot_configuration

    with run_test.keep_config() as config:
        config.optionvars["rez_docbot"] = {"publishers": [configuration]}

        yield preference.get_base_settings(package)["publishers"][0]


def _make_temporary_file(suffix, text=""):
    _, path = tempfile.mkstemp(suffix=suffix)
    atexit.register(functools.partial(os.remove, path))

    if not text:
        return path

    with io.open(path, "w", encoding="utf-8") as handler:
        handler.write(text)

    return path
