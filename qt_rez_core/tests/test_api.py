"""Make sure :mod:`qt_rez_core.api` works."""

import atexit
import functools
import tempfile
import os
import shutil
import unittest

from qt_rez_core._core import menu_magic
from qt_rez_core import api
from six.moves import mock


class GetCurrentMenu(unittest.TestCase):
    """Make sure :func:`qt_rez_core.api.get_current_help_menu` works."""

    def test_action_command(self):
        """Simulate an action running some command."""
        package = mock.MagicMock()
        package.help = "do something.sh"

        menu = _test(package)

        with mock.patch("qt_rez_core._core.menu_magic._run_command") as patch:
            menu.actions()[0].triggered.emit()

        self.assertEqual(1, patch.call_count)

    def test_action_url(self):
        """Simulate an action opening some URL in a browser."""
        package = mock.MagicMock()
        package.help = "https://www.aol.com"

        menu = _test(package)

        with mock.patch("qt_rez_core._core.menu_magic._open_as_url") as patch:
            menu.actions()[0].triggered.emit()

        self.assertEqual(1, patch.call_count)

    def test_action_path_absolute(self):
        """Simulate an action opening an absolute file path."""
        package_path = os.path.join(
            _make_temporary_directory("_test_action_path_absolute"),
            "package.py",
        )
        path = _make_temporary_file("_test_find_from_str.py")
        package = mock.MagicMock()
        package.help = path
        package.filepath = package_path

        menu = _test(package)

        with mock.patch("qt_rez_core._core.menu_magic._open_generic") as patch:
            menu.actions()[0].triggered.emit()

        self.assertEqual(1, patch.call_count)

    def test_action_path_relative(self):
        """Simulate an action opening a file path which is relative to the package."""
        raise ValueError()
        package = mock.MagicMock()
        package.help = None

        menu = _test(package)

    def test_current_package(self):
        """Get this package's `help`_ attribute."""
        menu = api.get_current_help_menu()

        self.assertEqual(1, len(menu.actions()))

    def test_empty(self):
        """Fail if the Rez package has no `help`_ attribute."""
        package = mock.MagicMock()
        package.help = None

        with self.assertRaises(RuntimeError):
            _test(package)

    def test_find_from_caller(self):
        """Find a help option, using a callable function."""

        def _is_foo(entry):
            label, _ = entry

            return label == "FooBar"

        label = "FooBar"
        package = mock.MagicMock()
        package.help = [[label, "foo"], ["Foo Bar", "bar"]]

        menu = _test(package, matches=_is_foo)

        self.assertEqual(1, len(menu.actions()))
        self.assertEqual(label, menu.actions()[0].text())

    def test_find_from_str(self):
        """Find a help option, using a :obj:`str`."""
        path = _make_temporary_file("_test_find_from_str.py")
        package = mock.MagicMock()
        package.help = path

        menu = _test(package, matches="elp")

        expected_default_text = "Help"
        self.assertEqual(1, len(menu.actions()))
        self.assertEqual(expected_default_text, menu.actions()[0].text())

    def test_not_found(self):
        """Fail early if Rez package could be found."""
        with self.assertRaises(ValueError):
            api.get_current_help_menu(directory="/does/not/exist")

        directory = _make_temporary_directory("_test_not_found")

        with self.assertRaises(ValueError):
            api.get_current_help_menu(directory=directory)

    def test_help_str(self):
        """Find the help command, even if `help`_ is defined as a string."""
        path = _make_temporary_file("_test_find_from_str.py")
        package = mock.MagicMock()
        package.help = path

        menu = _test(package)

        expected_default_text = "Help"
        self.assertEqual(1, len(menu.actions()))
        self.assertEqual(expected_default_text, menu.actions()[0].text())


def _make_temporary_directory(suffix):
    directory = tempfile.mkdtemp(suffix=suffix)
    atexit.register(functools.partial(shutil.rmtree, directory))

    return directory


def _make_temporary_file(suffix):
    # TODO : doc
    _, path = tempfile.mkstemp(suffix=suffix)
    atexit.register(functools.partial(os.remove, path))

    return path


def _test(package, matches=menu_magic._get_anything):
    # TODO : doc
    return menu_magic._get_menu(package, matches=matches)
