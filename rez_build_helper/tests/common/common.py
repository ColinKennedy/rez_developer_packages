#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Miscellaneous functions for making testing easier."""

import atexit
import functools
import io
import os
import shutil
import tempfile
import unittest

from rez.config import config

from . import finder


class Common(unittest.TestCase):
    """A basic unittest class for creating a fake ``rez_build_helper`` install."""

    @classmethod
    def setUpClass(cls):
        """Copy over dependent packages so rez_build_helper resolves to the latest version.

        If a user sets their REZ_PACKAGES_PATH in their shell start-up
        scripts, it causes tests to fail. So this block of code copies
        packages into a temporary location so that they can be used in
        place of the user's packages_path, so that tests will always
        can be made to pass.

        """
        build_path = os.path.dirname(
            os.path.dirname(os.environ["REZ_REZ_BUILD_HELPER_BASE"])
        )
        directory = tempfile.mkdtemp(suffix="_test_egg_Egg_folder")
        atexit.register(functools.partial(shutil.rmtree, directory))

        for name in (
            "arch",
            "os",
            "platform",
            "python",
            "rez",
            "setuptools",
            "six",
            "whichcraft",
        ):
            package = finder.get_nearest_rez_package(
                os.environ["REZ_{name}_ROOT".format(name=name.upper())]
            )
            root = finder.get_package_root(package)
            path = os.path.dirname(root)
            destination = os.path.join(directory, os.path.relpath(root, path))

            if not os.path.isdir(destination):
                os.makedirs(destination)
                _copytree(root, destination)

        cls._packages_path = [config.local_packages_path, build_path, directory]


def _copytree(source, destination, symlinks=False, ignore=None):
    """Copy `source` into `destination`.

    Why is this not just default behavior. Guido, explain yourself!

    Reference:
        https://stackoverflow.com/a/12514470/3626104

    Args:
        source (str):
            The folder to copy from.
        destination (str):
            The folder to copy into.
        symlinks (bool, optional):
            If True, copy through symlinks. If False, copy just the
            symlink. Default is False.
        ignore (set[str], optional):
            The names of the files/folders to ignore during copy.

    """
    for item in os.listdir(source):
        source_ = os.path.join(source, item)
        destination_ = os.path.join(destination, item)

        if os.path.isdir(source_):
            shutil.copytree(source_, destination_, symlinks, ignore)
        else:
            shutil.copy2(source_, destination_)


def _make_file(path):
    """Create ``path`` on disk if it doesn't already exist.

    Args:
        path (str): An absolute path that may or may not exist on-disk.

    """
    with io.open(path, "a", encoding="utf-8"):
        pass


# Note : This was copied from :mod:`python_compatibility` to avoid a cyclic depemdendency
def make_files(file_structure, root):
    """Create a file and folder structure, starting a `root` directory.

    Args:
        file_structure (dict[str, dict[str] or None]): Every key represents a file or folder.
            If the value of that key is None, it is created as a file.
            If the key's value is an empty dict, an empty folder is
            created instead.
        root (str): The starting directory that is used to recursively build
            files and folders.

    """
    for key, items in file_structure.items():
        if items:
            make_files(items, os.path.join(root, key))

            continue

        item_path = os.path.join(root, key)
        directory = os.path.dirname(item_path)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        if items is None:
            if not os.path.isfile(item_path):
                _make_file(item_path)
        elif not os.path.isdir(item_path):
            os.makedirs(item_path)
