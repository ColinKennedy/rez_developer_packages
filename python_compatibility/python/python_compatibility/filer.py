#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A file-system related module."""

import os

from . import pathrip


def in_directory(path, directory, follow=True):
    """Check if `file` can be found in `directory`.

    Warning:
        `directory` does not actually need to be a folder on-disk for
        `path` to be "inside" of `directory` for this function to return True.

    Reference:
        https://stackoverflow.com/questions/3812849/

    Args:
        path (str):
            A file or folder that may or may not be in `directory`.
        directory (str):
            A parent folder of `path`.
        follow (bool, optional):
            If True, symlinks will be expanded and compared against.
            If False, the raw paths are compared without expanding symlinks.
            Default is True.

    Returns:
        bool: If `path` is inside of `directory`.

    """
    if not follow:
        return pathrip.get_common_prefix([path, directory]) == directory

    directory = os.path.join(os.path.realpath(directory), "")
    path = os.path.realpath(path)

    # return true, if the common prefix of both is equal to directory
    # e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
    #
    return os.path.commonprefix([path, directory]) == directory
