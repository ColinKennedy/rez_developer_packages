"""Make sure all version / latest logic works as expected."""

import unittest


class Publish(unittest.TestCase):
    """Skip / Overwrite documentation, under certain circumstances."""

    def test_any_version_never_skip(self):
        """Publish documentation for every new version, no matter what.

        .. seealso::

            :doc:`publishing_per_version`

        """
        raise ValueError()

    def test_overwrite_version(self):
        """Overwrite the version folder if the Rez package is a new patch."""
        raise ValueError()

    def test_overwrite_latest(self):
        """Overwrite the latest folder if the Rez package is a new version."""
        raise ValueError()

    def test_regex(self):
        """Allow users to specify a regular expression for finding versions."""
        raise ValueError()

    def test_skip_version(self):
        """Don't overwrite the version folder if the Rez package is an older patch."""
        raise ValueError()

    def test_skip_latest(self):
        """Don't overwrite the latest folder if the Rez package is an older version."""
        raise ValueError()
