#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic functions for querying a user's environment."""

from . import registry


def get_skip_reason(package, paths=None):
    """Check if there's a reason why `package` does not need documentation.

    This function's logic changes depending on the skip plugins that the
    user has registered.

    Args:
        package (:class:`rez.packages_.Package`):
            The Rez package to check.
        paths (list[str], optional):
            The locations on-disk that will be used to any
            Rez-environment-related work. Some plugins need these
            paths for resolving a context, for example. Default is None.

    Returns:
        str:
            A message that explains why `package` should not be
            processed. If the check passes, an empty string is returned,
            instead.

    """
    for checker in registry.get_skip_plugins():
        if checker.has_issue(package, paths=paths):
            return checker.get_message()

    return ""
