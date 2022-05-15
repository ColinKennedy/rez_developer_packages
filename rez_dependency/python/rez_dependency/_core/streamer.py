"""Wrap Python's built-in :func:`print` so it's easier to unittest / debug."""

from __future__ import print_function


def printer(*args, **kwargs):
    """Wrap Python's built-in :func:`print` so it's easier to unittest / debug."""
    print(*args, **kwargs)
