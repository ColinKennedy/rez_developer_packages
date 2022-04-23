#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module to change parts of a Rez package."""

import copy
import os

import parso
from parso.python import tree
from rez import serialise
from rez.utils import filesystem
from rez.vendor.version import version as version_
from rez_industry.core import convention, parso_utility


def _write_package_to_disk(package, version):
    """Update a Rez package on-disk with its new contents.

    Args:
        package (:class:`rez.packages_.DeveloperPackage`):
            Some package on-disk to write out.
        version (str): The new semantic version that will be written to-disk.

    """
    with open(package, "r") as handler:
        code = handler.read()

    graph = parso.parse(code)

    try:
        assignment = parso_utility.find_assignment_nodes("version", graph)[-1]
    except IndexError:
        assignment = None

    prefix = " "

    if assignment:
        prefix = assignment.children[0].prefix.strip("\n") or prefix

    node = tree.String('"{version}"'.format(version=version), (0, 0), prefix=prefix)
    graph = convention.insert_or_append(node, graph, assignment, "version")

    # Writing to DeveloperPackage objects is currently bugged.
    # So instead, we disable caching during write.
    #
    # Reference: https://github.com/nerdvegas/rez/issues/857
    #
    with filesystem.make_path_writable(os.path.dirname(os.path.dirname(package))):
        with serialise.open_file_for_write(package) as handler:
            handler.write(graph.get_code())


def bump_version(version, minor, absolute=False, normalize=False):
    """Bump the Rez package version minor.

    Args:
        version (:class:`rez.vendor.version.version.Version`):
            The major / minor / patch semantic data that will be bumped.
        minor (int):
            The new value to bump in `version`.
        absolute (bool, optional):
            If True, instead of adding to an existing version number,
            the given version information will be replaced with whatever
            number is given. If False, the value is added, instead.
            Default is False.
        normalize (bool, optional):
            If True, all values below the minor will be reset to 0.
            If False, the values below the minor keep their original values.
            Default is False.

    Returns:
        :class:`rez.vendor.version.version.Version`:
            The modified `version` but with a new minor.

    """

    def _bump(version, position, value, absolute=False):
        version = copy.deepcopy(version)

        if position == "minor":
            if absolute:
                new_value = value
            else:
                new_value = int(str(version.minor)) + value

            new_token = version_.NumericToken(str(new_value))
            version.tokens[1] = new_token
            # Force `version` to update by deleting its internal cache
            version._str = None  # pylint: disable=protected-access

            return version

        raise NotImplementedError("Need to support non-minor bumps.")

    def _normalize(version, position):
        version = copy.deepcopy(version)

        version.tokens[position + 1 :] = [
            version_.NumericToken("0") if str(token).isdigit() else token
            for token in version.tokens[position + 1 :]
        ]

        # Force `version` to update by deleting its internal cache
        version._str = None  # pylint: disable=protected-access

        return version

    positions = []

    if minor:
        positions.append(("minor", minor))

    for position, value in positions:
        version = _bump(version, position, value, absolute=absolute)

    if normalize:
        version = _normalize(version, positions[-1][1])

    return version


def bump(package, minor=0, absolute=False, normalize=False):
    """Change the version of `package`.

    Reference:
        https://semver.org

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
        normalize (bool, optional):
            If True, all values below the minor will be reset to 0.
            If False, the values below the minor keep their original values.
            Default is False.

    Raises:
        ValueError:
            If `minor` is undefined when `absolute` is False or if
            `minor` is negative when `absolute` is True.

    """
    if not absolute and not minor:
        raise ValueError("Nothing to do. No value was given to `minor`.")

    if absolute and minor < 0:
        raise ValueError(
            'Minor "{minor}" cannot be less than zero when absolute is True.'.format(
                minor=minor
            )
        )

    version = package.version or ""

    if not version:
        raise RuntimeError(
            'No version exists so Package "{package}" could not be bumped.'
            "".format(package=package)
        )

    version = bump_version(version, minor, absolute=absolute, normalize=normalize)

    _write_package_to_disk(package.filepath, version)
