#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create helpful functions for building Rez packages, using Python."""

import itertools
import logging
import os
import shutil
import sys
import zipfile

from . import exceptions

_LOGGER = logging.getLogger(__name__)


def must_symlink():
    """bool: Check if the user wants symlinks, not copy files."""
    return "--symlink" in sys.argv[1:]


def must_symlink_files():
    """bool: Check if the user wants symlinked files."""
    return "--symlink-folders" in sys.argv[1:]


def must_symlink_folders():
    """bool: Check if the user wants symlinked folders."""
    return "--symlink-folders" in sys.argv[1:]


def _make_egg(source, destination):
    """Make an egg from `source` and put it in `destination`.

    Args:
        source (str): The path to a file or folder on-disk.
        destination (str): The absolute path to somewhere on-disk where the .egg is saved.

    Raises:
        RuntimeError: If `source` does not exist.

    """
    if not os.path.exists(source):
        raise RuntimeError(
            'Path "{source}" does not exist. Cannot make an .egg.'.format(source=source)
        )

    with zipfile.ZipFile(destination, "w") as handler:
        if os.path.isdir(source):
            for root, directories, files in os.walk(source):
                for name in itertools.chain(directories, files):
                    path = os.path.join(root, name)
                    relative_path = os.path.relpath(path, source)
                    handler.write(path, arcname=relative_path)
        else:
            handler.write(source, arcname=os.path.basename(source))


def _run_command(
    command,
    source_path,
    destination_path,
    symlink,
    symlink_folders,
    symlink_files,
):
    if not os.path.exists(source_path):
        raise RuntimeError(
            'Path "{source_path}" does not exist. Cannot continue.'
            "".format(source_path=source_path)
        )

    if (
        symlink
        or (symlink_folders and os.path.isdir(source_path))
        or (symlink_files and os.path.isfile(source_path))
    ):
        _LOGGER.info('Creating "%s" symlink.', destination_path)
        os.symlink(source_path, destination_path)
    else:
        _LOGGER.info('Running command on "%s".', destination_path)
        command(source_path, destination_path)


def _build(source, destination, items, eggs, symlink, symlink_folders, symlink_files):
    # """Copy or symlink all items in `source` to `destination`.
    #
    # Args:
    #     source (str):
    #         The absolute path to the root directory of the Rez package.
    #     destination (str):
    #         The location where the built files will be copied or symlinked from.
    #     items (iter[str]):
    #         The local paths to every item in `source` to copy / symlink.
    #     eggs (iter[str]):
    #         The local paths which will be compressed into .egg (zip) files.
    #     symlink (bool):
    #         If True, create symlinks for each item in `items`.
    #         Otherwise, copy the files. This parameter's default value is
    #         set using sys.argv but typically is False.
    #
    # Raises:
    #     RuntimeError: If any item in `items` does not exist.
    #
    # """

    def _copy_file_or_folder(source, destination):
        if os.path.isdir(source):
            _LOGGER.info('Copying "%s" folder.', source)
            shutil.copytree(source, destination)
        elif os.path.isfile(source):
            _LOGGER.info('Copying "%s" file.', source)
            shutil.copy2(source, destination)

    for name in eggs:
        source_path = os.path.join(source, name)
        egg = name + ".egg"
        destination_path = os.path.join(destination, egg)

        _run_command(
            _make_egg,
            source_path,
            destination_path,
            symlink,
            symlink_folders,
            symlink_files,
        )

    print(('itemz', items))

    for item in items:
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)

        _run_command(
            _copy_file_or_folder,
            source_path,
            destination_path,
            symlink,
            symlink_folders,
            symlink_files,
        )


def _validate_egg_names(items):
    """Check to ensure no item is in a sub-folder."""
    invalids = set()

    for item in items:
        if "/" in item or "\\" in item:
            invalids.add(item)

    if invalids:
        raise exceptions.NonRootItemFound(
            'Found bad names "{invalids}".'.format(invalids=sorted(invalids))
        )


def build(
    source,
    destination,
    items=None,
    eggs=None,
    symlink=False,
    symlink_folders=False,
    symlink_files=False,
):
    # """Copy or symlink all items in `source` to `destination`.
    #
    # Args:
    #     source (str):
    #         The absolute path to the root directory of the Rez package.
    #     destination (str):
    #         The location where the built files will be copied or symlinked from.
    #     items (iter[str], optional):
    #         The local paths to every item in `source` to copy / symlink. Default is None.
    #     eggs (iter[str], optional):
    #         The local paths which will be compressed into .egg (zip) files. Default is None.
    #     symlink (bool, optional):
    #         If True, create symlinks for each item in `items`.
    #         Otherwise, copy the files. This parameter's default value is
    #         set using sys.argv but typically is False.
    #
    # """
    if not items:
        items = []

    if not eggs:
        eggs = []

    remove(destination)  # Clean any old build folder
    os.makedirs(destination)

    _validate_egg_names(eggs)

    try:
        _build(
            source,
            destination,
            items,
            eggs,
            symlink=symlink,
            symlink_folders=symlink_folders,
            symlink_files=symlink_files,
        )
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
