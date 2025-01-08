#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A basic module for finding top-level information about Rez packages."""

import logging
import os
import typing

from rez import developer_package, exceptions
from rez import packages as packages_
from rez.vendor.schema import schema

_LOGGER = logging.getLogger(__name__)


def get_package_root(package: packages_.Package) -> str:
    """Find the directory that contains the gizen Rez package.

    Depending on if the Rez package is a regular package or a developer
    package, the logic is slightly different.

    Args:
        package:
            The built or source Rez package to get a valid path from.

    Raises:
        EnvironmentError:
            If the found Rez package does not have a root folder. This
            exception should only happen if the Rez package is damaged
            somehow.

    Returns:
        The found folder. A Rez package should always have a root folder.

    """
    path_to_package = package.resource.location

    if not os.path.isdir(path_to_package) and hasattr(package, "filepath"):
        return typing.cast(str, os.path.dirname(package.filepath))

    path = os.path.join(path_to_package, package.name, str(package.version))

    if not os.path.isdir(path):
        raise EnvironmentError(
            'Package "{package}" has an invalid path "{path}".'
            "".format(package=package, path=path)
        )

    return path


def get_nearest_rez_package(
    directory: str,
) -> typing.Optional[developer_package.DeveloperPackage]:
    """Assuming that `directory` is on or inside a Rez package, find the nearest Rez package.

    Args:
        directory:
            The absolute path to a folder on disk. This folder should be
            a sub-folder inside of a Rez package to the root of the Rez package.

    Returns:
        The found package, if any.

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
