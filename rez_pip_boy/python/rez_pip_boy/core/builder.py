#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module responsible for modifying Rez package files to make the ``rez_pip_boy`` compatible.

Mainly, ``rez_pip_boy`` makes certain assumptions about where tar files
go. This module keeps build processes and those files in-sync.

"""

import inspect
import os
import stat

from rez import serialise
from rez_utilities import inspection
from six.moves import io

from . import _build_command

_FORMATS = {"package." + item.name: item for item in serialise.FileFormat}


def _get_build_command():
    """str: The full rez file which later will become a rezbuild.py file."""
    return inspect.getsource(_build_command)


def _get_package_full_path(root):
    """Find the exact path to a Rez package.py / package.yaml file.

    I had trouble finding how to do this with native Rez API. Oh well.

    Args:
        root (str):
            An absolute directory path which is assumed to have a
            package definition file directly inside of it.

    Returns:
        str: The found path, if any.

    """
    for name in _FORMATS.keys():
        path = os.path.join(root, name)

        if os.path.isfile(path):
            return path

    return ""


def _update_package(package):
    """Change the given Rez package to work with ``rez_pip_boy``.

    Specifically, give the package a build command.

    Args:
        package (:class:`rez.packages_.Package`):
            A rez-pip generated Rez package which will be modified.

    Raises:
        RuntimeError: If no path on-disk could be fould to `package`.

    """
    package.build_command = "python {root}/rezbuild.py"

    package_path = _get_package_full_path(inspection.get_package_root(package))

    if not package_path:
        raise RuntimeError(
            'Package "{package}" has no path on-disk'.format(package=package)
        )

    package_name = os.path.basename(package_path)
    format_ = _FORMATS[package_name]
    buffer_ = io.StringIO()
    package.print_info(buf=buffer_, format_=format_)

    # Set `package_path` to writable
    # Reference: https://stackoverflow.com/a/16249655
    #
    os.chmod(package_path, stat.S_IWGRP)

    with open(package_path, "w") as handler:
        handler.write(buffer_.getvalue())


def add_build_command(package):
    """Change a Rez package so it's "buildable" by Rez again.

    Specifically, give the package a build command + rezbuild.py file.

    Args:
        package (:class:`rez.packages_.Package`):
            A rez-pip generated Rez package which will be modified.

    """
    root = inspection.get_package_root(package)

    with open(os.path.join(root, "rezbuild.py"), "w") as handler:
        handler.write(_get_build_command())

    _update_package(package)
