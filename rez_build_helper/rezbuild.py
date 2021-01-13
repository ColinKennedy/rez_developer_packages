#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Copy / symlink the rez package files."""

import os
import shutil


def build(source, destination, items):
    """Copy or symlink all items in `source` to `destination`.

    Args:
        source (str):
            The absolute path to the root directory of the Rez package.
        destination (str):
            The location where the built files will be copied or symlinked from.
        items (iter[str]):
            The local paths to every item in `source` to copy / symlink.

    """
    shutil.rmtree(destination)
    os.makedirs(destination)

    for item in items:
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)

        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        elif os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)


if __name__ == "__main__":
    build(
        os.environ["REZ_BUILD_SOURCE_PATH"],
        os.environ["REZ_BUILD_INSTALL_PATH"],
        {"fake_bin", "python"},
    )
