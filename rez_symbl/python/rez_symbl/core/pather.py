#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Path-related generic functions."""

import fnmatch


def get_paths_from_environment(environment):
    """Find every Rez build-path for a given environment.

    Args:
        environment (iter[tuple[str, str]]):
            The key/value environment variable pairs to parse. Usually
            this comes from `os.environ.items()` or a similar object
            structure.

    Returns:
        set[str]:
            Each found path. e.g. {
            "/install/location/package_a/1.0.0/variant-a",
            "/install/location/package_b/1.0.0/variant-b",
        }

    """

    paths = set()

    for key, value in environment:
        if fnmatch.fnmatch(key, "REZ_*_BASE"):
            paths.add(value)

    return paths
