#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create helpful functions for building Rez packages, using Python."""

import os
import shutil
import sys


def _must_symlink():
    """bool: Check if the user wants symlinks, not copy files."""
    return "--symlink" in sys.argv[1:]


def _build(source, destination, items, symlink):
    """Copy or symlink all items in `source` to `destination`.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        items (iter[str]):
            The local paths to every item in `source` to copy / symlink.
        symlink (bool):
            If True, create symlinks for each item in `items`.
            Otherwise, copy the files. This parameter's default value is
            set using sys.argv but typically is False.

    Raises:
        RuntimeError: If any item in `items` does not exist.

    """
    for item in items:
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)

        if not os.path.exists(source_path):
            raise RuntimeError(
                'Path "{source_path}" does not exist. Cannot continue.'
                "".format(source_path=source_path)
            )

        if symlink:
            os.symlink(source_path, destination_path)
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        elif os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)


def build(source, destination, items, symlink=_must_symlink()):
    """Copy or symlink all items in `source` to `destination`.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        items (iter[str]):
            The local paths to every item in `source` to copy / symlink.
        symlink (bool, optional):
            If True, create symlinks for each item in `items`.
            Otherwise, copy the files. This parameter's default value is
            set using sys.argv but typically is False.

    """
    remove(destination)  # Clean any old build folder
    os.makedirs(destination)

    try:
        _build(source, destination, items, symlink=symlink)
    except RuntimeError:
        # If the build errors early for any reason, delete the
        # destination folder. This is done to prevent a situation where
        # we have a "partial install".
        #
        shutil.rmtree(destination)

        raise


def remove(path):
    """Delete whatever `path` is.

    Args:
        path (str): A directory or file or symlink.

    """
    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
