#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configurable functions to control the output of functions from this package."""

import contextlib
import itertools

import wurlitzer
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


def get_context():
    """:class:`contextlib.GeneratorContextManager`: Silence all C-level stdout messages."""
    return wurlitzer.pipes()


@contextlib.contextmanager
def patch_packages_path(paths):
    """Replace the paths that Rez uses to search for packages with `paths`.

    Example:
        with patch_packages_path(["/some/path"]):
            print('The paths are different now')

    Args:
        paths (list[str]): Directories on-disk to where to look for Rez package.

    """
    original = config.packages_path  # pylint: disable=no-member
    config.packages_path[:] = paths  # pylint: disable=no-member

    try:
        yield
    finally:
        config.packages_path[:] = original  # pylint: disable=no-member


@contextlib.contextmanager
def patch_release_packages_path(path):
    """Replace the paths that Rez uses to search for released packages with `path`.

    Example:
        with patch_release_packages_path("/some/path"):
            print('The paths are different now')

    Args:
        path (str): The directory on-disk to where to look for Rez package.

    """
    original = config.release_packages_path
    config.release_packages_path = path

    try:
        yield
    finally:
        config.release_packages_path = original
