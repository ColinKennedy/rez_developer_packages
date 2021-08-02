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


def _make_context_from_package(variant):
    """Convert a Rez package / variant into a resolved context.

    Args:
        variant (:class:`rez.packages.Variant`): The installed Rez package to convert.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`:
            The Rez context which includes `variant`.

    """
    root = variant.resource.location
    context = resolved_context.ResolvedContext(
        ["{variant.name}=={variant.version}".format(variant=variant)],
        package_paths=[root],
    )

    _, path = tempfile.mkstemp(suffix="_package_context")
    atexit.register(functools.partial(os.remove, path))

    context.save(path)

    return path


def make_context(directory, name="foo", version="1.0.0"):
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

    return _make_context_from_package(variant)
