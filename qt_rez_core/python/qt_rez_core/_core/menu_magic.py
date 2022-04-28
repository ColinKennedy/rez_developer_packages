"""Functions for converting Rez package `help`_ attributes to Qt objects."""

import functools
import inspect
import os

import six
from Qt import QtWidgets
from rez import package_help
from rez_utilities import finder


def _get_anything(entry):
    """bool: Don't filter ``entry``."""
    return True


def _get_actions(package, matches=_get_anything):
    """Get a Qt action for every `help`_ entry in ``package``.

    Args:
        package (rez.packages.Package):
            An **installed** Rez package to query `help`_ entries from.
        matches (callable[tuple[str, str]] or str, optional):
            Any entry which returns ``True`` from the given function will be
            returned as actions in the menu. If a string is given, it's
            retreated as a regular Python ``in`` partial match. If no
            ``matches`` is given, every `help`_ entry is returned.

    Returns:
        list[Qt.QtWidgets.QAction]: Each found entry, as a pressable button.

    """

    def _in(phrase, text):
        return phrase in text

    help_ = package.help

    if not help_:
        raise RuntimeError(
            'Package "{package}" has no help attribute.'.format(package=package)
        )

    if isinstance(help_, six.string_types):
        # This matches how :class:`rez.package_help.PackageHelp` does it
        help_ = [["Help", help_]]

    if isinstance(matches, six.string_types):
        matches = functools.partial(_in, matches)

    help_caller = package_help.PackageHelp(package.name)
    help_caller.package = package
    actions = []

    for index, entry in enumerate(help_):
        if not matches(entry):
            continue

        label, _ = entry
        action = QtWidgets.QAction(label)
        action.triggered.connect(functools.partial(help_caller.open, index))

        actions.append(action)

    return actions


def _get_menu(package, matches=_get_anything):
    """Get a Qt menu containing all `help`_ entries for the Rez ``package``.

    Args:
        package (rez.packages.Package):
            An **installed** Rez package to query `help`_ entries from.
        matches (callable[tuple[str, str]] or str, optional):
            Any entry which returns ``True`` from the given function will be
            returned as actions in the menu. If a string is given, it's
            retreated as a regular Python ``in`` partial match. If no
            ``matches`` is given, every `help`_ entry is returned.

    Returns:
        Qt.QtWidgets.QMenu: The generated menu.

    """
    menu = QtWidgets.QMenu()

    for action in _get_actions(package, matches=matches):
        menu.addAction(action)

    return menu


def get_current_help_menu(directory="", matches=_get_anything):
    """Get a Qt menu containing all `help`_ entries for the Rez package in ``directory``.

    Args:
        directory (str, optional):
            The absolute folder on-disk to an **installed** Rez package. If no
            folder is given, it is automatically queried by checking the caller
            function's file location.
        matches (callable[tuple[str, str]] or str, optional):
            Any entry which returns ``True`` from the given function will be
            returned as actions in the menu. If a string is given, it's
            retreated as a regular Python ``in`` partial match. If no
            ``matches`` is given, every `help`_ entry is returned.

    Returns:
        Qt.QtWidgets.QMenu: The generated menu.

    """
    if not directory:
        current_frame = inspect.currentframe()
        caller_frame = current_frame.f_back
        file_path, _, _, _, _ = inspect.getframeinfo(caller_frame)

        directory = os.path.dirname(file_path)

    package = finder.get_nearest_rez_package(directory)

    return _get_menu(package, matches=matches)
