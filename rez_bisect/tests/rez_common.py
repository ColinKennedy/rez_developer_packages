#!/usr/bin/env python

"""Any functions which make unittesting with Rez easier."""

import atexit
import functools
import os
import tempfile

from rez import resolved_context

try:
    from rez import package_maker  # Newer Rez versions
except ImportError:
    from rez import package_maker__ as package_maker  # Older Rez versions


def make_combined_context(variants, package_paths=""):
    """Convert a Rez package / variant into a resolved context.

    Args:
        variants (container[:class:`rez.packages.Variant`]):
            The installed Rez package to convert.
        package_paths (str, optional):
            The directories to search within for packages. If no paths
            are given, default paths are found and used, instead.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`:
            The Rez context which includes `variant`.

    """
    if not package_paths:
        package_paths = {variant.resource.location for variant in variants}

    context = resolved_context.ResolvedContext(
        [
            "{variant.name}=={variant.version}".format(variant=variant)
            for variant in variants
        ],
        package_paths=package_paths,
    )

    _, path = tempfile.mkstemp(suffix="_package_context.rxt")

    context.save(path)

    return path


def make_variant(directory, name, version, commands="", requires=None):
    with package_maker.make_package(name, directory) as maker:
        maker.name = name
        maker.version = version

        if commands:
            maker.commands = commands

        if requires:
            maker.requires = requires

    return maker["installed_variants"][0]


def make_single_context(directory, name="foo", version="1.0.0"):
    """Create a Rez context which contains a fake `name`-`version` package.

    This function is meant specifically to make unittests simpler. It
    should not be used anywhere else.

    Args:
        directory (str):
            The absolute path to a folder on-disk where this new Rez
            package will go.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`:
            The Rez context which includes the fake Rez package.

    """
    with package_maker.make_package(name, directory) as maker:
        maker.name = name
        maker.version = version

    variant = maker["installed_variants"][0]

    return make_combined_context([variant])
