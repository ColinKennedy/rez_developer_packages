"""Make sure :mod:`qt_rez_core.api` works."""

import unittest

from qt_rez_core import api


class GetCurrentMenu(unittest.TestCase):
    """Make sure :func:`qt_rez_core.api.get_current_help_menu` works."""

    def test_action_url(self):
        raise ValueError()

    def test_action_path(self):
        raise ValueError()

    def test_current_package(self):
        """Get this package's `help`_ attribute."""
        menu = api.get_current_help_menu()

        self.assertEqual(1, len(menu.actions()))

    def test_empty(self):
        """Fail if the Rez package has no `help`_ attribute."""
        raise ValueError()

    def test_find_from_caller(self):
        """Find a help option, using a callable function."""
        raise ValueError()

    def test_find_from_str(self):
        """Find a help option, using a :obj:`str`."""
        raise ValueError()

    def test_not_found(self):
        """Fail early if Rez package could be found."""
        raise ValueError()
