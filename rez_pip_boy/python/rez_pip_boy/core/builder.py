#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module responsible for modifying Rez package files to make the ``rez_pip_boy`` compatible.

Mainly, ``rez_pip_boy`` makes certain assumptions about where tar files
go. This module keeps build processes and those files in-sync.

"""

import inspect
import os

from rez import serialise
from rez_utilities import inspection

from . import _build_command

_FORMATS = {"package." + item.name: item for item in serialise.FileFormat}


def _get_build_command():
    """str: The full rez file which later will become a rezbuild.py file."""
    return inspect.getsource(_build_command)


def add_build_file(package, name):
    """Change a Rez package so it's "buildable" by Rez again.

    Specifically, give the package a rezbuild.py file.

    Args:
        package (:class:`rez.packages_.Package`):
            A rez-pip generated Rez package which will be modified.
        name (str):
            The name which will be used for the build file. Usually this is "rezbuild.py".

    """
    root = inspection.get_package_root(package)

    with open(os.path.join(root, name), "w") as handler:
        handler.write(_get_build_command())
