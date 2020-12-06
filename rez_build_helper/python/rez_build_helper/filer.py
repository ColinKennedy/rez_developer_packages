#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create helpful functions for building Rez packages, using Python."""

import glob
import itertools
import logging
import os
import shutil
import subprocess
import zipfile

import whichcraft

from . import exceptions, linker

_LOGGER = logging.getLogger(__name__)


def _get_hotl_executable():
    return whichcraft.which("hotl") or ""


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


def _run_command(  # pylint: disable=too-many-arguments
    command, source, destination, symlink, symlink_folders, symlink_files,
):
    """Run a commany or symlink instead, depending on the given input.

    Args:
        command (callable[str, str]):
            Some function to run if it's determined to not do a symlink.
        source (str):
            Some absolute path to a file or folder on-disk.
        destination (str):
            The absolute path to where generated content will go.
        symlink (bool):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    Raises:
        RuntimeError: If ``source`` does not exist.

    """
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


def _run_hotl(root, hda, symlink=linker.must_symlink()):
    executable = _get_hotl_executable()

    if not os.path.isfile(executable):
        raise EnvironmentError('Path "{executable}" is not an executable file.'.format(executable=executable))

    if symlink:
        _LOGGER.info('Creating symlink "%s" -> "%s".', root, hda)
        os.symlink(root, hda)

        return

    _LOGGER.info('Collapsing "%s" HDA to "%s".', root, hda)
    process = subprocess.Popen([executable, "-l", root, hda], stderr=subprocess.PIPE)
    _, stderr = process.communicate()

    if stderr:
        _LOGGER.error('HDA "%s" failed to generate.', root)

        raise RuntimeError(stderr)


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


def build(  # pylint: disable=too-many-arguments
    source,
    destination,
    hdas=None,
    items=None,
    eggs=None,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        items (iter[str], optional):
            The local paths to every item in `source` to copy / symlink. Default is None.
        eggs (iter[str], optional):
            The local paths which will be compressed into .egg (zip) files. Default is None.
        symlink (bool, optional):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool, optional):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool, optional):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """
    if not hdas:
        hdas = []

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

        if hdas:
            build_hdas(
                source,
                destination,
                hdas,
                symlink=symlink,
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


def build_eggs(  # pylint: disable=too-many-arguments
    source,
    destination,
    eggs,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        eggs (iter[str], optional):
            The local paths which will be compressed into .egg (zip) files. Default is None.
        symlink (bool, optional):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool, optional):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool, optional):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """
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


def build_hdas(
    source,
    destination,
    hdas,
    symlink=linker.must_symlink(),
):
    libraries = set()

    for folder_name in hdas:
        location = os.path.join(source, folder_name, "*", "houdini.hdalibrary")
        folder_libraries = list(glob.glob(location))

        if not folder_libraries:
            raise RuntimeError('Directory "{location}" has no VCS-style HDAs inside of it.'.format(location=location))

        libraries.update(folder_libraries)

    libraries = sorted(libraries)

    if not os.path.isdir(destination):
        os.makedirs(destination)

    for library in libraries:
        root = os.path.dirname(library)
        hda = os.path.join(destination, os.path.basename(root))

        if os.path.exists(hda):
            os.remove(hda)

        _run_hotl(root, hda, symlink=symlink)


def build_items(  # pylint: disable=too-many-arguments
    source,
    destination,
    items,
    symlink=linker.must_symlink(),
    symlink_folders=linker.must_symlink_folders(),
    symlink_files=linker.must_symlink_files(),
):
    """Copy or symlink all items in ``source`` to ``destination``.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        items (iter[str], optional):
            The local paths to every item in `source` to copy / symlink. Default is None.
        symlink (bool, optional):
            If True, symlinking will always happen. It implies
            If ``symlink_folders`` and ``symlink_files`` are both True.
            If False, symlinking is not guaranteed to always happen.
        symlink_folders (bool, optional):
            If True and ``source`` is a folder, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.
        symlink_files (bool, optional):
            If True and ``source`` is a file, make a symlink from
            ``destination`` which points back to ``source``. If False,
            run ``command`` instead.

    """

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
    """Delete and re-make the ``path`` folder."""
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
