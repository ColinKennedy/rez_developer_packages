#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module to change parts of a Rez package."""

from rez import serialise
from six.moves import io

from . import inspection


def _write_package_to_disk(package, serializer=serialise.FileFormat.py):
    """Update a Rez package on-disk with its new contents.

    Args:
        package (:class:`rez.packages_.DeveloperPackage`):
            Some package on-disk to write out.
        serializer (:attr:`rez.serialise.FileFormat`):
            A supported file format to write the package out to.
            By default, it will be written out as a package.py file.

    """
    stream = io.StringIO()
    package.print_info(buf=stream, format_=serializer)
    source_code = stream.getvalue()

    with open(package.filepath, "w") as handler:
        handler.write(source_code)


def bump(package, minor=0, absolute=False):
    """Change the version of `package`.

    Args:
        package (:class:`rez.packages_.DeveloperPackage`):
            Some Rez file on-disk that can be changed and re-written.
        minor (int, optional):
            A value to add to the existing version of `package`.
            It can be positive or negative.
        absolute (bool, optional):
            If True, instead of adding to an existing version number,
            the given version information will be replaced with whatever
            number is given. If False, the value is added, instead.
            Default is False.

    Raises:
        ValueError:
            If `minor` is undefined when `absolute` is False or if
            `minor` is negative when `absolute` is True.

    """

    def _bump(text, value, position):
        raise NotImplementedError()

    if not absolute and not minor:
        raise ValueError('Nothing to do. No value was given to `minor`.')

    if absolute and minor < 0:
        raise ValueError('Minor "{minor}" cannot be less than zero when absolute is True.'.format(minor=minor))

    version = package.version or ""

    if not version:
        raise RuntimeError(
            'No version exists so Package "{package}" could not be bumped.'
            ''.format(package=package)
        )

    positions = set()

    if minor:
        positions.add((-2, minor))

    for index, value in positions:
        version = _bump(version, value, index)

    package.version = version
    _write_package_to_disk(package)

    root = inspection.get_package_root(package)

    return inspection.get_nearest_rez_package(root)
