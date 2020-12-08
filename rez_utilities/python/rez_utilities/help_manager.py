#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for interfacing with any Rez package's `help` attribute."""

import fnmatch
import functools
import logging
import os
import sys
import traceback

import six
from python_compatibility import filer, iterbot, pathrip

from . import finder, rez_configuration

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_LOGGER = logging.getLogger(__name__)


def _discover_external_directory(excludes=frozenset()):
    """Find the first directory in the call stack which comes from outside of `excludes`.

    Args:
        excludes (set[str]):
            The absolute path to any directory which should be ignored
            while running this function. Default default, even if no
            paths are given, this module's current Rez package is always excluded.

    Raises:
        RuntimeError: If no external file path could be found or resolved.

    """
    file_path = _get_first_external_path(excludes=excludes)

    if not file_path:
        raise RuntimeError(
            "No directory was provided and the caller directory could not be found."
        )

    directory = os.path.dirname(file_path)

    if os.path.isdir(directory):
        return directory

    resolved = _resolve_rez_path(file_path)

    if not resolved:
        raise RuntimeError(
            'No directory was found. The found path "{file_path}" is not a valid file path. '
            'And no "real" path could be automatically found.'.format(
                file_path=file_path
            )
        )

    return os.path.dirname(resolved)


def _get_first_external_path(excludes=frozenset()):
    """Find the path of the Python file which calls this function.

    This function excludes paths within this same Rez package, for simplicity's sake.

    Args:
        excludes (set[str]):
            The absolute path to any directory which should be ignored
            while running this function. Default default, even if no
            paths are given, this module's current Rez package is always excluded.

    Returns:
        str: The found caller path, if any.

    """
    package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)
    root = os.path.dirname(package.filepath)

    excludes = set(excludes)
    excludes.add(root)

    for source_path, _, _, _ in reversed(traceback.extract_stack()):
        # If `source_path` isn't within any of the excluded paths,
        # return it. Otherwise if `source_path` does match at least one
        # of the excluded paths, keep searching.
        #
        for path in excludes:
            if filer.in_directory(source_path, path):
                break
        else:
            return source_path

    return ""


def _resolve_matches(matches):
    """Convert `matches` into a callable function for :func:`get_data` to use.

    Args:
        matches (str or callable[str] -> bool):
            If an empty string is given, a function which always return
            True is returned. If a non-empty string is given, a function
            which uses a glob expression is returned. And if `matches`
            is already a function, it's returned.

    Returns:
        callable[str] -> bool: The given `matches` or an auto-generated function.

    """

    def _return_true(_):
        return True

    def _matches(text, pattern):
        return text.startswith(pattern) or fnmatch.fnmatch(text, pattern)

    if not matches:
        return _return_true

    if isinstance(matches, six.string_types):
        return functools.partial(_matches, pattern=matches)

    return matches


def _resolve_rez_path(path):
    """Find the first path in :attr:`sys.path` which represents some given `path`.

    Python .egg paths tend to be incomprehensible, like
    "build/some_rez_package/1.0.0/namespace/file.py". So this function's
    job is to find the "real", location of the egg where file.py came
    from. This function is only an approximation. After all, file.py
    isn't actually a literal file on disk. It's a resource, within a
    .egg file.

    This function assumes that the .egg comes from another Rez package.
    And installed Rez packages are always named after the Rez package
    family + version. So we split the path up and use that name +
    version pair to find the real .egg path.

    Args:
        path (str): Some raw stack line to the contents of a Python .egg file.

    Returns:
        str: The found real path, if any.

    """
    parts = pathrip.split_os_path_asunder(path)

    if not parts:
        return ""

    if parts[0] == "build":
        parts[:] = parts[1:]

    all_sys_parts = [
        (sys_path, pathrip.split_os_path_asunder(sys_path)) for sys_path in sys.path
    ]

    for name, version in iterbot.make_chains(parts):
        for sys_path, sys_parts in all_sys_parts:
            try:
                next(iterbot.iter_sub_finder([name, version], sys_parts))
            except StopIteration:
                # Nothing was found. Just ignore the path.
                continue

            return sys_path

    return ""


def get_data(directory="", matches="", resolve=True, excludes=frozenset()):
    """Get a Rez package's help information.

    Args:
        directory (str, optional): The absolute path on-disk where
            a Rez package is assumed to be in. If no folder is given,
            this function will automatically find the Rez package which
            called this function and use that directory, instead.
        matches (str or callable[str] -> bool, optional): If nothing is given,
            the whole `help` attribute is returned. If a string is
            given, it matches the string against each key as a glob
            expression. Matches are returned. If a function is given,
            all True return values are shown and False are not. Default: "".
        resolve (bool, optional): If True and a `help` value is pointing
            to a relative path on-disk, that path is expanded into an
            absolute path and returned. If False, the path is returned
            as-is without being modified. Default is True.
        excludes (set[str]): The absolute path to any directory which
            should be ignored while running this function. Default
            default, even if no paths are given, this module's current
            Rez package is always excluded.

    Raises:
        ValueError: If no `directory` is given and one couldn't be automatically found.
        RuntimeError: If the `directory` has no Rez package inside of it.

    Returns:
        list[list[str, str]]: Each found package help key and value, if any.

    """
    matches = _resolve_matches(matches)

    if not directory:
        directory = _discover_external_directory(excludes=excludes)
        _LOGGER.debug('Directory "%s" was found.', directory)

    if not os.path.isdir(directory):
        raise ValueError(
            'Text "{directory}" is not a directory.'.format(directory=directory)
        )

    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise RuntimeError(
            'Directory "{directory}" is not in a Rez package.'.format(
                directory=directory
            )
        )

    _LOGGER.debug('Found package "%s".', package)

    if not package.help:
        return []

    package_directory = os.path.dirname(package.filepath)

    if isinstance(package.help, six.string_types):
        help_ = [[rez_configuration.DEFAULT_HELP_LABEL, package.help]]
    else:
        help_ = package.help or []

    output = []

    for key, path in help_:
        if not matches(key):
            continue

        if resolve:
            # Rez package `help` attributes are usually relative paths
            # or website URLs. If it's a file path, we need to make it
            # absolute again.
            #
            resolved_path = os.path.join(package_directory, path)

            if os.path.exists(resolved_path):
                path = resolved_path

        output.append([key, path])

    return output
