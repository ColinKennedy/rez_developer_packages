import contextlib
import unittest

from rez_docbot.core import preference
from python_compatibility import website

from .common import run_test


class Publish(unittest.TestCase):
    @unittest.skipIf(not website.is_internet_on(), "External Internet is not accessible.")
    def test_authentication(self):
        # TODO : Make a burner account so we can use it in this test
        with _get_quick_publisher(
            {
                "authentication": [
                    {
                        "access_token": "TODO FILL THIS OUT",
                        "type": "github",
                    },
                ],
                "repository_uri": "https://www.some_fake.website",
            }
        ) as publisher:
            publisher.authenticate()

    def test_initialization(self):
        with _get_quick_publisher(
            {
                "authentication": [
                    {
                        "access_token": "TODO FILL THIS OUT",
                        "type": "github",
                    },
                ],
                "repository_uri": "https://www.some_fake.website",
            }
        ) as publisher:
            raise ValueError(publisher)


@contextlib.contextmanager
def _get_quick_publisher(configuration):
    with run_test.keep_config() as config:
        config.optionvars["rez_docbot"] = {"publishers": [configuration]}

        yield preference.get_base_settings()["publishers"][0]
