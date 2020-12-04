#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for interfacing with any Rez package's `help` attribute."""

import fnmatch
import functools
import logging
import os
import traceback

import six
from python_compatibility import filer

from . import finder, rez_configuration

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_LOGGER = logging.getLogger(__name__)


def _get_first_external_path():
    """Find the path of the Python file which calls this function.

    This function excludes paths within this same Rez package, for simplicity's sake.

    Returns:
        str: The found caller path, if any.

    """
    package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)
    root = os.path.dirname(package.filepath)

    for source_path, _, _, _ in reversed(traceback.extract_stack()):
        if not filer.in_directory(source_path, root):
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


def get_data(directory="", matches="", resolve=True):
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

    """
    matches = _resolve_matches(matches)

    if not directory:
        file_path = _get_first_external_path()

        if not file_path:
            raise RuntimeError(
                "No directory was provided and the caller directory could not be found."
            )

        directory = os.path.dirname(file_path)
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
