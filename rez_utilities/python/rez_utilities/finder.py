#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A basic module for finding top-level information about Rez packages."""

import itertools
import logging
import os

from rez import exceptions, packages_, serialise
from rez.config import config
from rez.vendor.schema import schema

_LOGGER = logging.getLogger(__name__)


def get_package_root(package):
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

    return path


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

    package_file_names = get_valid_package_names()

    while directory and previous != directory:
        previous = directory
        items = set(os.listdir(directory))

        if not any(True for name in package_file_names if name in items):
            directory = os.path.dirname(directory)

            continue

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


def get_valid_package_names():
    """set[str]: Find Rez package names. e.g. ``{"package.py", "package.yaml"}``."""
    package_file_names = config.plugins.package_repository.filesystem.package_filenames
    extensions = {
        extension
        for extensions_ in serialise.FileFormat.__members__.values()
        for extension in extensions_.value
    }

    output = set()

    for name, extension in itertools.product(package_file_names, extensions):
        output.add("{name}.{extension}".format(name=name, extension=extension))

    return output
