#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module responsible for modifying Rez package files to make the ``rez_pip_boy`` compatible.

Mainly, ``rez_pip_boy`` makes certain assumptions about where tar files
go. This module keeps build processes and those files in-sync.

"""

from __future__ import unicode_literals

import inspect
import io
import logging
import os

from rez import serialise
from rez.vendor.version import version as version_
from rez_utilities import finder

from . import _build_command

_BUILD_FILE_NAME = "rezbuild.py"
_FORMATS = {"package." + item.name: item for item in serialise.FileFormat}
_LOGGER = logging.getLogger(__name__)


def _get_build_command():
    """str: The full rez file which later will become a rezbuild.py file."""
    return inspect.getsource(_build_command)


def _get_rez_pip_version_range():
    """Find the most appropriate version number(s) to add to unittests.

    If rez_pip_boy is semantically versioned (it should be), take the current
    version and cap it at the next major version.

    Returns:
        str: The found version range.

    """
    current = version_.Version(os.environ["REZ_REZ_PIP_BOY_VERSION"])
    major = current.major

    if not major:
        _LOGGER.debug('Version "%s" isn\'t semantic versioning.')

        return current.major

    if not str(major).isdigit():
        _LOGGER.debug('Major "%s" isn\'t a digit!')

        return current.major

    next_major = int(str(major)) + 1

    return "{current}+<{next_major}".format(current=current, next_major=next_major)


def get_normal_dependencies_overrides():
    """Get the key + value pairs needed when ``--no-dependencies`` is ommitted.

    Returns:
        dict[str, object]: Rez package specific data to append to a Rez variant, later.

    """
    return {
        "build_command": "python -m rez_pip_boy build-from-source",
        "private_build_requires": [
            "rez_pip_boy-{version_range}".format(
                version_range=_get_rez_pip_version_range()
            )
        ],
    }


def get_no_dependencies_overrides():
    """Get the key + value pairs needed when ``--no-dependencies`` is used.

    Returns:
        dict[str, object]: Rez package specific data to append to a Rez variant, later.

    """
    build_command = "python {{root}}/{_BUILD_FILE_NAME}".format(
        _BUILD_FILE_NAME=_BUILD_FILE_NAME
    )

    return {"build_command": build_command}


def add_build_file(package):
    """Change a Rez package so it's "buildable" by Rez again.

    Specifically, give the package a rezbuild.py file.

    Args:
        package (:class:`rez.packages_.Package`):
            A rez-pip generated Rez package which will be modified.

    """
    root = finder.get_package_root(package)
    encoding = "ascii"
    data = _get_build_command()

    if hasattr(data, "decode"):
        # Needed for Python 2. Python 3+ deprecates this method
        data = data.decode(encoding)

    with io.open(
        os.path.join(root, _BUILD_FILE_NAME), "w", encoding=encoding
    ) as handler:
        handler.write(data)
