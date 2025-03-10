#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configurable functions to control the output of functions from this package."""

import contextlib
import itertools
import platform
import typing

from rez import serialise
from rez.config import config

REZ_PACKAGE_NAMES = frozenset(
    name + "." + extension.lstrip(".")
    for name, format_ in itertools.product(
        config.plugins.package_repository.filesystem.package_filenames,
        serialise.FileFormat,
    )
    for extension in format_.value
)


def get_current_platform_as_rez_name() -> str:
    """Grab the current environment's platform, but as a Rez-friendly name.

    Raises:
        EnvironmentError: If no platform name could be found.

    Returns:
        The found platform name.

    """
    name = platform.system()
    choices = {"Linux": "linux", "Windows": "windows"}

    if name in choices:
        return choices[name]

    raise EnvironmentError(
        'Platform "{name}" is unknown. Options were "{choices}".'.format(
            name=name,
            choices=choices.keys(),
        )
    )


@contextlib.contextmanager
def patch_local_packages_path(
    paths: typing.List[str],
) -> typing.Generator[None, None, None]:
    """Replace the paths that Rez uses to search for packages with `paths`.

    Example:
        >>> with patch_local_packages_path("/some/path"):
        ...     print('The path is different now')

    Args:
        paths: Directories on-disk to where to look for Rez package.

    """
    original = config.local_packages_path  # pylint: disable=no-member
    config.local_packages_path = paths  # pylint: disable=no-member

    try:
        yield
    finally:
        config.local_packages_path = original  # pylint: disable=no-member


@contextlib.contextmanager
def patch_packages_path(paths: typing.List[str]) -> typing.Generator[None, None, None]:
    """Replace the paths that Rez uses to search for packages with `paths`.

    Example:
        >>> with patch_packages_path(["/some/path"]):
        ...     print('The paths are different now')

    Args:
        paths: Directories on-disk to where to look for Rez package.

    """
    original = list(config.packages_path)  # pylint: disable=no-member
    config.packages_path[:] = paths  # pylint: disable=no-member

    try:
        yield
    finally:
        config.packages_path[:] = original  # pylint: disable=no-member


@contextlib.contextmanager
def patch_release_packages_path(path: str) -> typing.Generator[None, None, None]:
    """Replace the paths that Rez uses to search for released packages with `path`.

    Example:
        >>> with patch_release_packages_path("/some/path"):
        ...     print('The paths are different now')

    Args:
        path: The directory on-disk to where to look for Rez package.

    """
    original = list(config.release_packages_path)
    config.release_packages_path = path

    try:
        yield
    finally:
        config.release_packages_path = original
