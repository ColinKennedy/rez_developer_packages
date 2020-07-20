#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Miscellaneous functions for making testing easier."""

import os


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
                open(item_path, "a").close()
        elif not os.path.isdir(item_path):
            os.makedirs(item_path)
