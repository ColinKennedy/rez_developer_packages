#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create helpful functions for building Rez packages, using Python."""

import itertools
import logging
import os
import shutil
import zipfile

from . import exceptions, linker

_LOGGER = logging.getLogger(__name__)


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


def _run_command(command, source, destination, symlink, symlink_folders, symlink_files):
    if not os.path.exists(source):
        raise RuntimeError(
            'Path "{source}" does not exist. Cannot continue.'.format(source=source)
        )

    if (
        symlink
        or (symlink_folders and os.path.isdir(source))
        or (symlink_files and os.path.isfile(source))
    ):
        _LOGGER.info('Creating "%s" symlink.', destination)
        os.symlink(source, destination)
    else:
        _LOGGER.info('Running command on "%s".', destination)
        command(source, destination)


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
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
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

    try:
        if eggs:
            build_eggs(
                source,
                destination,
                eggs,
                symlink=symlink,
                symlink_folders=symlink_folders,
                symlink_files=symlink_files,
            )

        if items:
            build_items(
                source,
                destination,
                items,
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


def build_eggs(
    source,
    destination,
    eggs,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    _validate_egg_names(eggs)

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


def build_items(
    source,
    destination,
    items,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    def _copy_file_or_folder(source, destination):
        if os.path.isdir(source):
            _LOGGER.info('Copying "%s" folder.', source)
            shutil.copytree(source, destination)
        elif os.path.isfile(source):
            _LOGGER.info('Copying "%s" file.', source)
            shutil.copy2(source, destination)

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


def clean(path):
    remove(path)  # Clean any old build folder
    os.makedirs(path)


def remove(path):
    """Delete whatever `path` is.

    Args:
        path (str): A directory or file or symlink.

    """
    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
