#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that is devoted to querying Sphinx documentation information.

Most of the functions here assume reasonable conventions about how
folders are named and the data that could be returned.

Note:
    The logic of the functions in this module go generally like this

    "If we find API documentation, assume that it is Sphinx API
    documentation and don't bother checking."

    "But if it is just general documentation, double-check to make sure
    that the documentation is compatible with Sphinx before recommending
    / returning the URL."

"""

import logging
import os
import sys

from .. import imports
from . import exceptions

_LOGGER = logging.getLogger(__name__)
SETTINGS_FILE = "conf.py"


def _is_sphinx_configuration_file(path):
    """Check if the given Python file is a valid Sphinx conf.py file.

    Args:
        path (str): The Sphinx conf.py to check for issues.

    Returns:
        bool: If `path` is or is not a correct conf.py file.

    """
    try:
        module = import_conf_file(path)
    except Exception:  # pylint: disable=broad-except
        _LOGGER.warning('Path "%s" could not be imported.', path, exc_info=True)

        return False

    required_attributes = ("project", "release", "version")
    missing = set()

    for attribute in required_attributes:
        if not hasattr(module, attribute):
            missing.add(attribute)

    if missing:
        _LOGGER.warning(
            'Path "%s" is missing these required keys "%s".', path, sorted(missing)
        )

        return False

    return True


def _guess_conf_file(directory):
    """Find the Sphinx conf.py file that describes the documentation settings.

    Args:
        directory (str): The absolute directory that likely has a conf.py inside of it.

    Returns:
        str: The full path to the found conf.py file, if any.

    """
    for root, _, files in os.walk(directory):
        for path in files:
            if path != SETTINGS_FILE:
                continue

            conf_file = os.path.join(root, path)

            if _is_sphinx_configuration_file(conf_file):
                return conf_file
            else:
                _LOGGER.debug(
                    'File "%s" was found but it is not a valid Sphinx file.', conf_file
                )

    return ""


def get_conf_file(directory):
    """Find the Sphinx settings conf.py file.

    Args:
        directory (str):
            The root folder for (presumably) a Rez package. The folder
            should be above the "documentation" folder.


    Raises:
        :class:`.SphinxFileBroken`:
            If there is a found documentation file but it is invalid.

    Returns:
        str: The absolute path to the Sphinx conf.py file, if it exists.

    """
    common_conventions = [
        ("documentation", "source", SETTINGS_FILE),
        ("docs", "source", SETTINGS_FILE),
        ("documentation", SETTINGS_FILE),
        ("docs", SETTINGS_FILE),
    ]

    for option in common_conventions:
        path = os.path.join(directory, *option)

        if os.path.isfile(path):
            if not _is_sphinx_configuration_file(path):
                raise exceptions.SphinxFileBroken(
                    'Path "{path}" was found but is an invalid conf.py file.'.format(
                        path=path
                    )
                )

            return path

    return _guess_conf_file(directory)


def import_conf_file(path):
    """Import a Sphinx "conf.py" file as a Python module.

    Args:
        path (str): The absolute path to a Sphinx "conf.py" file.

    Returns:
        module: The imported Python code object.

    """
    try:
        return imports.import_file("conf", path)
    except Exception:  # pylint: disable=broad-except
        raise
    finally:
        # Import the Python module but remove "conf" from the global
        # module namespace. Otherwise, if this functions if called
        # repeatedly with different `path` values, it'll cause
        # unexpected results.
        #
        if "conf" in sys.modules:
            del sys.modules["conf"]
