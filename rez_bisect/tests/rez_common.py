#!/usr/bin/env python

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
    root = variant.resource.location
    context = resolved_context.ResolvedContext(
        ["{variant.name}=={variant.version}".format(variant=variant)],
        package_paths=[root],
    )

    _, path = tempfile.mkstemp(suffix="_package_context")
    atexit.register(functools.partial(os.remove, path))

    context.save(path)

    return path


def make_package(directory, name="foo", version="1.0.0", is_bad=False):
    with package_maker.make_package(name, directory) as maker:
        maker.name = name
        maker.version = version

    variant = maker["installed_variants"][0]
    context = _make_context_from_package(variant)

    return context
