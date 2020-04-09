#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import os
import stat

from rez import serialise
from rez_utilities import inspection
from six.moves import io

from . import _build_command


_FORMATS = {"package." + item.name: item for item in serialise.FileFormat}


def _get_build_command():
    return inspect.getsource(_build_command)


def _get_package_full_path(root):
    for name in _FORMATS.keys():
        path = os.path.join(root, name)

        if os.path.isfile(path):
            return path

    return ""


def _update_package(package):
    package.build_command = "python {root}/rezbuild.py"

    package_path = _get_package_full_path(inspection.get_package_root(package))

    if not package_path:
        raise RuntimeError('Package "{package}" has no path on-disk'.format(package=package))

    package_name = os.path.basename(package_path)
    format_ = _FORMATS[package_name]
    buffer_ = io.StringIO()
    package.print_info(buf=buffer_, format_=format_)

    # Set `package_path` to writable
    # Reference: https://stackoverflow.com/a/16249655
    os.chmod(package_path, stat.S_IWGRP)

    with open(package_path, "w") as handler:
        handler.write(buffer_.getvalue())


def add_build_command(package):
    root = inspection.get_package_root(package)

    with open(os.path.join(root, "rezbuild.py"), "w") as handler:
        handler.write(_get_build_command())

    _update_package(package)
