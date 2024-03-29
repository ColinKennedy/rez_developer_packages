#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A basic module for finding top-level information about Rez packages."""

import logging
import os

from rez import exceptions, packages_
from rez.vendor.schema import schema

_LOGGER = logging.getLogger(__name__)


# Note: Pylint's missing-raises-doc is bugged. Remove the disable= once it's fixed
def get_package_root(package):  # pylint: disable=missing-raises-doc
    """Find the directory that contains the gizen Rez package.

    Depending on if the Rez package is a regular package or a developer
    package, the logic is slightly different.

    Args:
        package (:class:`rez.packages_.Package`):
            The built or source Rez package to get a valid path from.

    Raises:
        EnvironmentError:
            If the found Rez package does not have a root folder. This
            exception should only happen if the Rez package is damaged
            somehow.

    Returns:
        str: The found folder. A Rez package should always have a root folder.

    """
    path_to_package = package.resource.location

    if not os.path.isdir(path_to_package) and hasattr(package, "filepath"):
        return os.path.dirname(package.filepath)

    path = os.path.join(path_to_package, package.name, str(package.version))

    if not os.path.isdir(path):
        raise EnvironmentError(
            'Package "{package}" has an invalid path "{path}".'
            "".format(package=package, path=path)
        )

    return os.path.normcase(os.path.realpath(path))


def get_nearest_rez_package(directory):
    """Assuming that `directory` is on or inside a Rez package, find the nearest Rez package.

    Args:
        directory (str):
            The absolute path to a folder on disk. This folder should be
            a sub-folder inside of a Rez package to the root of the Rez package.

    Returns:
        :class:`rez.developer_package.DeveloperPackage` or NoneType: The found package.

    """
    previous = None
    original = directory

    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)

    while directory and previous != directory:
        previous = directory

        try:
            return packages_.get_developer_package(directory)
        except (
            # This happens if the package in `directory` is missing required data
            exceptions.PackageMetadataError,
            # This happens if the package in `directory` is written incorrectly
            schema.SchemaError,
        ):
            _LOGGER.debug('Directory "%s" found an invalid Rez package.', directory)

        directory = os.path.dirname(directory)

    _LOGGER.debug(
        'Directory "%s" is either inaccessible or is not part of a Rez package.',
        original,
    )

    return None
