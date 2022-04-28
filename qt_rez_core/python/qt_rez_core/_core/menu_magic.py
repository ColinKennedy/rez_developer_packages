"""Functions for converting Rez package `help`_ attributes to Qt objects."""

import functools
import inspect
import platform
import os
from rez.config import config
import webbrowser
import subprocess

import six
from six.moves import urllib_parse
from Qt import QtWidgets
from rez_utilities import finder


def _is_url(url):
    result = urllib_parse.urlparse(url)

    return all((result.scheme, result.netloc))


def _get_anything(entry):
    """bool: Don't filter ``entry``."""
    return True


def _get_absolute(sub, root):
    if os.path.isabs(sub):
        return sub

    absolute = os.path.join(root, sub)

    if not os.path.exists(absolute):
        return ""

    return os.path.normcase(absolute)


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

    def _in(phrase, entry):
        return phrase in entry[0]

    def _call(entry, package):
        @functools.wraps(_call)
        def wrap(*_, **__):
            _, destination = entry

            if _is_url(destination):
                _open_as_url(destination)

                return

            root = finder.get_package_root(package)
            absolute = _get_absolute(destination, root)

            if absolute:
                _open_generic(absolute)

                return

            _run_command(destination)

        return wrap

    help_ = package.help

    if not help_:
        raise RuntimeError(
            'Package "{package}" does not define a help attribute.'.format(package=package)
        )

    if isinstance(help_, six.string_types):
        # This matches how :class:`rez.package_help.PackageHelp` does it
        help_ = [["Help", help_]]

    if isinstance(matches, six.string_types):
        matches = functools.partial(_in, matches)

    actions = []

    for index, entry in enumerate(help_):
        if not matches(entry):
            continue

        label, _ = entry
        action = QtWidgets.QAction(label)
        action.triggered.connect(_call(entry, package))
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
        action.setParent(menu)  # Required or it breaks in PySide2-5(.15?)
        menu.addAction(action)

    return menu


def _open_as_url(destination):
    if not config.browser:
        webbrowser.open_new(destination)

        return

    process = subprocess.Popen([config.browser, destination])
    process.communicate()


def _open_generic(path):
    system = platform.system()

    if system == "Windows":
        # Reference: https://stackoverflow.com/a/1585848/3626104
        subprocess.Popen(["cmd", "/C", "start", path])
    elif system == "Linux":
        # Reference: https://stackoverflow.com/a/435631/3626104
        subprocess.Popen(["xdg-open", path])
    elif system == "Darwin":
        # Reference: https://stackoverflow.com/a/434612/3626104
        subprocess.Popen(["open", path])
    else:
        raise NotImplementedError(
            'System "{system}" is unknown. Please add support for it!'.format(system=system)
        )


def _run_command(destination):
    subprocess.Popen(destination, shell=True)


def get_current_help_menu(directory="", matches=_get_anything):
    # """Get a Qt menu containing all `help`_ entries for the Rez package in ``directory``.
    #
    # Args:
    #     directory (str, optional):
    #         The absolute folder on-disk to an **installed** Rez package. If no
    #         folder is given, it is automatically queried by checking the caller
    #         function's file location.
    #     matches (callable[tuple[str, str]] or str, optional):
    #         Any entry which returns ``True`` from the given function will be
    #         returned as actions in the menu. If a string is given, it's
    #         retreated as a regular Python ``in`` partial match. If no
    #         ``matches`` is given, every `help`_ entry is returned.
    #
    # Returns:
    #     Qt.QtWidgets.QMenu: The generated menu.
    #
    # """
    if not directory:
        current_frame = inspect.currentframe()
        caller_frame = current_frame.f_back
        file_path, _, _, _, _ = inspect.getframeinfo(caller_frame)

        directory = os.path.dirname(file_path)

    if not os.path.isdir(directory):
        raise ValueError(
            'Directory "{directory}" does not exist.'.format(directory=directory)
        )

    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise ValueError('Directory "{directory}" is not in a Rez package.'.format(directory=directory))

    return _get_menu(package, matches=matches)
