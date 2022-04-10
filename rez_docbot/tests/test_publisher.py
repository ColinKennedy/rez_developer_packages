"""General publishing-related unittests and integration tests for :ref:`rez_docbot`."""

import contextlib
import unittest

from python_compatibility import website

from rez_docbot.core import preference

from .common import run_test


class Publish(unittest.TestCase):
    """Make sure :class:`rez_docbot.core.publisher_.Publisher` works."""

    @unittest.skipIf(
        not website.is_internet_on(), "External Internet is not accessible."
    )  # pylint: disable=no-self-use
    def test_authentication(self):
        """Make sure :class:`rez_docbot.core.publisher_.Publisher` authenticates."""
        # TODO : Make a burner account so we can use it in this test
        with _get_quick_publisher(
            {
                "authentication": [
                    {
                        "token": "fake_access_token",
                        "type": "github",
                        "user": "fake_user",
                    },
                ],
                "repository_uri": "git@github.com:FakeUser/{package.name}",
                "view_url": "https://www.some_fake.website",
            }
        ) as publisher:
            publisher.authenticate()

    def test_initialization(self):  # pylint: disable=no-self-use
        """Make sure :class:`rez_docbot.core.publisher_.Publisher` instantiates."""
        with _get_quick_publisher(
            {
                "authentication": [
                    {
                        "token": "fake_access_token",
                        "type": "github",
                        "user": "fake_user",
                    },
                ],
                "repository_uri": "git@github.com:FakeUser/{package.name}",
                "view_url": "https://www.some_fake.website",
            }
        ):
            pass


@contextlib.contextmanager
def _get_quick_publisher(configuration):
    """Make a quick Publisher, based on ``configuration``.

    This function assumes that ``configuration`` only defines a single Publisher.

    Args:
        configuration (dict[str, object]):
            The :ref:`rez_docbot` preferences to use in order to create the Publisher.

    Yields:
        :class:`rez_docbot.core.publisher_.Publisher`: The generated instance.

    """
    with run_test.keep_config() as config:
        config.optionvars["rez_docbot"] = {"publishers": [configuration]}

        yield preference.get_base_settings()["publishers"][0]
