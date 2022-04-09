"""Make sure miscellaneous functions from :mod:`.preference` work.

These functions are important for internal uses of :ref:`rez_sphinx` but aren't
linked to specific configuration values. To see the configuration tests, check
out :doc:`test_preference_configuration`.

"""

import unittest

from rez_sphinx.preferences import preference


class GetMasterDocumentName(unittest.TestCase):
    """Ensure :func:`rez_sphinx.preferences.preference.get_master_document_name` works."""

    def test_global(self):
        raise ValueError()

    def test_package(self):
        raise ValueError()


class GetPreferenceFromPath(unittest.TestCase):
    """Ensure :func:`rez_sphinx.preferences.preference.get_preference_from_path` works."""

    def test_global(self):
        raise ValueError()

    def test_package(self):
        raise ValueError()


class GetPreferencePaths(unittest.TestCase):
    """Ensure :func:`rez_sphinx.preferences.preference.get_preference_paths` works."""

    def test_global(self):
        raise ValueError()

    def test_package(self):
        raise ValueError()


class PreferenceValidation(unittest.TestCase):
    """Ensure invalid settings are caught properly."""

    def test_global(self):
        raise ValueError()

    def test_package(self):
        raise ValueError()
