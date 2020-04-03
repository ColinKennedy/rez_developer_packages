#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module which controls symlink baking."""

import logging
import os

from rez import exceptions, resolved_context
from rez_utilities import inspection

from . import pather

_LOGGER = logging.getLogger(__name__)


def bake_from_current_environment(directory, force=False):
    """Generate symlinks to reproduce the current environment.

    Args:
        directory (str):
            The absolute path to a directory on-disk to place the
            symlinks under. This path can later be fed directly into
            REZ_PACKAGES_PATH to reproduce the environment.
        force (bool, optional):
            If True, delete any symlinks that may already exist.
            If False and symlinks exist, normal exceptions will be raised.
            Default is False.

    Raises:
        EnvironmentError: If the user is not in a Rez-resolved environment.

    """
    paths = pather.get_paths_from_environment(os.environ.items())

    if not paths:
        raise EnvironmentError(
            "bake_from_current_environment cannot be run because you are not in a Rez environment."
        )

    make_symlinks(paths, directory, force=force)


def bake_from_request(request, directory, force=False):
    """Generate symlinks for a user's given Rez package request.

    Args:
        request (list[str]):
            The Rez packages to make into a Rez resolve.
        directory (str):
            The absolute path to a directory on-disk to place the
            symlinks under. This path can later be fed directly into
            REZ_PACKAGES_PATH to reproduce the environment.
        force (bool, optional):
            If True, delete any symlinks that may already exist.
            If False and symlinks exist, normal exceptions will be raised.
            Default is False.

    Raises:
        ValueError: If `request` contains 1+ package that does not exist.

    """
    try:
        context = resolved_context.ResolvedContext(request)
    except exceptions.PackageFamilyNotFoundError:
        _LOGGER.exception('Request "%s" was not found.', request)

        raise ValueError('Request "{request}" was not found.'.format(request=request))

    paths = pather.get_paths_from_environment(context.get_environ().items())
    make_symlinks(paths, directory, force=force)


def make_symlinks(paths, directory, force=False):
    """Make symlinks for all of the given Rez-specific paths and place them under `directory`.

    Args:
        paths (iter[str]):
            Each installed Rez package path to generate symlinks for.
        directory (str):
            The absolute path to a directory on-disk to place the
            symlinks under. This path can later be fed directly into
            REZ_PACKAGES_PATH to reproduce the environment.
        force (bool, optional):
            If True, delete any symlinks that may already exist.
            If False and symlinks exist, normal exceptions will be raised.
            Default is False.

    """
    for path in paths:
        package = inspection.get_nearest_rez_package(path)
        root = inspection.get_packages_path_from_package(package)

        relative_directory = os.path.relpath(path, root)
        destination_directory = os.path.join(directory, relative_directory)
        destination_root = os.path.dirname(destination_directory)

        if not os.path.isdir(destination_root):
            os.makedirs(destination_root)

        if force and os.path.exists(destination_directory):
            os.remove(destination_directory)

        os.symlink(path, destination_directory)
